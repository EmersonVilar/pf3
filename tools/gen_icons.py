"""Regenerate pf3/icons_data.py from nvim-web-devicons (MIT, nvim-tree).

Usage: python tools/gen_icons.py
Downloads the two Lua tables, maps each icon's hex color to the nearest ANSI
color name by hue, and writes name -> (codepoint, color).
"""
import colorsys
import re
import urllib.request
from pathlib import Path

BASE = (
    "https://raw.githubusercontent.com/nvim-tree/nvim-web-devicons/master/"
    "lua/nvim-web-devicons/default/"
)
OUT = Path(__file__).resolve().parent.parent / "pf3" / "icons_data.py"
LINE = re.compile(
    r'\s*\["([^"]+)"\]\s*=\s*\{\s*icon\s*=\s*"([^"]*)",\s*color\s*=\s*"#([0-9A-Fa-f]{6})"'
)


def ansi(hexc: str) -> str:
    r, g, b = (int(hexc[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s < 0.22 or v < 0.2:
        return ""
    d = h * 360
    if d < 20 or d >= 340:
        return "red"
    if d < 70:
        return "yellow"
    if d < 165:
        return "green"
    if d < 200:
        return "cyan"
    if d < 260:
        return "blue"
    return "magenta"


def fetch(name: str) -> dict[str, tuple[int, str]]:
    text = urllib.request.urlopen(BASE + name).read().decode("utf-8")
    out = {}
    for line in text.splitlines():
        m = LINE.match(line)
        if m and m.group(2):
            out[m.group(1)] = (ord(m.group(2)[0]), ansi(m.group(3)))
    return out


def fmt(d: dict[str, tuple[int, str]]) -> str:
    return "\n".join(f"    {k!r}: ({cp:#x}, {c!r})," for k, (cp, c) in sorted(d.items()))


def main() -> None:
    ext = fetch("icons_by_file_extension.lua")
    name = fetch("icons_by_filename.lua")
    OUT.write_text(
        '"""Generated from nvim-web-devicons (MIT, nvim-tree). '
        'key -> (codepoint, ansi color from hue of original hex)."""\n\n'
        f"EXTENSION_ICONS = {{\n{fmt(ext)}\n}}\n\n"
        f"FILENAME_ICONS = {{\n{fmt(name)}\n}}\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {len(ext)} extensions, {len(name)} filenames")


if __name__ == "__main__":
    main()
