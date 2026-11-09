"""Keyboard and screenshot harness for the official Windows HP emulator only."""
import argparse
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import struct
import time

u, g = c.WinDLL("user32"), c.WinDLL("gdi32")
u.GetWindowTextW.argtypes = [w.HWND, w.LPWSTR, c.c_int]
u.PostMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
u.GetWindowDC.argtypes = [w.HWND]
u.GetWindowDC.restype = w.HDC
g.CreateCompatibleDC.argtypes = [w.HDC]
g.CreateCompatibleDC.restype = w.HDC
g.CreateCompatibleBitmap.argtypes = [w.HDC, c.c_int, c.c_int]
g.CreateCompatibleBitmap.restype = w.HBITMAP
g.SelectObject.argtypes = [w.HDC, w.HGDIOBJ]
g.SelectObject.restype = w.HGDIOBJ
u.PrintWindow.argtypes = [w.HWND, w.HDC, w.UINT]
g.GetDIBits.argtypes = [w.HDC, w.HBITMAP, w.UINT, w.UINT, c.c_void_p, c.c_void_p, w.UINT]
g.DeleteObject.argtypes = [w.HGDIOBJ]
g.DeleteDC.argtypes = [w.HDC]
u.ReleaseDC.argtypes = [w.HWND, w.HDC]

def windows():
    result = []
    @c.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    def callback(hwnd, param):
        text = c.create_unicode_buffer(512)
        u.GetWindowTextW(hwnd, text, 512)
        if text.value == "HPPrime" or text.value.startswith("HP Prime"):
            result.append((hwnd, text.value))
        return True
    u.EnumWindows(callback, 0)
    return result

def screenshot(hwnd, filename):
    rect = w.RECT()
    u.GetWindowRect(hwnd, c.byref(rect))
    width, height = rect.right - rect.left, rect.bottom - rect.top
    dc = u.GetWindowDC(hwnd)
    mem = g.CreateCompatibleDC(dc)
    bmp = g.CreateCompatibleBitmap(dc, width, height)
    old = g.SelectObject(mem, bmp)
    u.PrintWindow(hwnd, mem, 2)
    header = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0,
                         width * height * 4, 0, 0, 0, 0)
    info = c.create_string_buffer(header)
    data = c.create_string_buffer(width * height * 4)
    g.GetDIBits(mem, bmp, 0, height, data, info, 0)
    dest = Path(filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(struct.pack("<2sIHHI", b"BM", 54 + len(data), 0, 0, 54) + header + data.raw)
    g.SelectObject(mem, old)
    g.DeleteObject(bmp)
    g.DeleteDC(mem)
    u.ReleaseDC(hwnd, dc)

def keys(hwnd, codes):
    for key in codes:
        if key.startswith("text:"):
            for char in key[5:]:
                u.PostMessageW(hwnd, 0x102, ord(char), 1)
        else:
            code = int(key, 0)
            u.PostMessageW(hwnd, 0x100, code, 1)
            time.sleep(0.04)
            u.PostMessageW(hwnd, 0x101, code, 0xC0000001)
        time.sleep(0.1)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["list", "screen", "keys"])
    p.add_argument("args", nargs="*")
    args = p.parse_args()
    found = windows()
    if args.action == "list":
        print(found)
    else:
        if len(found) != 1:
            raise RuntimeError(f"Expected exactly one emulator window: {found}")
        hwnd = found[0][0]
        if args.action == "screen":
            screenshot(hwnd, args.args[0])
        elif args.action == "keys":
            keys(hwnd, args.args)
