"""Rebuilt crisp terminal-art portraits & smooth animations for neofetch.

Channels (190 x 157 local coordinate space, center = (95, 78.5)):
  0. MEOW         — Pixel CRT monitor cat with glancing pupils & scanline
  1. GEMINI       — Crisp geometric 4-point astroid sparkle + scanlines, smooth breathing pulse
  2. OPENAI       — Exact 6-fold rotational hexagonal knot, seamless 0->60deg continuous spin
  3. CLAUDE / 403 — 12-ray Anthropic starburst + crisp RGB chromatic glitch & HTTP 403 stamp
"""
from math import atan2, cos, degrees, radians, sin, sqrt


CX, CY = 95.0, 78.5


def _box(x, y, w, h, fill, r=0, stroke=None):
    edge = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r}" fill="{fill}"{edge}/>'


def _scanline_pattern(pid, P):
    return (
        f'<pattern id="{pid}" width="4" height="3" patternUnits="userSpaceOnUse">'
        f'<path d="M0 2.4H4" stroke="{P["scan_stroke"]}" stroke-opacity="{P["scan_op"]}" stroke-width="0.9"/>'
        f"</pattern>"
    )


def computer_cat(P):
    """Pixel-art CRT monitor cat (MEOW)."""
    def shape(d, fill):
        return f'<path d="{d}" fill="{fill}"/>'

    return "".join([
        shape("M24 49V8h9v7h9v7h9v7h9v6h72v-6h9v-7h9v-7h9V8h9v41h8v78h-8v9H24v-9h-8V49z", P["cat_body"]),
        shape("M32 37V22h6v7h8v8zm116 0h12V22h-5v7h-7z", P["cyan"]),
        _box(21, 42, 150, 84, P["cat_bezel"], 5),
        _box(27, 48, 138, 71, P["cat_inner"], 4),
        _box(32, 53, 128, 60, P["cat_screen"], 3),
        shape("M37 57h32v3H40v20h-3z", P["cat_glare"]),
        shape("M50 74h7v-5h23v5h4v16H50zm60 0h5v-5h23v5h5v16h-33z", P["mint"]),
        '<g class="pupils">' + shape("M67 73h7v13h-7zm60 0h7v13h-7z", P["cat_pupil"]) + "</g>",
        shape("M90 88h13v4h-4v4h-5v-4h-4z", P["gold"]),
        shape("M83 95h4v4h7v-3h5v3h8v-4h4v7h-10v-2h-8v2H83z", P["cat_bezel"]),
        shape("M7 83h20v4H7zm-5 13h23v4H2zm161-13h21v4h-21zm2 13h23v4h-23z", P["cyan"]),
        _box(34, 129, 31, 2, P["cat_slot"]),
        f'<rect class="cat-led" x="151" y="127" width="7" height="4" rx="1" fill="{P["mint"]}"/>',
        shape("M81 136h29v9h15v6H65v-6h16z", P["cat_body"]),
        _box(52, 151, 90, 4, P["cat_stand"]),
    ])


def _sparkle_path(cx, cy, r, k=0.76):
    """Smooth 4-point Gemini astroid centered at (cx, cy) with radius r."""
    c = r * k
    return (
        f"M{cx:.2f} {cy - r:.2f}"
        f" C{cx:.2f} {cy - r + c:.2f} {cx + r - c:.2f} {cy:.2f} {cx + r:.2f} {cy:.2f}"
        f" C{cx + r - c:.2f} {cy:.2f} {cx:.2f} {cy + r - c:.2f} {cx:.2f} {cy + r:.2f}"
        f" C{cx:.2f} {cy + r - c:.2f} {cx - r + c:.2f} {cy:.2f} {cx - r:.2f} {cy:.2f}"
        f" C{cx - r + c:.2f} {cy:.2f} {cx:.2f} {cy - r + c:.2f} {cx:.2f} {cy - r:.2f}Z"
    )


def gemini_art(P):
    """Crisp vector-geometric Gemini 4-point star with terminal scanlines & ambient sparkles."""
    main = _sparkle_path(CX, CY, 59, 0.70)
    inner = _sparkle_path(CX, CY, 25, 0.66)
    mini1 = _sparkle_path(147, 29, 10.5, 0.70)
    mini2 = _sparkle_path(42, 127, 8.0, 0.70)
    mini3 = _sparkle_path(149, 125, 5.5, 0.70)
    return "".join([
        f'<circle class="gemini-ring" cx="{CX:g}" cy="{CY:g}" r="48" fill="none" stroke="{P["mint"]}" stroke-width="1.3" stroke-dasharray="3 4"/>',
        f'<g class="gemini-core">',
        f'<path d="{main}" fill="url(#gem-grad)"/>',
        f'<path d="{main}" fill="url(#icon-scan)"/>',
        f'<path d="{inner}" fill="{P["bg"]}" opacity="0.22"/>',
        f'<path d="{main}" fill="none" stroke="{P["mint"]}" stroke-opacity="0.45" stroke-width="1"/>',
        "</g>",
        f'<path class="gem-twinkle-1" d="{mini1}" fill="{P["cyan"]}"/>',
        f'<path class="gem-twinkle-2" d="{mini2}" fill="{P["mint"]}"/>',
        f'<path class="gem-twinkle-3" d="{mini3}" fill="{P["gold"]}"/>',
    ])


def _openai_petal_path():
    """Generate one exact OpenAI hexagonal blossom petal; 6x 60deg rotation forms the exact knot.

    Geometry around origin (0, 0):
      - Inner hexagon apothem a = 14.0 -> vertex radius h = 2a / sqrt(3) ≈ 16.166
      - Straight spoke starts at inner hex vertex V0, runs along edge V0->V1 (120deg)
        for length L, then curves clockwise in a circular arc of radius R that lands
        cleanly on the outer tangent of the next petal.
    """
    a = 13.8
    h = 2.0 * a / sqrt(3.0)
    # Place lobe center C0 so the circle of radius R is tangent to line L0 (normal at 30deg, offset a)
    # and intersects the neighboring circle C5 smoothly.
    R = 23.0
    # C0 = (dx, dy) in frame rotated by 30deg (n0 = x', u0 = y'):
    # Since circle is tangent to L0 on the +n0 side: x' = a + R.
    # Choose y' (along u0 from midpoint of V0-V1) so the 6 lobes form a tight, balanced blossom.
    xp = a + R
    yp = 10.5
    c30, s30 = cos(radians(30)), sin(radians(30))
    # n0 = (c30, s30), u0 = (-s30, c30)
    cx0 = xp * c30 - yp * s30
    cy0 = xp * s30 + yp * c30

    # Tangent point on line L0 (at x'=a, y'=yp):
    tx0 = a * c30 - yp * s30
    ty0 = a * s30 + yp * c30

    # Start of straight spoke: inner hexagon vertex V0 = (h, 0) -> x'=a, y'=-h/2
    vx0, vy0 = h, 0.0

    # Find exact intersection between this circle (cx0, cy0, R) and the next rotated straight spoke L5
    # Wait: in OpenAI's logo, the arc curves clockwise from (tx0, ty0) around (cx0, cy0)
    # until it meets the straight spoke of petal k=5 (rotated -60deg) OR the outer arc of petal k=5!
    # Compute intersection with spoke k=5 (line with normal at -30deg, offset a):
    # Dot(P, n5) = a where P = C0 + R*(cos t, sin t)
    # n5 = (cos(-30), sin(-30)) = (c30, -s30)
    # dot(C0, n5) + R * cos(t + 30deg) = a  =>  cos(t + 30deg) = (a - dot(C0, n5)) / R
    dot_c_n5 = cx0 * c30 - cy0 * s30
    # We want the arc going clockwise (decreasing angle in standard math, increasing in SVG Y-down?
    # Note: in SVG Y points DOWN, so standard (cos t, sin t) increases CLOCKWISE!).
    # Wait: let's compute tangent angle at T0 relative to C0:
    # T0 - C0 = (-R * c30, -R * s30) -> angle = 210deg (in SVG Y-down: left-up)
    # Moving from V0=(h,0) toward T0=(tx0,ty0): direction is u0=(-0.5, +0.866) (down-left in SVG).
    # At T0, the center C0 is to the RIGHT of direction u0 (since T0->C0 is +n0 = (+0.866, +0.5),
    # cross product u0 x n0 = (-0.5)(0.5) - (0.866)(0.866) = -1 < 0 -> C0 is to the LEFT in Y-down,
    # i.e. curving COUNTER-CLOCKWISE in SVG Y-down = sweep-flag 0!).
    # Let's check exact intersection with neighboring circle C5 (C0 rotated by -60deg):
    c60, s60 = 0.5, sqrt(3.0) / 2.0
    # Rotate C0 by -60deg:
    cx5 = cx0 * c60 + cy0 * s60
    cy5 = -cx0 * s60 + cy0 * c60
    # Distance between C0 and C5:
    dx, dy = cx5 - cx0, cy5 - cy0
    dist = sqrt(dx * dx + dy * dy)
    # Midpoint + perpendicular offset to outer intersection of two equal-radius R circles:
    half = dist / 2.0
    perp = sqrt(max(0.0, R * R - half * half))
    mx, my = (cx0 + cx5) / 2.0, (cy0 + cy5) / 2.0
    # Two intersection points: pick the one FARTHER from origin (outer notch between lobes!)
    ux, uy = -dy / dist, dx / dist
    p1 = (mx + perp * ux, my + perp * uy)
    p2 = (mx - perp * ux, my - perp * uy)
    ex, ey = p1 if (p1[0] ** 2 + p1[1] ** 2) > (p2[0] ** 2 + p2[1] ** 2) else p2

    # Check arc sweep angle (large-arc-flag):
    # Vector from C0 to T0 vs C0 to E:
    a_start = atan2(ty0 - cy0, tx0 - cx0)
    a_end = atan2(ey - cy0, ex - cx0)
    # Going sweep=0 (decreasing angle in SVG Y-down):
    delta = (a_start - a_end) % (2.0 * 3.141592653589793)
    large_arc = 1 if delta > 3.141592653589793 else 0

    return (
        f"M{vx0:.2f} {vy0:.2f}"
        f" L{tx0:.2f} {ty0:.2f}"
        f" A{R:.2f} {R:.2f} 0 {large_arc} 0 {ex:.2f} {ey:.2f}"
    )


def openai_art(P):
    """Mathematically exact 6-fold OpenAI knot with seamless 0->60deg continuous rotation."""
    petal = _openai_petal_path()
    rotors = "".join(
        f'<path d="{petal}" transform="rotate({k * 60})"/>' for k in range(6)
    )
    return "".join([
        f'<g class="openai-rotor">',
        f'<g transform="translate({CX:g} {CY:g})">',
        # Soft outer glow ring
        f'<g fill="none" stroke="{P["cyan"]}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" opacity="0.14">{rotors}</g>',
        # Crisp main blossom knot
        f'<g fill="none" stroke="url(#oai-grad)" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round">{rotors}</g>',
        # Subtle terminal scanline texture on top of the strokes
        f'<g fill="none" stroke="url(#icon-scan)" stroke-width="6.4" stroke-linecap="round" stroke-linejoin="round">{rotors}</g>',
        "</g></g>",
    ])


def _claude_starburst_paths(cx, cy):
    """Crisp 12-ray Anthropic/Claude starburst geometry centered at (cx, cy)."""
    # Authentic slightly organic alternating ray lengths & widths
    rays = [
        (0, 44, 5.2),
        (29, 39, 4.6),
        (58, 45, 5.0),
        (89, 41, 4.8),
        (119, 46, 5.2),
        (150, 38, 4.5),
        (181, 45, 5.2),
        (210, 40, 4.6),
        (240, 46, 5.0),
        (271, 39, 4.7),
        (301, 44, 5.1),
        (331, 41, 4.6),
    ]
    parts = [f'<circle cx="{cx:g}" cy="{cy:g}" r="11.5"/>']
    for deg, length, width in rays:
        rad = radians(deg)
        x2 = cx + length * cos(rad)
        y2 = cy + length * sin(rad)
        parts.append(
            f'<line x1="{cx:g}" y1="{cy:g}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke-width="{width:.1f}" stroke-linecap="round"/>'
        )
    return "".join(parts)


def claude_art(P):
    """Crisp 12-ray Claude starburst + authentic RGB chromatic glitch + HTTP 403 stamp."""
    cy = 67.0
    burst = _claude_starburst_paths(CX, cy)
    return "".join([
        # Chromatic aberration ghost layers (only pop during short glitch bursts)
        f'<g class="claude-ghost-c" fill="{P["cyan"]}" stroke="{P["cyan"]}">{burst}</g>',
        f'<g class="claude-ghost-r" fill="{P["red"]}" stroke="{P["red"]}">{burst}</g>',
        # Primary starburst
        f'<g class="claude-core" fill="{P["red"]}" stroke="{P["red"]}">{burst}</g>',
        # Crisp horizontal glitch tear slices
        f'<g clip-path="url(#claude-tear-a)"><g class="claude-slice-a" fill="{P["red"]}" stroke="{P["red"]}">{burst}</g></g>',
        f'<g clip-path="url(#claude-tear-b)"><g class="claude-slice-b" fill="{P["cyan"]}" stroke="{P["cyan"]}">{burst}</g></g>',
        # Scanline grain over starburst
        f'<g fill="url(#icon-scan)" stroke="url(#icon-scan)" opacity="0.65">{burst}</g>',
        # Crisp HTTP 403 terminal badge below starburst
        f'<g class="claude-badge">',
        _box(27, 126, 136, 22, P["pill_red_bg"], 4, P["pill_red_bd"]),
        f'<text x="{CX:g}" y="141" font-size="11" fill="{P["red"]}" text-anchor="middle" class="bold">HTTP 403 · BANNED</text>',
        "</g>",
    ])


PORTRAIT_CSS = """
.slide,.contact-sheet{opacity:0}.first{opacity:1}
.crt-line,.claude-ghost-c,.claude-ghost-r,.claude-slice-a,.claude-slice-b{opacity:0}
.gemini-core{transform-origin:95px 78.5px}
.gemini-ring{transform-origin:95px 78.5px;opacity:.22}
.openai-rotor{transform-origin:95px 78.5px}
@media(prefers-reduced-motion:no-preference){
  .slide{animation:ch-cycle 16s linear infinite;animation-delay:var(--offset)}
  .crt-line{animation:crt-pass 4s linear infinite}
  .cat-led{animation:led-pulse 2.2s ease-in-out infinite}
  .pupils{animation:glance 6.4s steps(2,end) infinite}
  .gemini-core{animation:gem-breathe 4s ease-in-out infinite}
  .gemini-ring{animation:gem-wave 4s ease-out infinite}
  .gem-twinkle-1{animation:twinkle-a 2.6s ease-in-out infinite}
  .gem-twinkle-2{animation:twinkle-a 2.6s ease-in-out -.9s infinite}
  .gem-twinkle-3{animation:twinkle-a 2.6s ease-in-out -1.7s infinite}
  .openai-rotor{animation:oai-spin 6s linear infinite}
  .claude-core{animation:cl-flicker 4s steps(1,end) infinite}
  .claude-ghost-c{animation:cl-rgb-c 4s steps(1,end) infinite}
  .claude-ghost-r{animation:cl-rgb-r 4s steps(1,end) infinite}
  .claude-slice-a{animation:cl-tear-a 4s steps(1,end) infinite}
  .claude-slice-b{animation:cl-tear-b 4s steps(1,end) infinite}
  .claude-badge{animation:cl-badge 4s steps(1,end) infinite}
}
@keyframes ch-cycle{0%,23.5%{opacity:1}25%,98.5%{opacity:0}100%{opacity:1}}
@keyframes crt-pass{0%,10%{opacity:0;transform:translateY(0)}18%{opacity:.5}68%,100%{opacity:0;transform:translateY(56px)}}
@keyframes led-pulse{0%,100%{opacity:1}50%{opacity:.45}}
@keyframes glance{0%,66%,89%,100%{transform:translateX(0)}72%,83%{transform:translateX(5px)}}
@keyframes gem-breathe{0%,100%{transform:scale(.93)}50%{transform:scale(1.04)}}
@keyframes gem-wave{0%{transform:scale(.76);opacity:.48}75%,100%{transform:scale(1.26);opacity:0}}
@keyframes twinkle-a{0%,100%{opacity:.3}50%{opacity:1}}
@keyframes oai-spin{from{transform:rotate(0deg)}to{transform:rotate(60deg)}}
@keyframes cl-flicker{0%,29%,35%,67%,73%,100%{opacity:1}31%,69%{opacity:.78}}
@keyframes cl-rgb-c{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}29%,67%{opacity:.65;transform:translateX(-4px)}32%,70%{opacity:.45;transform:translateX(2.5px)}}
@keyframes cl-rgb-r{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}29%,67%{opacity:.65;transform:translateX(4px)}32%,70%{opacity:.45;transform:translateX(-2.5px)}}
@keyframes cl-tear-a{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}30%,68%{opacity:.95;transform:translateX(6px)}33%,71%{opacity:.95;transform:translateX(-4px)}}
@keyframes cl-tear-b{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}30%,68%{opacity:.9;transform:translateX(-5px)}33%,71%{opacity:.9;transform:translateX(3px)}}
@keyframes cl-badge{0%,29%,34%,67%,72%,100%{opacity:1}31%,69%{opacity:.35}}
@media(prefers-reduced-motion:reduce){.channels{display:none}.contact-sheet{opacity:1}}
"""


def build_mascot(P, x=24, y=64, w=268, h=242):
    """Render the 4-channel animated viewport for neofetch."""
    portraits = [
        ("meow", "CH 01 · MEOW", P["mint"], computer_cat(P)),
        ("gemini", "CH 02 · GEMINI", P["mint"], gemini_art(P)),
        ("openai", "CH 03 · OPENAI", P["cyan"], openai_art(P)),
        ("claude", "CH 04 · CLAUDE 403", P["red"], claude_art(P)),
    ]
    parts = [
        _box(x, y, w, h, P["panel"], 8, P["border"]),
        # Subtle corner ticks for CRT viewport polish
        f'<path d="M{x+10} {y+1}h-4a5 5 0 0 0-5 5v4 M{x+w-10} {y+1}h4a5 5 0 0 1 5 5v4" fill="none" stroke="{P["muted"]}" stroke-opacity="0.35" stroke-width="1"/>',
        "<defs>",
        _scanline_pattern("icon-scan", P),
        f'<linearGradient id="gem-grad" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{P["mint"]}"/>'
        f'<stop offset="55%" stop-color="{P["cyan"]}"/>'
        f'<stop offset="100%" stop-color="{P["mauve"]}"/></linearGradient>',
        f'<linearGradient id="oai-grad" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{P["cyan"]}"/>'
        f'<stop offset="100%" stop-color="{P["mint"]}"/></linearGradient>',
        '<clipPath id="claude-tear-a"><rect x="0" y="42" width="190" height="10"/></clipPath>',
        '<clipPath id="claude-tear-b"><rect x="0" y="84" width="190" height="8"/></clipPath>',
    ]
    for name, _, _, art in portraits:
        parts.append(f'<g id="portrait-{name}">{art}</g>')
    parts.append('</defs><g class="channels">')

    # Center 190x157 viewport cleanly inside the (w x h) panel
    px = x + (w - 190) / 2
    py = y + 32
    dots_x0 = x + (w - (4 * 14 + 3 * 6)) / 2
    dots_y = y + h - 18

    for i, (name, label, color, _) in enumerate(portraits):
        # 16s cycle, 4s per slide: i=0 -> 0s, i=1 -> -12s (enters at 4s), i=2 -> -8s (8s), i=3 -> -4s (12s)
        offset = 4 * i - 16 if i else 0
        parts.append(f'<g class="slide{" first" if not i else ""}" style="--offset:{offset}s">')
        parts.append(
            f'<circle cx="{x + 16:g}" cy="{y + 18:g}" r="3" fill="{color}"/>'
            f'<text x="{x + 26:g}" y="{y + 21.5:g}" font-size="10.5" fill="{color}" class="bold">{label}</text>'
        )
        parts.append(f'<g transform="translate({px:g} {py:g})"><use href="#portrait-{name}"/>')
        if name == "meow":
            parts.append(f'<rect class="crt-line" x="34" y="55" width="122" height="1.5" fill="{P["mint"]}"/>')
        parts.append("</g>")
        for j in range(4):
            parts.append(_box(dots_x0 + j * 20, dots_y, 14, 3.2, color if i == j else P["border"], 1.6))
        parts.append("</g>")

    # Contact sheet fallback when prefers-reduced-motion: reduce
    parts.append('</g><g class="contact-sheet">')
    for i, (name, label, color, _) in enumerate(portraits):
        short_lbl = label.split("· ", 1)[-1]
        cx = x + 16 + (i % 2) * 124
        cy = y + 14 + (i // 2) * 110
        parts.append(f'<use href="#portrait-{name}" transform="translate({cx + 17:g} {cy:g}) scale(.45)"/>')
        parts.append(
            f'<text x="{cx + 60:g}" y="{cy + 92:g}" font-size="10" fill="{color}" text-anchor="middle" class="bold">{short_lbl}</text>'
        )
    parts.append("</g>")
    return "".join(parts)
