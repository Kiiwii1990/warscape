"""Prepare additive collectible Item.dbc rows; preserve every existing record and MPQ entry."""
import argparse,json,struct,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'contrib/warscape/worldgen'),str(ROOT/'contrib/warscape/mining')]
sys.path.insert(0,str(ROOT/'addons/WarscapeHUD/tools'))
from client_assets import ClientAssets as BaseClientAssets
from deploy_sandbox import archive_entries
class ClientAssets(BaseClientAssets):
    def __init__(self,path):
        super().__init__(path)
        def priority(pair):
            path=pair[0];suffix=path.stem.rsplit('-',1)[-1].lower()
            rank=ord(suffix) if path.stem.lower().startswith('patch-') and len(suffix)==1 and suffix.isalpha() else 0
            return rank, path.parent.name.lower()=='enus' if rank else False
        self.archives.sort(key=priority,reverse=True)
def dbc(data,fields):
    magic,count,actual,width,length=struct.unpack_from('<4s4I',data)
    if magic!=b'WDBC' or actual!=fields or width!=fields*4 or len(data)!=20+count*width+length:raise ValueError('Unexpected DBC layout')
    rows={}
    for i in range(count):
        row=list(struct.unpack_from('<'+str(fields)+'I',data,20+i*width))
        if row[0] in rows:raise ValueError('Duplicate DBC ID')
        rows[row[0]]=row
    return rows,data[20+count*width:]
def merge(existing,updates,destination):
    original=archive_entries(existing); merged=dict(original)
    for name,data in updates.items():
        previous=next((k for k in merged if k.lower()==name.lower()),None)
        if previous:del merged[previous]
        merged[name]=data
    archive(destination,merged)
    checked=archive_entries(destination)
    assert all(checked[k]==v for k,v in original.items() if k.lower() not in {n.lower() for n in updates})

from generate import archive

def append(data,items):
    rows,strings=dbc(data,8); extra=b''
    for item in items:
        if item['entry'] in rows: raise ValueError('Item.dbc ID collision')
        row=rows[item['display_source']][:]; row[0]=item['entry'];row[1]=15;row[2]=0;row[6]=0;row[7]=0
        extra+=struct.pack('<8I',*row)
    result=struct.pack('<4s4I',b'WDBC',len(rows)+len(items),8,32,len(strings))+data[20:20+len(rows)*32]+extra+strings
    checked,st=dbc(result,8)
    if st!=strings or any(checked[k]!=v for k,v in rows.items()): raise ValueError('Existing DBC data changed')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--client',type=Path,required=True);p.add_argument('--server-data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--catalogue',type=Path,default=Path(__file__).with_name('goblins.json'));a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    c=json.loads(a.catalogue.read_text(encoding='utf-8'));assets=ClientAssets(a.client)
    try:
        client=assets.get(r'DBFilesClient\Item.dbc')[0];server=(a.server_data/'dbc/Item.dbc').read_bytes()
        cr,_=dbc(client,8);sr,_=dbc(server,8)
        for item in c['items']:
            if cr[item['display_source']][5]!=sr[item['display_source']][5]:raise ValueError('Source display mismatch')
        newclient=append(client,c['items']);newserver=append(server,c['items'])
        (a.output/'Item.dbc').write_bytes(newserver)
        patch=a.client/'Data/enUS/patch-enUS-Z.MPQ';target=a.output/'patch-enUS-Z.MPQ'
        if patch.exists():merge(patch,{r'DBFilesClient\Item.dbc':newclient},target)
        else:archive(target,{r'DBFilesClient\Item.dbc':newclient})
        manifest={'client':str(a.client),'server_data':str(a.server_data),'server_original_sha256':hashlib.sha256(server).hexdigest(),'client_original_sha256':hashlib.sha256(client).hexdigest(),'items':len(c['items']),'server_prepared_sha256':hashlib.sha256(newserver).hexdigest(),'patch_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
        (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(f"Prepared {len(c['items'])} additive collectible items; original DBC rows/strings preserved.")
    finally:
        for _,f in assets.archives:f.file.close()
if __name__=='__main__':main()
