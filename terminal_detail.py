"""Self-contained SVG details for the terminal cards. Coordinates are local to each panel."""
from functools import lru_cache
from html import escape
from pathlib import Path


@lru_cache(maxsize=1)
def fate_lettering():
    return (Path(__file__).parent / "chaldeas" / "fate-title.txt").read_text(encoding="ascii").splitlines()


def ascii_lines(rows, advance, leading, size):
    lines = []
    for i, row in enumerate(rows):
        indent = len(row) - len(row.lstrip())
        ink = row[indent:]
        if ink:
            lines.append(
                f'<text x="{indent*advance:g}" y="{(i+1)*leading:g}" '
                f'style="font-family:monospace;white-space:pre" textLength="{len(ink)*advance:g}" '
                f'lengthAdjust="spacingAndGlyphs">{escape(ink)}</text>'
            )
    return (f'<g xml:space="preserve" font-family="monospace" style="font-family:monospace" '
            f'font-weight="bold" font-size="{size:g}">' + "".join(lines) + "</g>")


def fate_background(p):
    dark = p["name"] == "dark"
    base, highlight = ("#9a8158", "#e0c58e") if dark else ("#9c8467", "#80673f")
    lines = ascii_lines(fate_lettering(), 1.59, 2.42, 2.65)
    return (
        '<defs><linearGradient id="fate-metal" x1="0" x2="1" y1="0" y2=".16">'
        f'<stop stop-color="{highlight}"/><stop offset=".5" stop-color="{base}"/>'
        f'<stop offset="1" stop-color="{highlight}"/></linearGradient></defs>'
        '<g aria-hidden="true" transform="translate(641 52) scale(.83)" class="fate-sigil" '
        'fill="url(#fate-metal)">' + lines + '</g>'
    )


ANVIL = (
    "             ______________________",
    "            /_____________________/|",
    "   ________/#####################| |",
    "   \\======+=====================|_/",
    "    '::----.___#############__.-'",
    "               \\#########/",
    "                |#######|",
    "               /#########\\",
    "           __.'###########'.__",
    "          /___________________/|",
    "          |___________________|/",
)
HAMMER = (
    "  _______",
    " /______/|",
    " |######|/==+==========o",
    " '------'",
)


def forge_background(p):
    base = "#829eae" if p["name"] == "dark" else "#536d79"
    hot = "#e5ac66" if p["name"] == "dark" else "#a4622f"
    anvil = ascii_lines(ANVIL, 4.3, 5.8, 6.9)
    hammer = ascii_lines(HAMMER, 4.2, 5.7, 6.9)
    return (
        '<g aria-hidden="true" transform="translate(686 47) scale(.89)">'
        f'<g fill="{base}" opacity=".72" transform="translate(0 55)">{anvil}</g>'
        '<g transform="translate(43 34)"><g class="forge-stroke">'
        f'<g fill="{base}" opacity=".87">{hammer}</g></g></g>'
        f'<g class="forge-sparks" fill="{hot}" font-family="monospace" font-size="12">'
        '<text x="40" y="53">/</text><text x="66" y="46">·</text>'
        '<text x="81" y="55">\\</text></g></g>'
    )


FORGE_CSS = """
.forge-stroke{transform-origin:94px 17px;transform:rotate(10deg)}
.forge-sparks{opacity:0}
@media(prefers-reduced-motion:no-preference){
.forge-stroke{animation:strike 5.8s ease-in-out infinite}
.forge-sparks{animation:swarf 5.8s linear infinite}
}
@keyframes strike{0%,47%,75%,100%{transform:rotate(10deg)}57%{transform:rotate(23deg)}61%{transform:rotate(-4deg)}65%{transform:rotate(5deg)}69%{transform:rotate(1deg)}}
@keyframes swarf{0%,60%,69%,100%{opacity:0;transform:translateY(0)}61%{opacity:.78}68%{opacity:0;transform:translateY(-6px)}}
"""
FATE_CSS = """
.fate-sigil{opacity:.74}
@media(prefers-reduced-motion:no-preference){.fate-sigil{animation:crest-ink 7.6s linear infinite}}
@keyframes crest-ink{0%,73%,94%,100%{opacity:.69}80%{opacity:.93}}
"""
TREE_CSS = """
@media(prefers-reduced-motion:no-preference){.tree-guide{animation:read-dir 14s linear infinite;animation-delay:var(--delay)}}
@keyframes read-dir{0%,14%,100%{opacity:.7}5%,8%{opacity:1;fill:currentColor}}
"""
SKILL_CSS = """
@media(prefers-reduced-motion:no-preference){.perm{animation:read-mode .45s ease-out both;animation-delay:var(--delay)}}
@keyframes read-mode{from{opacity:.42}to{opacity:1}}
"""
