"""Stage a collision-checked Item.dbc addition and preserved client MPQ merge."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'contrib/warscape/worldgen'), str(ROOT/'contrib/warscape/mining')]
from build_pickaxe_assets import ClientAssets, dbc, merge, CLIENT, SERVER
ENTRY, BASE = 900500, 2841

def append(data):
    rows, strings = dbc(data, 8)
    if ENTRY in rows:
        raise ValueError('Bronze Bar ID collision')
    row = rows[BASE][:]
    row[0] = ENTRY
    assert row[5] == 7390
    count = len(rows)
    result = struct.pack('<4s4I', b'WDBC', count+1, 8, 32, len(strings))
    result += data[20:20+count*32] + struct.pack('<8I', *row) + strings
    checked, checked_strings = dbc(result, 8)
    assert all(checked[k] == v for k,v in rows.items()) and checked_strings == strings
    return result

def build(output):
    output.mkdir(parents=True, exist_ok=False)
    assets = ClientAssets(CLIENT)
    try:
        source = assets.get(r'DBFilesClient\Item.dbc')[0]
        server = (SERVER/'dbc/Item.dbc').read_bytes()
        client_data, server_data = append(source), append(server)
        (output/'client-Item.dbc').write_bytes(client_data)
        (output/'server-Item.dbc').write_bytes(server_data)
        # Existing standard Bronze Bar display and icon: no new model or texture.
        displays, strings = dbc(assets.get(r'DBFilesClient\ItemDisplayInfo.dbc')[0], 25)
        offset = displays[7390][5]
        icon = strings[offset:].split(b'\0')[0].decode('ascii')
        assets.get('Interface\\Icons\\'+icon+'.blp')
        info = merge(CLIENT/'Data/enUS/patch-enUS-Z.MPQ',
                     {r'DBFilesClient\Item.dbc':client_data},output/'patch-enUS-Z.MPQ')
        manifest = {'entry':ENTRY,'base':BASE,'display':7390,'icon':icon,
                    'server_source_sha256':hashlib.sha256(server).hexdigest(),
                    'client_source_sha256':hashlib.sha256(source).hexdigest(), 'merge':info}
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print('PASS: client/server Item.dbc addition; original rows, strings and unrelated MPQ payloads preserved')
    finally:
        for _, opened in assets.archives: opened.file.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    build(parser.parse_args().output)
