"""ORIVANE - The Poster for a Place That Isn't There (make.fun entry).

Copies the poster image entry.png from this repository to the output
directory required by the competition.
"""
import os
import shutil
import struct
import sys
from pathlib import Path

MAX_BYTES = 1_048_576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def read_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) for a PNG or JPEG file, stdlib-only."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 1:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + length
    raise ValueError(f"unsupported image format: {path}")


def validate(source: Path) -> None:
    """Check the poster meets the competition limits before copying."""
    size = source.stat().st_size
    if size == 0:
        raise SystemExit("entry.png is empty")
    if size > MAX_BYTES:
        raise SystemExit(f"entry.png too large: {size} bytes > {MAX_BYTES}")
    width, height = read_dimensions(source)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise SystemExit(f"entry.png must be 1024x1024, got {width}x{height}")


def main() -> None:
    repo = Path(__file__).resolve().parent
    source = repo / "entry.png"
    if not source.is_file():
        raise SystemExit("entry.png missing from repository")
    validate(source)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(source, dest)
    if dest.stat().st_size != source.stat().st_size:
        raise SystemExit("round-trip check failed: output size differs")
    if dest.read_bytes() != source.read_bytes():
        raise SystemExit("round-trip check failed: output bytes differ")
    print(f"wrote entry.png ({source.stat().st_size} bytes, 1024x1024)")


if __name__ == "__main__":
    main()
