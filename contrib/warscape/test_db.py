"""Offline safety tests: never connect to a database or execute real SQL."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import db


NAME = '2026_10_25_01_world.sql'
MIGRATION = db.ROOT / 'sql/updates/world/3.3.5' / NAME


class SafetyTests(unittest.TestCase):
    def test_hash_matches_windows_text_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'test.sql'
            file.write_bytes(b'SELECT 1;\r\n')
            first = db.migration_hash(file)
            file.write_bytes(b'SELECT 1;\n')
            self.assertEqual(first, db.migration_hash(file))

    def fake_inventory(self, status='pending'):
        return {NAME: dict(path=MIGRATION, hash=db.migration_hash(MIGRATION),
                           state='RELEASED', status=status)}

    def test_unapproved_apply_never_backs_up_or_executes(self):
        with patch.object(sys, 'argv', ['db.py', 'apply', '--migration', NAME]), \
             patch.object(db, 'Database') as client, \
             patch.object(db, 'inventory', return_value=self.fake_inventory()), \
             patch.object(db, 'backup') as backup:
            with self.assertRaisesRegex(db.SafeError, 'approval'):
                db.main()
            backup.assert_not_called()
            client.return_value.execute.assert_not_called()

    def test_duplicate_and_conflicting_apply_refused(self):
        for status in ['applied', 'hash-conflict', 'renamed-or-duplicate']:
            with self.subTest(status=status), \
                 patch.object(sys, 'argv', ['db.py', 'apply', '--migration', NAME,
                                           '--approved', '--servers-stopped']), \
                 patch.object(db, 'Database') as client, \
                 patch.object(db, 'inventory', return_value=self.fake_inventory(status)), \
                 patch.object(db, 'backup') as backup:
                with self.assertRaises(db.SafeError):
                    db.main()
                backup.assert_not_called()
                client.return_value.execute.assert_not_called()

    def test_failed_preconditions_refuse_mutation(self):
        with patch.object(sys, 'argv', ['db.py', 'apply', '--migration', NAME,
                                       '--approved', '--servers-stopped']), \
             patch.object(db, 'Database') as client, \
             patch.object(db, 'inventory', return_value=self.fake_inventory()), \
             patch.object(db, 'backup') as backup:
            client.return_value.query.return_value = '0'
            with self.assertRaisesRegex(db.SafeError, 'Preconditions'):
                db.main()
            backup.assert_not_called()
            client.return_value.execute.assert_not_called()

    def test_backup_precedes_sql_and_ledger_follows_verification(self):
        events = []
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(sys, 'argv', ['db.py', 'apply', '--migration', NAME,
                                       '--approved', '--servers-stopped', '--backup-dir', folder]), \
             patch.object(db, 'Database') as client, \
             patch.object(db, 'inventory', side_effect=[self.fake_inventory(), self.fake_inventory(), self.fake_inventory('applied')]), \
             patch.object(db, 'permissions', return_value=True), \
             patch.object(db, 'backup', side_effect=lambda *args: events.append('backup')), \
             contextlib.redirect_stdout(io.StringIO()):
            client.return_value.kind = 'world'
            client.return_value.query.side_effect = lambda sql: events.append('check') or '1'
            client.return_value.execute.side_effect = lambda sql: events.append('ledger' if sql.startswith('INSERT INTO updates') else 'migration')
            db.main()
            self.assertEqual(events, ['check', 'backup', 'check', 'migration', 'check', 'ledger'])
            self.assertFalse((Path(folder) / 'world.migration.lock').exists())

    def test_failed_migration_retains_lock(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(sys, 'argv', ['db.py', 'apply', '--migration', NAME,
                                       '--approved', '--servers-stopped', '--backup-dir', folder]), \
             patch.object(db, 'Database') as client, \
             patch.object(db, 'inventory', return_value=self.fake_inventory()), \
             patch.object(db, 'permissions', return_value=True), \
             patch.object(db, 'backup'):
            client.return_value.kind = 'world'
            client.return_value.query.return_value = '1'
            client.return_value.execute.side_effect = db.SafeError('simulated SQL failure')
            with self.assertRaises(db.SafeError):
                db.main()
            self.assertTrue((Path(folder) / 'world.migration.lock').exists())

    def test_backup_completion_and_nontransactional_guard(self):
        class Fake:
            kind = 'world'
            name = 'test'

            def query(self, sql):
                if 'DISTINCT engine' in sql:
                    return self.engine
                if "table_type='BASE TABLE'" in sql:
                    return '1'
                if "table_type='VIEW'" in sql:
                    return '1'
                return '0'

            def run(self, program, extra, output, timeout):
                output.write(self.export)

        fake = Fake()
        fake.engine = 'MyISAM'
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(db.SafeError, 'InnoDB'):
                db.backup(fake, Path(folder))
            fake.engine = 'InnoDB'
            fake.export = b'CREATE TABLE `test` (id int);\n'
            with self.assertRaisesRegex(db.SafeError, 'verification'):
                db.backup(fake, Path(folder))
            fake.export += b'INSERT INTO `test` VALUES (1);\n/*!50001 VIEW `sample_view` AS SELECT 1 */;\n-- Dump completed on test\n'
            first = db.backup(fake, Path(folder))
            second = db.backup(fake, Path(folder))
            self.assertNotEqual(first, second)
            manifest = json.loads(first.with_suffix('.sql.json').read_text())
            self.assertEqual(manifest['tables'], 1)
            self.assertEqual(manifest['insert_statements'], 1)
            self.assertEqual(manifest['views'], 1)

    def test_errors_never_include_raw_client_messages(self):
        client = object.__new__(db.Database)
        client.bin = Path('unused')
        client.connection = []
        client.env = {}
        with patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, b'', b'ERROR 1045 (28000) secret-password SQL server-data')):
            with self.assertRaises(db.SafeError) as error:
                client.run('mariadb.exe', [])
            self.assertEqual(str(error.exception), 'Database operation failed: ERROR 1045 (28000)')


if __name__ == '__main__':
    unittest.main()
