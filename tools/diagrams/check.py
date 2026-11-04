#!/usr/bin/env python3
"""Check the README diagrams against tools/diagrams/KIT.md. Standard library only.

  python3 tools/diagrams/check.py                         the two templates (KIT.md stands in for the README)
  python3 tools/diagrams/check.py <repo> [<repo> ...]     docs/diagrams/*.svg of each repository, and its README
  python3 tools/diagrams/check.py --write-dark <repo>     write each X-dark.svg from X.svg first, then check
  python3 tools/diagrams/check.py --self-test             plant one fault per rule and confirm each is caught

Only the light file is drawn by hand. The dark twin is the same file with the palette line swapped.
Exit code 0 when everything passes, 1 otherwise, with one line per problem.
"""

from __future__ import annotations

import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = "{http://www.w3.org/2000/svg}"
MAX_BYTES = 150_000
MIN_TEXT_PX = 14
CANVAS_WIDTH = 1200
LIGHT = ":root{--paper:#ffffff;--ink:#10243d;--mute:#52677f;--accent:#0a6aa8;--good:#19743f;--warn:#8a5a00}"
DARK = ":root{--paper:#0d1117;--ink:#f5f4f8;--mute:#9a96ab;--accent:#6ec8ff;--good:#7ce0a1;--warn:#ffd166}"
BANNED_TAGS = {"image", "foreignObject", "script", "filter", "linearGradient", "radialGradient", "tspan", "use", "svg"}
BOXES = {"svc", "note", "win", "actor"}  # a text that starts inside one of these must end inside it


def luminance(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(one: str, two: str) -> float:
    high, low = sorted((luminance(one), luminance(two)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check_palette(palette: str, name: str) -> list[str]:
    tokens = dict(re.findall(r"--(\w+):(#[0-9a-f]{6})", palette))
    return [
        f"palette {name}: --{token} on --paper is {contrast(tokens[token], tokens['paper']):.2f}, under 4.5"
        for token in ("ink", "mute", "accent", "good", "warn")
        if contrast(tokens[token], tokens["paper"]) < 4.5
    ]


def section(source: str, tag: str) -> str:
    found = re.search(rf"<{tag}>.*?</{tag}>", source, re.S)
    return found.group(0) if found else ""


def font_sizes(style: str) -> dict[str, float]:
    return {name: float(px) for name, px in re.findall(r"\.([\w-]+)\{[^}]*?font-size:([\d.]+)px", style)}


def text_box(element: ET.Element, sizes: dict[str, float]) -> tuple[float, float, float, float, float]:
    """x0, y0, x1, y1 and the font size. Mono glyphs are 0.6 of the size wide; the serif title about 0.5."""
    classes = element.get("class", "").split()
    size = float(element.get("font-size", 0)) or max((sizes.get(name, 0) for name in classes), default=0)
    width = len(element.text or "") * size * (0.5 if "title" in classes else 0.6)
    x, y = float(element.get("x", 0)), float(element.get("y", 0))
    anchor = element.get("text-anchor", "start")
    x0 = x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x
    return x0, y - size * 0.8, x0 + width, y + size * 0.2, size


def check_svg(path: Path, template_style: str, template_defs: str) -> list[str]:
    problems: list[str] = []
    source = path.read_text(encoding="utf-8")
    if len(source.encode()) >= MAX_BYTES:
        problems.append(f"{len(source.encode())} bytes, limit {MAX_BYTES}")
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        return [f"not well-formed: {error}"]
    box = (root.get("viewBox") or "").split()
    if root.tag != f"{NS}svg" or len(box) != 4 or box[:3] != ["0", "0", str(CANVAS_WIDTH)]:
        return [f"viewBox must be 0 0 {CANVAS_WIDTH} H, found {root.get('viewBox')}"]
    height = float(box[3])
    if root.get("width") != str(CANVAS_WIDTH) or root.get("height") != box[3]:
        problems.append("width and height attributes must match the viewBox")
    if root.get("role") != "img":
        problems.append('root needs role="img"')
    for tag in ("title", "desc"):
        element = root.find(f"{NS}{tag}")
        if element is None or not (element.text or "").strip():
            problems.append(f"missing <{tag}>")
    if section(source, "style") != template_style:
        problems.append("<style> differs from the template's: copy it unchanged")
    if section(source, "defs") != template_defs:
        problems.append("<defs> differs from the template's: copy it unchanged")
    body = source.replace(section(source, "style"), "")
    if re.search(r"#[0-9a-fA-F]{3,8}\b(?!\))", re.sub(r'url\(#[\w-]+\)|href="#[\w-]+"', "", body)):
        problems.append("a hex color outside the palette: use the classes")
    if re.search(r"https?://(?!www\.w3\.org/2000/svg)|url\((?!#)|@import|\shref=\"(?!#)", source):
        problems.append("an external reference")

    sizes = font_sizes(template_style)
    texts: list[tuple[tuple[float, float, float, float, float], str]] = []
    boxes: list[tuple[float, float, float, float]] = []
    for element in root.iter():
        tag = element.tag.replace(NS, "")
        if tag in BANNED_TAGS and element is not root:
            problems.append(f"<{tag}> is not allowed")
        if element.get("transform") or element.get("style"):
            problems.append(f"<{tag}> carries transform or style: use coordinates and classes")
        if tag == "rect" and BOXES & set(element.get("class", "").split()):
            x, y = float(element.get("x", 0)), float(element.get("y", 0))
            boxes.append((x, y, x + float(element.get("width", 0)), y + float(element.get("height", 0))))
        if tag == "text":
            label = (element.text or "").strip()
            bounds = text_box(element, sizes)
            if not label:
                problems.append("an empty <text>")
            if bounds[4] < MIN_TEXT_PX:
                problems.append(f'"{label}": {bounds[4]:g} px, floor {MIN_TEXT_PX} (does it have a size class?)')
            if bounds[0] < 0 or bounds[2] > CANVAS_WIDTH or bounds[1] < 0 or bounds[3] > height:
                problems.append(f'"{label}" runs off the canvas')
            texts.append((bounds, label))
    for index, (one, label) in enumerate(texts):
        for other, other_label in texts[index + 1 :]:
            if one[0] < other[2] and other[0] < one[2] and one[1] < other[3] and other[1] < one[3]:
                problems.append(f'"{label}" overlaps "{other_label}"')
        for x0, y0, x1, y1 in boxes:
            if x0 <= one[0] <= x1 and y0 <= one[1] <= y1 and (one[2] > x1 or one[3] > y1):
                problems.append(f'"{label}" spills out of its box (ends at x={one[2]:.0f}, box ends at {x1:g})')
    return problems


def check_readme(repo: Path, names: list[str]) -> list[str]:
    problems: list[str] = []
    readme = (repo / "README.md").read_text(encoding="utf-8")
    for name in names:
        light, dark = f"docs/diagrams/{name}.svg", f"docs/diagrams/{name}-dark.svg"
        if not re.search(rf'<source media="\(prefers-color-scheme: dark\)" srcset="{dark}">', readme):
            problems.append(f"README has no dark <source> for {dark}")
        if not re.search(rf'<img alt="[^"]{{20,}}" src="{light}"', readme):
            problems.append(f"README has no <img> with meaningful alt text for {light}")
    headings = re.findall(r"^## .+$", readme, re.M)
    if headings[:2] != ["## Architecture", "## How one run flows"]:
        problems.append("the first two README sections must be Architecture and How one run flows")
    architecture = (repo / "ARCHITECTURE.md").read_text(encoding="utf-8")
    if "docs/diagrams/architecture.svg" not in architecture or "docs/diagrams/flow.svg" not in architecture:
        problems.append("ARCHITECTURE.md has no line pointing at the drawn figures")
    return problems


def self_test() -> int:
    """Each planted fault must produce a problem; the clean template must produce none."""
    template = (HERE / "template-flow.svg").read_text(encoding="utf-8")
    style, defs = section(template, "style"), section(template, "defs")
    faults = {
        "viewBox": template.replace('viewBox="0 0 1200', 'viewBox="0 0 1000'),
        "floor": template.replace('class="legend"', 'font-size="12"', 1),
        "image": template.replace("</svg>", '<image href="#x"/></svg>'),
        "external": template.replace("</svg>", '<a href="https://example.com"/></svg>'),
        "hex": template.replace('class="dot"', 'fill="#ff0000" class="dot"', 1),
        "style": template.replace("font-size:36px", "font-size:30px"),
        "overlap": template.replace('x="96" y="232"', 'x="96" y="212"', 1),
        "off canvas": template.replace('x="1004"', 'x="1190"'),
        "spill": template.replace('>the line the run prints at the end<', f'>{"x" * 60}<'),
        "size": template.replace("</svg>", f"<!-- {'x' * MAX_BYTES} --></svg>"),
    }
    folder = Path(tempfile.mkdtemp())
    clean = folder / "clean.svg"
    clean.write_text(template, encoding="utf-8")
    assert check_svg(clean, style, defs) == [], check_svg(clean, style, defs)
    for name, source in faults.items():
        path = folder / "fault.svg"
        path.write_text(source, encoding="utf-8")
        assert check_svg(path, style, defs), f"not caught: {name}"
    assert contrast("#ffffff", "#000000") == 21
    print(f"self-test passed: {len(faults)} planted faults caught")
    return 0


def main(arguments: list[str]) -> int:
    if "--self-test" in arguments:
        return self_test()
    write_dark = "--write-dark" in arguments
    repos = [Path(argument) for argument in arguments if argument != "--write-dark"]
    template = (HERE / "template-architecture.svg").read_text(encoding="utf-8")
    style, defs = section(template, "style"), section(template, "defs")
    failures = check_palette(LIGHT, "light") + check_palette(DARK, "dark")
    if LIGHT not in style:
        failures.append("template: the palette line differs from LIGHT in check.py")
    targets = [(None, HERE / "template-architecture.svg"), (None, HERE / "template-flow.svg")]
    if repos:
        targets = []
    for repo in repos:
        folder = repo / "docs" / "diagrams"
        names = [name for name in ("architecture", "flow") if (folder / f"{name}.svg").exists()]
        if names != ["architecture", "flow"]:
            failures.append(f"{repo}: docs/diagrams needs architecture.svg and flow.svg")
        targets += [(repo, folder / f"{name}.svg") for name in names]
        if write_dark:
            for name in names:
                light = (folder / f"{name}.svg").read_text(encoding="utf-8")
                (folder / f"{name}-dark.svg").write_text(light.replace(LIGHT, DARK), encoding="utf-8")
        failures += [f"{repo}: {problem}" for problem in check_readme(repo, names)]
    for repo, path in targets:
        failures += [f"{path}: {problem}" for problem in check_svg(path, style, defs)]
        if repo is not None:
            twin = path.with_name(f"{path.stem}-dark.svg")
            light = path.read_text(encoding="utf-8")
            if not twin.exists() or twin.read_text(encoding="utf-8") != light.replace(LIGHT, DARK):
                failures.append(f"{twin}: missing or out of step; run check.py --write-dark {repo}")
    for failure in failures:
        print(failure)
    print(f"{len(targets)} drawings checked, {len(failures)} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
