"""Exercise replacement staging in a temporary client/server, never the live one."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import deploy_briarbrook as deployer
from deploy_sandbox import archive_entries
from generate import archive


class RefinementDeploymentTests(unittest.TestCase):
    def fixture(self,root):
        client=root/'client';server=root/'server';output=root/'new';baseline=root/'approved'
        for p in [client/'Data/enUS',server/'maps',server/'vmaps',server/'mmaps',server/'dbc',
                  output/'runtime',output/'extracted/maps',baseline]:p.mkdir(parents=True,exist_ok=True)
        old_terrain=b'approved terrain';new_terrain=b'refined terrain';dbc=b'unchanged map registration'
        adt='World\\Maps\\WarscapeBriarbrook\\WarscapeBriarbrook_32_32.adt'
        wdt='World\\Maps\\WarscapeBriarbrook\\WarscapeBriarbrook.wdt'
        unrelated='World\\Maps\\WarscapeDevSandbox\\WarscapeDevSandbox.wdt'
        archive(client/'Data/patch-Z.MPQ',{adt:b'approved adt',wdt:b'wdt',unrelated:b'preserve map 904'})
        locale={'DBFilesClient\\Map.dbc':dbc,'DBFilesClient\\Light.dbc':b'unchanged native lighting'}
        archive(client/'Data/enUS/patch-enUS-Z.MPQ',locale)
        archive(output/'runtime/patch-Z.MPQ',{adt:b'refined adt',wdt:b'wdt'})
        archive(output/'runtime/patch-enUS-Z.MPQ',locale)
        (output/'runtime/Map.dbc').write_bytes(dbc);(server/'dbc/Map.dbc').write_bytes(dbc)
        (server/'maps/9053232.map').write_bytes(old_terrain);(server/'maps/9043232.map').write_bytes(b'preserve flat sandbox')
        (output/'extracted/maps/9053232.map').write_bytes(new_terrain)
        (baseline/'manifest.json').write_text('{}')
        (baseline/'build-validation.json').write_text(json.dumps({'files':{'maps/9053232.map':hashlib.sha256(old_terrain).hexdigest()}}))
        (output/'build-validation.json').write_text(json.dumps(dict(terrain_tiles=1,nav_tiles=1,
            files={'maps/9053232.map':hashlib.sha256(new_terrain).hexdigest()})))
        (output/'artifact-validation.json').write_text(json.dumps(dict(road_navigation_issues=[],
            interior_entrances=[{'entrance_connected':True}]*7,cellar_and_stair_probes=[True]*4,
            refinement={'all_material_resources_resolved':True})))
        manifest=dict(configuration=dict(map_id=905,directory='WarscapeBriarbrook',tiles=[[32,32]]),
            base_server_map_sha256=hashlib.sha256(dbc).hexdigest(),refinement=dict(baseline=str(baseline),
                baseline_source_hash=deployer.digest(baseline/'manifest.json'),baseline_adt_sha256=hashlib.sha256(b'approved adt').hexdigest()))
        (output/'manifest.json').write_text(json.dumps(manifest))
        return client,server,output,unrelated

    def test_replacement_stage_preserves_other_maps_and_never_selects_dbc_targets(self):
        with tempfile.TemporaryDirectory() as d:
            client,server,output,unrelated=self.fixture(Path(d))
            with patch.object(deployer,'CLIENT',client),patch.object(deployer,'SERVER',server):
                pairs,kept,before=deployer.prepare(output,replace_existing=True)
            self.assertEqual(kept,1)
            self.assertEqual(len(pairs),2)
            self.assertFalse(any(target.suffix.lower()=='.dbc' or 'enUS' in target.parts for _,target in pairs))
            self.assertEqual(archive_entries(output/'deploy-prepared/patch-Z.MPQ')[unrelated],b'preserve map 904')
            self.assertEqual((server/'maps/9053232.map').read_bytes(),b'approved terrain','Preparation must be read-only on deployed files')

    def test_replacement_refuses_an_unexpected_deployed_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            client,server,output,unrelated=self.fixture(Path(d))
            (server/'maps/9053232.map').write_bytes(b'another editor changed this')
            with patch.object(deployer,'CLIENT',client),patch.object(deployer,'SERVER',server):
                with self.assertRaisesRegex(ValueError,'baseline artifact changed'):
                    deployer.prepare(output,replace_existing=True)


if __name__=='__main__':unittest.main()
