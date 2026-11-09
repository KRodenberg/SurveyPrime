"""Reproducibly build a named native HP Prime program and readable source."""
from pathlib import Path
import hashlib
import json
import re
import struct
import shutil

ROOT = Path(__file__).resolve().parents[1]

def source(files=None):
    files = files or ['core.ppl','geometry.ppl','geodesy.ppl','keypad.ppl','missing_ui.ppl',
                      'priority_ui.ppl','extended_ui.ppl','selftest.ppl','main.ppl']
    bodies = [(ROOT/'src'/name).read_text(encoding='utf-8') for name in files]
    # Exported variables must be visible before any function that uses them.
    declaration = re.compile(r'(?m)^EXPORT SC_\w+\s*:=[^\n]*;[ \t]*$')
    globals_ = [line for body in bodies for line in declaration.findall(body)]
    bodies = [declaration.sub('',body) for body in bodies]
    # PPL requires declarations for functions referenced before their definitions.
    # Native declarations use empty parameter lists, as in HP's supplied examples.
    names = []
    for body in bodies:
        names.extend(re.findall(r'(?m)^(?!EXPORT\b)(SC_\w+)\([^\n]*\)\s*\nBEGIN',body))
    return ('#pragma mode( separator(.,;) integer(h32) )\n'+'\n'.join(globals_)+'\n'
            +'\n'.join(n+'();' for n in names)+'\n\n'+'\n'.join(bodies))

def encode(name, text):
    namebytes = (name+'\0').encode('utf-16le')
    body = (text+'\0').encode('utf-16le')
    return (struct.pack('<IIIIH',18+len(namebytes)-4,0,1,0,0x31)
            +namebytes+struct.pack('<I',len(body))+body)

def decode(data):
    assert struct.unpack_from('<I',data,8)[0] == 1
    pos = 18
    while data[pos:pos+2] != b'\0\0': pos += 2
    name = data[18:pos].decode('utf-16le')
    size = struct.unpack_from('<I',data,pos+2)[0]
    text = data[pos+6:pos+6+size].decode('utf-16le').removesuffix('\0')
    assert pos+6+size == len(data)
    return name,text

def build():
    dest = ROOT/'Final Output'
    dest.mkdir(exist_ok=True)
    text = source()
    native = encode('SURVEYPRIME',text)
    assert decode(native) == ('SURVEYPRIME',text)
    (dest/'SURVEYPRIME.hpprgm').write_bytes(native)
    (dest/'SURVEYPRIME.ppl').write_text(text,encoding='utf-8',newline='\n')
    for doc in (ROOT/'docs'/'release').glob('*.md'):
        shutil.copyfile(doc,dest/doc.name)
    manifest = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(dest.iterdir()) if p.is_file() and p.name!='SHA256.json'}
    (dest/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(text.splitlines())} lines, {len(native)} native bytes')

if __name__ == '__main__': build()
