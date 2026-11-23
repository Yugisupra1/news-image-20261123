"""Front page for Monday 23 November 2026 (Python 3.13, stdlib only).

The finished page ships beside this file as entry.png, and this program
places an exact copy of it at /output/entry.png. The run is offline,
deterministic, and makes no random choices.

What the page shows, all first reported on 23 November 2026: Ukrainian
sea drones sink the Russian corvette Merkury at the Benghazi naval base;
the COP31 climate talks collapse without an agreement after record
overtime; a Russian drone hits a flat block north of Kyiv, leaving 11
missing; the BepiColombo probe enters orbit around Mercury after an
eight-year journey; and Okinawa's restored Shuri Castle opens again.

The drawing itself lives in a build script outside this repository;
what runs here is only the delivery of the finished image.

Run it anywhere with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"

LIMIT_BYTES = 1_048_576
LIMIT_SIDE = 1024

HEADLINES = (
    ("LIBYA", "Sea drones sink Russian warship at Benghazi"),
    ("COP31", "Climate talks collapse without a deal"),
    ("KYIV", "Drone hits flats, 11 missing"),
    ("MERCURY", "BepiColombo reaches Mercury"),
    ("OKINAWA", "Shuri Castle rises again"),
)


def _describe():
    """One line per story, so the run log names the day's news."""
    return "\n".join(f"  - {place}: {head}" for place, head in HEADLINES)


def _jpeg_size(data):
    """Read width and height from a JPEG's SOF marker."""
    pos = 2
    while pos < len(data) - 9:
        if data[pos] != 0xFF:
            pos += 1
            continue
        marker = data[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        pos += 2 + length
    raise ValueError("no SOF marker found")


def _fingerprint(data):
    """Short hash of the shipped bytes, for the run log."""
    return hashlib.sha256(data).hexdigest()[:16]


def _report(source, dest):
    """Check the shipped image against the gate, then copy it."""
    data = source.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ValueError("entry.png is not JPEG bytes")
    if len(data) > LIMIT_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the limit")
    width, height = _jpeg_size(data)
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        raise ValueError(f"entry.png is {width}x{height}, over the limit")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    print(f"copied {len(data)} bytes, {width}x{height}, "
          f"sha256={_fingerprint(data)}, to {dest}")
    print(_describe())


def main():
    _report(SOURCE, DEST)


if __name__ == "__main__":
    main()
