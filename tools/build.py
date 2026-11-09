"""Build the HP Prime program bundle and readable source.

Native container skeleton and blank-app descriptor from
hp-prime-kit/templates/code.hpprgm and templates/app/blank.hpapp:
https://github.com/JordiRigau/hp-prime-kit (MIT License)
Copyright (c) 2026 Jordi Rigau

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from pathlib import Path
import base64
import binascii
import hashlib
import json
import re
import struct
import zlib
from ppl_runner import Parser, TOKEN

ROOT = Path(__file__).resolve().parents[1]

def order_functions(text):
    """Place helpers before callers, avoiding fragile native prototypes."""
    matches = list(re.finditer(r'(?m)^(?:EXPORT )?([A-Za-z_]\w*)\([^;\n]*\)\s*\nBEGIN',text))
    if not matches: return text
    functions,_ = Parser(portable_locals(text)).program()
    chunks = {m[1]:text[m.start():matches[ii+1].start() if ii+1<len(matches) else len(text)]
              for ii,m in enumerate(matches)}
    def calls(node):
        if not isinstance(node,(tuple,list)): return
        if len(node)==3 and node[0]=='call' and node[1][0]=='name':
            yield node[1][1]
        for child in node:
            if isinstance(child,(tuple,list)): yield from calls(child)
    done,active,ordered = set(),set(),[]
    def visit(name):
        if name in done: return
        if name in active: raise ValueError('Cyclic native function dependency: '+name)
        active.add(name)
        for target in calls(functions[name][1]):
            if target in chunks: visit(target)
        active.remove(name); done.add(name); ordered.append(chunks[name])
    for name in chunks: visit(name)
    return text[:matches[0].start()]+''.join(ordered)

def portable_locals(text):
    """Declare a group before evaluating its ordered initializers.

    The target firmware cannot resolve a sibling local in the same LOCAL
    statement, e.g. LOCAL row:=JOIN(...),distance:=row(2).
    """
    tokens = [m for m in TOKEN.finditer(text)
              if not m.group().isspace() and not m.group().startswith('//')]
    changes = []
    for index, token in enumerate(tokens):
        if token.group() != 'LOCAL': continue
        depth, start, groups = 0, index+1, []
        for at in range(start,len(tokens)):
            value = tokens[at].group()
            if value in ('(', '[', '{'): depth += 1
            elif value in (')', ']', '}'): depth -= 1
            elif depth == 0 and value in (',', ';'):
                groups.append(tokens[start:at])
                start = at+1
                if value == ';': break
        names = [group[0].group() for group in groups]
        initializers = []
        for name, group in zip(names,groups):
            if len(group)>1:
                if group[1].group() != ':=': raise SyntaxError('Invalid LOCAL initializer')
                initializers.append(name+':='+text[group[2].start():group[-1].end()]+';')
        if initializers:
            indent = re.match(r'[ \t]*',text[text.rfind('\n',0,token.start())+1:]).group()
            replacement = ('\n'+indent).join(['LOCAL '+','.join(names)+';']+initializers)
            changes.append((token.start(),tokens[at].end(),replacement))
    for start,end,value in reversed(changes): text = text[:start]+value+text[end:]
    return text

def source(files=None, export_helpers=False):
    if files is None:
        return '\n'.join(native_sources().values())
    bodies = [(ROOT/'src'/name).read_text(encoding='utf-8') for name in files]
    # Exported variables must be visible before any function that uses them.
    declaration = re.compile(r'(?m)^EXPORT SC_\w+\s*:=[^\n]*;[ \t]*$')
    globals_ = [line for body in bodies for line in declaration.findall(body)]
    bodies = [declaration.sub('',body) for body in bodies]
    if export_helpers:
        bodies = [re.sub(r'(?m)^(SC_\w+\()',r'EXPORT \1',body) for body in bodies]
    text = ('#pragma mode( separator(.,;) integer(h32) )\n'+'\n'.join(globals_)+'\n'
            +'\n'.join(bodies))
    text = order_functions(text)
    text = portable_locals(text)
    # This is a structural guard for known native constraints, not HP's compiler.
    Parser(text).program()
    return text

def native_sources():
    text = source(['core.ppl','geometry.ppl','geodesy.ppl','keypad.ppl',
                   'geodesy_ui.ppl','missing_ui.ppl','priority_ui.ppl',
                   'extended_ui.ppl','selftest.ppl','main.ppl'],True)
    matches = list(re.finditer(r'(?m)^EXPORT ([A-Za-z_]\w*)\([^;\n]*\)\s*\nBEGIN',text))
    current = text[:matches[0].start()]
    groups = []
    for ii,match in enumerate(matches):
        function = text[match.start():matches[ii+1].start() if ii+1<len(matches) else len(text)]
        if len(current)+len(function)>29900:
            groups.append(current)
            current = '#pragma mode( separator(.,;) integer(h32) )\n'
        current += function
    groups.append(current)
    names = (['SURVEYPRIME'] if len(groups)==1 else
             ['SURVEYLIB']+['SURVEYTOOLS'+str(ii) for ii in range(1,len(groups)-1)]+['SURVEYPRIME'])
    programs = dict(zip(names,groups))
    for name in names[:-1]:
        programs[name] += '\nEXPORT '+name+'()\nBEGIN\n  RETURN 1;\nEND;\n'
    for name,text in programs.items():
        if len(text)>30000:
            raise ValueError(name+' exceeds the conservative native source-size budget')
        Parser(text).program()
    return programs

# A generic source-only CK container, with its placeholder source removed.
# It carries Main and default settings, with no calculator/user data.
SKELETON = zlib.decompress(base64.b64decode(
    'eNqrSeza9O////8MQMABxKz/6xkQbHsmBHs/WPwbUGQfgwPjOyDtAuR3Mzgw+DIkMmQy5DGQC0DmtzI0gNnTgObOZjjA8IaZgaGPyYEpgQFqD5MDA6VABIjbmBoY/qOBUTtG7Ri1Y2DtAADSls3W'))

# Base App: None. Always rebuild from the clean descriptor, rather than a
# calculator-saved copy that may carry the user's last view or settings.
APP_NAME = 'SurveyPrime'
APP_DESCRIPTOR = bytes.fromhex(
    '7c618ab2ffffffff010001000800000085ff7f00140000000800000085ffbf0001000000'
    '0800000085ffff00000000000800000085ff3f01000000000800000085ff7f0104000000'
    '0800000085ffbf01000000000c00000085ffff010000000020000000140000001e060905'
    '0c000000080000000506490000000000')

def app_source():
    text = (ROOT/'src/app.ppl').read_text(encoding='utf-8')
    Parser(text).program()
    return text

def app_icon():
    """Draw an original survey-boundary symbol as the native 73x74 RGBA PNG."""
    width,height = 73,74
    background = (22,47,66,255)
    pixels = bytearray(background*(width*height))
    def dot(x,y,r,color):
        for yy in range(max(0,y-r),min(height,y+r+1)):
            for xx in range(max(0,x-r),min(width,x+r+1)):
                if (xx-x)**2+(yy-y)**2<=r*r:
                    offset=4*(yy*width+xx)
                    pixels[offset:offset+4]=bytes(color)
    def line(a,b,color,r=1):
        dx,dy=b[0]-a[0],b[1]-a[1]
        steps=max(abs(dx),abs(dy),1)
        for ii in range(steps+1):
            dot(round(a[0]+dx*ii/steps),round(a[1]+dy*ii/steps),r,color)
    grid=(45,75,91,255)
    for x in (12,24,36,48,60): line((x,8),(x,66),grid,0)
    for y in (14,26,38,50,62): line((7,y),(66,y),grid,0)
    boundary=(245,249,250,255)
    accent=(88,218,195,255)
    points=((15,53),(21,24),(45,18),(58,43),(42,59))
    for ii,point in enumerate(points):
        line(point,points[(ii+1)%len(points)],boundary,1)
        dot(*point,3,accent)
    line((50,26),(50,8),accent,1)
    line((50,8),(46,14),accent,1)
    line((50,8),(54,14),accent,1)
    def chunk(tag,data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',binascii.crc32(tag+data)&0xffffffff)
    rows=b''.join(b'\0'+pixels[y*width*4:(y+1)*width*4] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))
            +chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b''))

def app_files():
    """The four files required for a native Apps-library application."""
    return {APP_NAME+'.hpapp':APP_DESCRIPTOR,
            APP_NAME+'.hpappnote':b'\0\0',
            APP_NAME+'.hpappprgm':encode(app_source()),
            'icon.png':app_icon()}

def encode(text):
    body = (text+'\0').encode('utf-16le')
    data = bytearray(SKELETON[:152]+body+SKELETON[152:])
    for offset,base in ((48,100),(56,92),(144,4)):
        struct.pack_into('<I',data,offset,len(body)+base)
    return bytes(data)

def decode(data):
    """Decode a source-only package made by this builder."""
    assert data[:4] == b'\x7c\x61\x8a\xb2'
    size = struct.unpack_from('<I',data,144)[0]-4
    assert size>=2 and size%2==0 and len(data)==len(SKELETON)+size
    body = data[152:152+size]
    assert body[-2:] == b'\0\0'
    text = body[:-2].decode('utf-16le')
    assert encode(text)==data
    return text

def build():
    dest = ROOT/'Final Output'
    dest.mkdir(exist_ok=True)
    (dest/'Programs').mkdir(exist_ok=True)
    (dest/'Source').mkdir(exist_ok=True)
    artifacts = []
    for name,text in native_sources().items():
        native = encode(text)
        assert decode(native) == text
        (dest/'Programs'/(name+'.hpprgm')).write_bytes(native)
        (dest/'Source'/(name+'.ppl')).write_text(text,encoding='utf-8',newline='\n')
        artifacts.extend(['Programs/'+name+'.hpprgm','Source/'+name+'.ppl'])
        print(f'Built {name}: {len(text)} characters, {len(native)} native bytes')
    app_relative = 'Application/'+APP_NAME+'.hpappdir/'
    (dest/app_relative).mkdir(parents=True,exist_ok=True)
    for name,data in app_files().items():
        relative = app_relative+name
        (dest/relative).write_bytes(data)
        artifacts.append(relative)
    (dest/'Source'/(APP_NAME+'.app.ppl')).write_text(app_source(),encoding='utf-8',newline='\n')
    artifacts.append('Source/'+APP_NAME+'.app.ppl')
    print('Built native app: '+app_relative)
    # Only generated build files belong in the manifest. Local notes or older
    # documentation in the output directory are not build inputs or artifacts.
    manifest = {name:hashlib.sha256((dest/name).read_bytes()).hexdigest()
                for name in artifacts}
    (dest/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__': build()
