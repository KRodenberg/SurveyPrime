"""Small HP Prime HID diagnostic/transfer tool. Never erases calculator data.

Protocol references: libhpcalcs and 56phil/prime_connection_kit (see docs/SOURCES.md).
Optional host dependency: hidapi. `work/deps` is used only for local diagnostics.
"""
from __future__ import annotations

import argparse
import binascii
import json
from pathlib import Path
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work" / "deps"))


class PrimeLink:
    def __init__(self):
        import hid
        devices = [d for d in hid.enumerate(0x03F0, 0)
                   if d["product_id"] in (0x0441, 0x1541, 0x2441)]
        if len(devices) != 1:
            raise RuntimeError(f"Expected one HP Prime, found {len(devices)}")
        self.info = devices[0]
        self.capacity = 1023 if self.info["product_id"] == 0x2441 else 63
        self.dev = hid.device()
        self.dev.open_path(self.info["path"])

    def close(self):
        self.dev.close()

    def drain(self):
        while self.dev.read(self.capacity + 1, 10):
            pass

    def send(self, message):
        for seq, offset in enumerate(range(0, len(message) + 1, self.capacity)):
            chunk = message[offset:offset + self.capacity]
            self.dev.write(bytes([0, seq % 255]) + chunk)

    def receive(self, timeout=8):
        out = bytearray()
        seq = 0
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            report = bytes(self.dev.read(self.capacity + 1, 200))
            if not report or report[0] == 255:
                continue
            if report[0] != seq % 255:
                raise RuntimeError(f"Packet sequence {report[0]}, expected {seq % 255}")
            seq += 1
            out.extend(report[1:])
            if out and out[0] in (0x59, 0xFF):
                return bytes(out[:1])
            if len(out) >= 6 and out[1] == 1:
                size = 6 + int.from_bytes(out[2:6], "big")
                if size > 128 * 1024 * 1024:
                    raise RuntimeError("Implausible reply length")
                if len(out) >= size:
                    return bytes(out[:size])
            if len(report) < self.capacity + 1:
                return bytes(out)
        raise TimeoutError(f"No complete calculator reply ({len(out)} bytes received)")

    def exchange(self, message, timeout=8):
        self.drain()
        self.send(message)
        return self.receive(timeout)

    def screen(self, path):
        reply = self.exchange(b"\xfc\x08")
        start = reply.find(b"\x89PNG\r\n\x1a\n")
        if start < 0:
            raise RuntimeError(f"Screenshot is not PNG: {reply[:30].hex()}")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(reply[start:])
        return str(path)

    def keys(self, values):
        body = bytes(values)
        self.drain()
        self.send(b"\xec\x01" + len(body).to_bytes(4, "big") + body)
        time.sleep(0.15)

    def file_message(self, command, name, content=b"", kind=6):
        encoded = name.encode("utf-16le")
        body = bytes([kind, len(encoded), 0, 0]) + encoded + content
        message = bytearray(bytes([command, 1]) + len(body).to_bytes(4, "big") + body)
        crc = binascii.crc_hqx(message[:-6], 0)
        message[8:10] = struct.pack("<H", crc)
        return bytes(message)

    def get_program(self, name):
        return self.exchange(self.file_message(0xF8, name))

    def backup(self, directory):
        dest = Path(directory)
        dest.mkdir(parents=True, exist_ok=True)
        self.drain()
        self.send(b'\xf9')
        objects = []
        records = []
        for index in range(20000):
            reply = self.receive(timeout=15)
            # The calculator streams without flow control. Avoid disk/antivirus
            # stalls while reading; a HID input queue can otherwise overflow.
            records.append(reply)
            if reply and reply[0] == 0xf9:
                for number, record in enumerate(records):
                    (dest / f'{number:05d}.bin').write_bytes(record)
                (dest / 'index.json').write_text(json.dumps(objects,indent=2),encoding='utf-8')
                return objects
            if len(reply) < 10 or reply[0] != 0xf7:
                raise RuntimeError(f'Invalid backup record: {reply[:20].hex()}')
            covered = bytearray(reply[:-6])
            covered[8:10] = b'\0\0'
            if binascii.crc_hqx(covered,0) != int.from_bytes(reply[8:10],'little'):
                raise RuntimeError('Backup checksum mismatch')
            name = reply[10:10+reply[7]].decode('utf-16le').rstrip('\0')
            objects.append({'record':index,'type':reply[6],'name':name,'bytes':len(reply)})
        raise RuntimeError('Backup exceeded object limit')

    def put_program(self, name, source):
        self.drain()
        self.send(self.file_message(0xF7, name, source.encode("utf-16le")))
        time.sleep(0.5)
        return self.exchange(b"\xff")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["info", "screen", "keys", "get", "put", "backup"])
    p.add_argument("args", nargs="*")
    args = p.parse_args()
    link = PrimeLink()
    try:
        if args.action == "info":
            desc = {k: v for k, v in link.info.items() if k != "path"}
            print(json.dumps(desc, indent=2))
            print("Ready:", link.exchange(b"\xff").hex())
            reply = link.exchange(b"\xfa")
            (ROOT / "work" / "device-info.bin").write_bytes(reply)
            print("Info:", reply.hex())
        elif args.action == "screen":
            print(link.screen(args.args[0]))
        elif args.action == "keys":
            link.keys([int(x) for x in args.args])
        elif args.action == "get":
            Path(args.args[1]).write_bytes(link.get_program(args.args[0]))
        elif args.action == "put":
            print("Ready after transfer:", link.put_program(
                args.args[0], Path(args.args[1]).read_text(encoding="utf-8")).hex())
        elif args.action == 'backup':
            objects = link.backup(args.args[0])
            print('Backed up',len(objects),'objects')
            print('Programs:',[o['name'] for o in objects if o['type']==6])
    finally:
        link.close()


if __name__ == "__main__":
    main()
