"""Extract embedded cabinets from an MSI without installing software."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import subprocess
import sys

msi = c.WinDLL("msi")
msi.MsiOpenDatabaseW.argtypes = [w.LPCWSTR, w.LPCWSTR, c.POINTER(w.UINT)]
msi.MsiDatabaseOpenViewW.argtypes = [w.UINT, w.LPCWSTR, c.POINTER(w.UINT)]
msi.MsiViewExecute.argtypes = [w.UINT, w.UINT]
msi.MsiViewFetch.argtypes = [w.UINT, c.POINTER(w.UINT)]
msi.MsiRecordGetStringW.argtypes = [w.UINT, w.UINT, w.LPWSTR, c.POINTER(w.DWORD)]
msi.MsiRecordReadStream.argtypes = [w.UINT, w.UINT, c.c_void_p, c.POINTER(w.DWORD)]

def check(value):
    if value:
        raise OSError(value, "MSI read failed")

db = w.UINT()
check(msi.MsiOpenDatabaseW(str(Path(sys.argv[1]).resolve()), None, c.byref(db)))
view = w.UINT()
check(msi.MsiDatabaseOpenViewW(db, "SELECT `Name`, `Data` FROM `_Streams`", c.byref(view)))
check(msi.MsiViewExecute(view, 0))
dest = Path(sys.argv[2]).resolve()
dest.mkdir(parents=True, exist_ok=True)
while True:
    record = w.UINT()
    if msi.MsiViewFetch(view, c.byref(record)) == 259:
        break
    name = c.create_unicode_buffer(1024)
    size = w.DWORD(1024)
    check(msi.MsiRecordGetStringW(record, 1, name, c.byref(size)))
    if name.value.lower().endswith(".cab"):
        data = bytearray()
        while True:
            buf = c.create_string_buffer(65536)
            count = w.DWORD(65536)
            check(msi.MsiRecordReadStream(record, 2, buf, c.byref(count)))
            data.extend(buf.raw[:count.value])
            if count.value == 0:
                break
        path = dest / Path(name.value).name
        path.write_bytes(data)
        if not (dest / 'HPPrime.exe').exists():
            check(subprocess.run(["expand.exe", str(path), "-F:*", str(dest)],
                                 capture_output=True).returncode)
        print("Extracted", name.value)
    msi.MsiCloseHandle(record)
msi.MsiCloseHandle(view)

def rows(sql, columns):
    view = w.UINT()
    check(msi.MsiDatabaseOpenViewW(db, sql, c.byref(view)))
    check(msi.MsiViewExecute(view, 0))
    result = []
    while True:
        record = w.UINT()
        if msi.MsiViewFetch(view, c.byref(record)) == 259: break
        row = []
        for column in range(1,columns+1):
            buf = c.create_unicode_buffer(4096)
            size = w.DWORD(4096)
            check(msi.MsiRecordGetStringW(record,column,buf,c.byref(size)))
            row.append(buf.value)
        result.append(row)
        msi.MsiCloseHandle(record)
    msi.MsiCloseHandle(view)
    return result

directories = {r[0]: r[1:] for r in rows('SELECT `Directory`, `Directory_Parent`, `DefaultDir` FROM `Directory`',3)}
components = dict(rows('SELECT `Component`, `Directory_` FROM `Component`',2))
print('Directories:',directories)
for key, component, filename in rows('SELECT `File`, `Component_`, `FileName` FROM `File`',3):
    filename = filename.split('|')[-1]
    directory = components[component]
    parts = []
    while directory in directories:
        parent, label = directories[directory]
        label = label.split(':')[0].split('|')[-1]
        if label not in ('.','SourceDir'):
            parts.insert(0,label)
        directory = parent
    original = dest / key
    if not original.exists(): original = dest / filename
    if original.exists():
        target = dest.joinpath('layout',*parts,filename)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(original.read_bytes())
msi.MsiCloseHandle(db)
