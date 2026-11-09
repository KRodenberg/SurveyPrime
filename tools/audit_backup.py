"""Compare two private Prime backup snapshots without displaying user data."""
import json
from pathlib import Path
import sys

old_dir,new_dir=map(Path,sys.argv[1:3])
old=json.loads((old_dir/'index.json').read_text())
new=json.loads((new_dir/'index.json').read_text())
lookup={(item['type'],item['name']):item for item in new}
same=0
programs=0
changed_types=[]
for item in old:
    match=lookup.get((item['type'],item['name']))
    if match is None:
        raise RuntimeError('An original calculator object is missing')
    old_bytes=(old_dir/('%05d.bin'%item['record'])).read_bytes()
    new_bytes=(new_dir/('%05d.bin'%match['record'])).read_bytes()
    if old_bytes==new_bytes:
        same+=1
        programs+=item['type']==6
    else:
        changed_types.append(item['type'])
print('Byte-identical original records:',same,'/',len(old))
print('Byte-identical original programs:',programs)
print('Changed record types:',changed_types)
