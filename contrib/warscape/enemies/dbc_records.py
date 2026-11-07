"""Bounded additive WotLK DBC record operations; standard-library only."""
import struct

def dbc(data,fields):
    magic,count,actual,width,length=struct.unpack_from('<4s4I',data)
    if magic!=b'WDBC' or actual!=fields or width!=fields*4 or len(data)!=20+count*width+length:raise ValueError('Unexpected DBC layout')
    rows={}
    for i in range(count):
        row=list(struct.unpack_from('<'+str(fields)+'I',data,20+i*width))
        if row[0] in rows:raise ValueError('Duplicate DBC ID')
        rows[row[0]]=row
    return rows,data[20+count*width:]
def append_spells(data,spells):
    fields=struct.unpack_from('<I',data,8)[0]
    rows,strings=dbc(data,fields);extra=b'';names=bytearray(strings)
    # Native 3.3.5a Spell.dbc layout; never alter existing rows or string offsets.
    if fields!=234:raise ValueError('Unexpected Spell.dbc field layout')
    for spell in spells:
        if spell['entry'] in rows:raise ValueError('Spell.dbc ID collision')
        row=rows[spell['source']][:];row[0]=spell['entry']
        row[37]=0;row[38]=1;row[39]=1;row[42]=0;row[43]=0;row[204]=0
        if 'range_source' in spell:row[46]=rows[spell['range_source']][46]
        if spell.get('ignore_native_hit'):row[7] |= 0x00040000 # SPELL_ATTR3_IGNORE_HIT_RESULT
        if 'keep_effects' in spell:
            if not set(spell['keep_effects']).issubset({0,1,2}):raise ValueError('Invalid spell effect selection')
            for effect in set(range(3))-set(spell['keep_effects']):
                for start in range(71,122,3):row[start+effect]=0
                row[122+3*effect:125+3*effect]=[0]*3
        if spell.get('pacify_root'):
            # Second effect: pacify with the root's same target/duration; no periodic damage.
            row[72]=6;row[87]=row[86];row[96]=25
        if spell.get('pacify_root') or spell.get('unbreakable_root'):
            row[32]=0;row[34]=0;row[35]=0;row[36]=0
            row[208:212]=[0]*4 # No inherited Druid family procs or damage-break behaviour.
        if spell.get('visual_only'):
            for start in range(71,131):row[start]=0
            row[71]=3;row[86]=1 # Dummy, caster target; no native heal/damage/aura.
        for start,text in ((136,spell['name']),(153,''),(170,spell['description']),(187,'')):
            row[start:start+16]=[0]*16
            if text:
                row[start]=len(names);names.extend(text.encode('utf-8')+b'\0')
        extra+=struct.pack('<234I',*row)
    result=struct.pack('<4s4I',b'WDBC',len(rows)+len(spells),fields,fields*4,len(names))+data[20:20+len(rows)*fields*4]+extra+names
    checked,st=dbc(result,fields)
    if not st.startswith(strings) or any(checked[k]!=v for k,v in rows.items()):raise ValueError('Existing spell data changed')
    return result
