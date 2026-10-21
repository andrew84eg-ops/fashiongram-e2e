"""Test data: throwaway members, generated photos, and the app's known seed data."""

import struct
import uuid
import zlib
from dataclasses import dataclass, field
from pathlib import Path

# Test-only password for accounts that live in the app's local, throwaway database.
TEST_PASSWORD = "Test-pass-123"


@dataclass(frozen=True)
class Member:
    email: str
    password: str = TEST_PASSWORD
    name: str = "QA Member"


def new_member(name: str = "QA Member") -> Member:
    """A unique member per call, so tests never share state."""
    return Member(email=f"qa.{uuid.uuid4().hex[:12]}@example.test", name=name)


def unique_title(prefix: str) -> str:
    return f"{prefix} {uuid.uuid4().hex[:6]}"


@dataclass(frozen=True)
class Piece:
    title: str
    category: str
    color: str


# Every new member is given this 8-piece starter closet by the app
# (STARTER_CLOSET in src/lib/fashion.ts). Tests derive their expectations from it.
STARTER_CLOSET: tuple[Piece, ...] = (
    Piece("Ivory Silk Blouse", "top", "ivory"),
    Piece("Black Turtleneck", "top", "black"),
    Piece("Cream Cashmere", "top", "cream"),
    Piece("Black Trousers", "bottom", "black"),
    Piece("Light Straight Jean", "bottom", "navy"),
    Piece("Black Slip Dress", "dress", "black"),
    Piece("Black Blazer", "outerwear", "black"),
    Piece("Court Sneaker", "shoes", "white"),
)

CATEGORY_LABELS = {
    "top": "Tops",
    "bottom": "Bottoms",
    "dress": "Dresses",
    "outerwear": "Outerwear",
    "shoes": "Shoes",
    "bag": "Bags",
    "accessory": "Accessories",
}


def starter_titles(category: str | None = None, color: str | None = None) -> set[str]:
    return {
        p.title
        for p in STARTER_CLOSET
        if (category is None or p.category == category) and (color is None or p.color == color)
    }


def make_photo(path: Path, rgb: tuple[int, int, int] = (200, 120, 90), size: int = 64) -> Path:
    """Write a solid-colour PNG using only the standard library."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    row = b"\x00" + bytes(rgb) * size
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(row * size))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)
    return path
