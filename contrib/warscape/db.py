#!/usr/bin/env python3
"""Warscape database tooling. Never log configuration, SQL output, or raw errors."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
KEYS = {'world': 'WorldDatabaseInfo', 'auth': 'LoginDatabaseInfo',
        'characters': 'CharacterDatabaseInfo'}


class SafeError(Exception):
    pass


def literal(value):
    return "CONVERT(0x" + value.encode().hex() + " USING utf8mb4)"


def migration_hash(file):
    # TrinityCore's Windows text-mode ifstream translates CRLF to LF.
    return hashlib.sha1(file.read_text(encoding='utf-8').encode('utf-8')).hexdigest().upper()


class Database:
    def __init__(self, args):
        self.kind = args.database
        text = args.config.read_text(encoding='utf-8-sig')
        matches = re.findall(r'^\s*' + KEYS[self.kind] + r'\s*=\s*"([^"\r\n]*)"', text, re.M)
        if len(matches) != 1:
            raise SafeError('Expected exactly one database configuration entry.')
        fields = matches[0].split(';')
        if len(fields) != 5 or not fields[1].isdigit():
            raise SafeError('Unsupported connection format; TCP configuration required.')
        self.host, self.port, self.user, password, self.name = fields
        self.env = dict(os.environ, MYSQL_PWD=password)
        self.bin = args.client_dir
        self.connection = ['--no-defaults', '--protocol=TCP', '--connect-timeout=10',
                           '--host=' + self.host, '--port=' + self.port,
                           '--user=' + self.user, '--default-character-set=utf8mb4']

    def run(self, program, extra, sql=None, output=subprocess.PIPE, timeout=60):
        try:
            connection = [x for x in self.connection if program != 'mariadb-dump.exe' or not x.startswith('--connect-timeout=')]
            result = subprocess.run([str(self.bin / program), *connection, *extra],
                                    input=sql.encode() if sql is not None else None,
                                    stdout=output, stderr=subprocess.PIPE,
                                    env=self.env, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            raise SafeError('Database client unavailable or timed out; details suppressed.') from None
        if result.returncode:
            code = re.search(rb'ERROR\s+\d+(?:\s+\([A-Z0-9]+\))?', result.stderr)
            raise SafeError('Database operation failed: ' +
                            (code[0].decode() if code else 'client error (details suppressed)'))
        return result.stdout.decode('utf-8') if output == subprocess.PIPE else None

    def query(self, sql):
        return self.run('mariadb.exe', ['--batch', '--raw', '--skip-column-names',
                                      '--database=' + self.name],
                        'SET SESSION TRANSACTION READ ONLY; START TRANSACTION READ ONLY;\n' +
                        sql + ';\nROLLBACK;').strip()

    def execute(self, sql):
        return self.run('mariadb.exe', ['--batch', '--skip-column-names',
                                      '--database=' + self.name], sql, timeout=3600)


def inventory(db):
    applied = {}
    archived = set()
    for row in db.query('SELECT name, hash, state FROM updates').splitlines():
        name, digest, state = row.split('\t')
        applied[name] = digest.upper()
        if state == 'ARCHIVED':
            archived.add(name)
    available = {}
    for row in db.query('SELECT path, state FROM updates_include').splitlines():
        directory, state = row.split('\t')
        path = ROOT / directory[2:] if directory.startswith('$/') else Path(directory)
        if not path.is_absolute() or not path.is_relative_to(ROOT):
            raise SafeError('Updater include directory outside repository; inspect manually.')
        if not path.is_dir():
            raise SafeError('An updater include directory is missing.')
        for file in sorted(path.rglob('*.sql')):
            if file.name in available:
                raise SafeError('Duplicate migration filenames found.')
            digest = migration_hash(file)
            status = ('archived' if state == 'ARCHIVED' and file.name in archived else
                      ('applied' if applied[file.name] == digest else 'hash-conflict')) if file.name in applied else (
                'renamed-or-duplicate' if digest in applied.values() else 'pending')
            available[file.name] = dict(path=file, hash=digest, state=state, status=status)
    # Custom files must still be visible when the server updater does not include them.
    for file in sorted((ROOT / 'sql/custom' / db.kind).glob('*.sql')):
        if file.name not in available:
            digest = migration_hash(file)
            status = ('applied' if applied[file.name] == digest else 'hash-conflict') if file.name in applied else (
                'renamed-or-duplicate' if digest in applied.values() else 'pending')
            available[file.name] = dict(path=file, hash=digest, state='RELEASED', status=status)
    return available


def permissions(db):
    # SHOW GRANTS may contain authentication material: inspect only in memory.
    grants = db.query('SHOW GRANTS FOR CURRENT_USER')
    effective = set()
    scope = '`' + db.name.replace('`', '``') + '`.*'
    for line in grants.splitlines():
        match = re.match(r'GRANT (.+?) ON (.+?) TO ', line)
        if match and match[2] in ('*.*', scope):
            effective.update(match[1].split(', '))
    all_privileges = 'ALL PRIVILEGES' in effective
    required = ['SELECT', 'SHOW VIEW', 'TRIGGER', 'EVENT', 'LOCK TABLES',
                'CREATE', 'ALTER', 'DROP', 'INDEX', 'INSERT', 'UPDATE', 'DELETE']
    results = {p: all_privileges or p in effective for p in required}
    # Flush with a global read lock is used by --lock-all-tables.
    results['RELOAD (global)'] = any(re.match(r'GRANT (ALL PRIVILEGES|.*\bRELOAD\b.*) ON \*\.\* TO ', x)
                                           for x in grants.splitlines())
    # Actual read probe for stored routine backup visibility (no routine bodies printed).
    try:
        db.query('SELECT COUNT(*) FROM mysql.proc')
        results['routine metadata readable'] = True
    except SafeError:
        results['routine metadata readable'] = False
    print(json.dumps({'database': db.kind, 'permission_checks': results}, indent=2))
    # Global read locks and mysql.proc are not required for an InnoDB-only
    # snapshot without routines. Backup independently enforces these conditions.
    return all(results[p] for p in required)


def secure_backup_directory(directory):
    directory.mkdir(parents=True, exist_ok=True)
    if os.name == 'nt':
        script = r'''
$ErrorActionPreference = 'Stop'
$acl = New-Object System.Security.AccessControl.DirectorySecurity
$acl.SetAccessRuleProtection($true, $false)
$owner = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
foreach ($sid in @($owner.Value, 'S-1-5-18', 'S-1-5-32-544')) {
    $identity = New-Object System.Security.Principal.SecurityIdentifier($sid)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
    $acl.AddAccessRule($rule)
}
[System.IO.Directory]::SetAccessControl($env:WARSCAPE_BACKUP_DIRECTORY, $acl)
'''
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                                env=dict(os.environ, WARSCAPE_BACKUP_DIRECTORY=str(directory)),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise SafeError('Cannot restrict backup directory permissions; export refused.')
    else:
        directory.chmod(0o700)


def backup(db, directory):
    directory = directory.resolve()
    if directory.is_relative_to(ROOT):
        raise SafeError('Backups must be outside the repository.')
    secure_backup_directory(directory)
    engines = db.query("SELECT DISTINCT engine FROM information_schema.tables WHERE table_schema=DATABASE() AND table_type='BASE TABLE'").splitlines()
    if engines != ['InnoDB']:
        raise SafeError('Consistent snapshot requires exclusively InnoDB tables; arrange privileged locked backup separately.')
    routines = int(db.query('SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema=DATABASE()'))
    views = int(db.query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_type='VIEW'"))
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    final = directory / f'{db.kind}_{stamp}_{uuid.uuid4().hex[:8]}.sql'
    partial = final.with_suffix('.sql.partial')
    # Exclusive creation plus rename (Windows refuses replacement) prevents overwrites.
    with partial.open('xb') as stream:
        db.run('mariadb-dump.exe', ['--single-transaction', '--skip-lock-tables', '--quick',
               *(['--routines'] if routines else []),
               '--events', '--triggers', '--hex-blob', '--comments',
               '--databases', db.name], output=stream, timeout=3600)
        stream.flush()
        os.fsync(stream.fileno())
    digest = hashlib.sha256()
    create_count = insert_count = view_count = 0
    tail = b''
    with partial.open('rb') as stream:
        for line in stream:
            digest.update(line)
            create_count += line.startswith(b'CREATE TABLE ')
            insert_count += line.startswith(b'INSERT INTO ')
            # MariaDB versioned comments split CREATE/ALGORITHM/VIEW across lines.
            view_count += bool(re.search(rb'CREATE ALGORITHM=.*?VIEW |/\*!\d+ VIEW\s+`', line))
            tail = (tail + line)[-2048:]
    expected = int(db.query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_type='BASE TABLE'"))
    if create_count != expected or view_count != views or not create_count or b'-- Dump completed on ' not in tail:
        raise SafeError('Backup verification failed; partial export retained outside repository.')
    if final.exists():
        raise SafeError('Backup destination already exists.')
    partial.rename(final)
    manifest = {'file': final.name, 'database': db.kind, 'sha256': digest.hexdigest(),
                'bytes': final.stat().st_size, 'tables': create_count,
                'views': view_count, 'insert_statements': insert_count, 'completed': True,
                'consistency': 'single-transaction (InnoDB only; no concurrent DDL)',
                'routines': routines, 'restore_tested': False}
    with final.with_suffix('.sql.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2)
    print(json.dumps({'backup': str(final), **manifest}, indent=2))
    return final


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'permissions', 'backup', 'verify', 'apply'])
    parser.add_argument('--database', choices=KEYS, default='world')
    parser.add_argument('--config', type=Path, default=ROOT / 'worldserver.conf')
    parser.add_argument('--client-dir', type=Path, default=Path(r'C:\Program Files\MariaDB 11.7\bin'))
    parser.add_argument('--backup-dir', type=Path, default=Path(r'C:\WoWDev\Backups'))
    parser.add_argument('--migration', help='Exact migration filename; required for verify/apply')
    parser.add_argument('--approved', action='store_true', help='Use only after explicit user approval')
    parser.add_argument('--servers-stopped', action='store_true', help='Confirm server and other updaters are stopped')
    args = parser.parse_args()
    db = Database(args)
    if args.command == 'permissions':
        if not permissions(db):
            raise SafeError('Some permissions are unverified or missing; no privileges changed.')
    elif args.command == 'backup':
        backup(db, args.backup_dir)
    else:
        files = inventory(db)
        if args.command == 'status':
            counts = {}
            for name, item in sorted(files.items()):
                counts[item['status']] = counts.get(item['status'], 0) + 1
                if item['status'] not in ('applied', 'archived'):
                    print(f"{item['status']}: {item['path'].relative_to(ROOT).as_posix()}")
            print(json.dumps({'database': db.kind, 'summary': counts}))
            return
        if args.migration not in files:
            raise SafeError('Select an existing migration by exact filename.')
        item = files[args.migration]
        spec_path = ROOT / 'contrib/warscape/verifications' / (Path(args.migration).stem + '.json')
        if not spec_path.is_file():
            raise SafeError('Migration requires a reviewed verification specification.')
        spec = json.loads(spec_path.read_text(encoding='utf-8'))
        if spec['sha1'].upper() != item['hash']:
            raise SafeError('Verification specification does not match migration contents.')
        if args.command == 'verify':
            if db.query(spec['verify_sql']) != '1':
                raise SafeError('Expected schema/data checks failed.')
            print('Expected schema/data checks passed; migration history unchanged.')
            return
        if not args.approved or not args.servers_stopped:
            raise SafeError('Apply requires explicit user approval and stopped servers/updaters.')
        if item['status'] != 'pending':
            raise SafeError('Migration is applied, duplicated, or has a hash conflict; refusing execution.')
        if any(x['status'] in ('hash-conflict', 'renamed-or-duplicate') for x in files.values()):
            raise SafeError('Resolve migration history conflicts before applying.')
        earlier = [n for n, x in files.items() if n < args.migration and x['status'] == 'pending']
        if earlier:
            raise SafeError('Earlier migrations are pending; review and apply in order.')
        if db.query(spec['precondition_sql']) != '1':
            raise SafeError('Preconditions failed: schema may be partially or manually applied.')
        if not permissions(db):
            raise SafeError('Required permissions not verified.')
        # Same-host exclusion; stopped servers and other writers are mandatory.
        lock_file = args.backup_dir / (db.kind + '.migration.lock')
        args.backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SafeError('Migration lock exists; inspect previous run before removing it.') from None
        os.close(fd)
        success = False
        try:
            backup(db, args.backup_dir)
            if inventory(db)[args.migration]['status'] != 'pending':
                raise SafeError('Migration status changed during backup.')
            if db.query(spec['precondition_sql']) != '1':
                raise SafeError('Preconditions changed during backup.')
            sql = item['path'].read_text(encoding='utf-8')
            if migration_hash(item['path']) != item['hash']:
                raise SafeError('Migration changed during backup.')
            # Keep the lock after ANY failure: MariaDB DDL can commit partially.
            db.execute(sql)
            if db.query(spec['verify_sql']) != '1':
                raise SafeError('Post-migration verification failed; lock retained for recovery.')
            db.execute('INSERT INTO updates (name, hash, state, speed) VALUES (' +
                       ','.join([literal(args.migration), literal(item['hash']),
                                 literal(item['state']), '0']) + ');')
            if inventory(db)[args.migration]['status'] != 'applied':
                raise SafeError('Migration ledger verification failed; lock retained for recovery.')
            success = True
            print('Migration verified and recorded in TrinityCore updates history.')
        finally:
            if success:
                lock_file.unlink()


if __name__ == '__main__':
    try:
        main()
    except (SafeError, OSError, ValueError, KeyError):
        # Never emit tracebacks, credentials, raw server messages or result rows.
        error = sys.exc_info()[1]
        print(str(error) if isinstance(error, SafeError) else 'Local configuration or file operation failed; details suppressed.', file=sys.stderr)
        sys.exit(1)
