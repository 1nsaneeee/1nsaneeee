"""Official brand ASCII-art portraits & smooth terminal animations for neofetch.

Sampled directly from official @lobehub/icons 24x24 SVGs onto upright monospace grids:
  0. MEOW         - Pixel CRT monitor cat with glancing pupils & scanline
  1. GEMINI       - Official Google Gemini 4-color ASCII star, breathing pulse + ASCII sparkles
  2. OPENAI       - Official OpenAI 6-fold knot, 8-frame upright ASCII shader spin (0..60deg seamless)
  3. CLAUDE / 403 - Official Claude #D97757 ASCII starburst + RGB chromatic glitch & HTTP 403 pill
"""
from html import escape
import re

CX, CY = 95.0, 78.5

GEMINI_ASCII = (
    '',
    '                :',
    '               :@:',
    '               #@#',
    '              +@@@+',
    '             :@@@@@:',
    '            :@@@@@@@:',
    '           +@@@@@@@@@+',
    '         :#@@@@@@@@@@@#:',
    '       :#@@@@@@@@@@@@@@@#:',
    '   .:+#@@@@@@@@@@@@@@@@@@@#*:.',
    '  +@@@@@@@@@@@@@@@@@@@@@@@@@@@+',
    '   .:*#@@@@@@@@@@@@@@@@@@@#+:.',
    '       :#@@@@@@@@@@@@@@@#:',
    '         :#@@@@@@@@@@@#:',
    '           +@@@@@@@@@+',
    '            :@@@@@@@:',
    '             :@@@@@:',
    '              +@@@+',
    '               #@#',
    '               :@:',
    '                :',
    '',
)

OPENAI_FRAMES = (
    (
        '',
        '           +#@@@@@+',
        '         +@#:.  .:#@**###+.',
        '        *@:      .#@@*++*#@@:',
        '       :@:     +@@*.       *@*',
        '      .@#   .*@@+           +@+',
        '    +@@@*   @@.     +@@#:    #@',
        '   #@: @*   @+   .*@@+.+@@*. :@.',
        '  #@   @*   @+ :#@@#     :#@#*@.',
        ' :@.   @*   @#@@+.+#@*.    .*@@.',
        ' #@    @*   @#:     .@@#:     *@:',
        ' #@    @*   @+       +@#@@+    #@',
        ' +@.   #@*. @+       +@  :@@   .@+',
        '  @#    .#@@@+       +@   *@    @#',
        '  .@#.    .+@@+.    +@@   *@    @*',
        '   .@@#:     :#@*:#@##@   *@   :@:',
        '   .@++@@*.    #@@*. +@   *@  .@#',
        '   .@:  :#@#+#@#:    +@   *@.*@*',
        '    @#    .*@*.     +@@   *@@#:',
        '    :@*          .*@@:    ##',
        '     :@#.      :#@*.     +@.',
        '      .*@@####@@*       +@+',
        '         .+++::#@*:..:*@@.',
        '                .*#@@#*.',
        '',
),
    (
        '              ....',
        '           .*@@@@@@#:',
        '          *@*.    .+@#. .',
        '         *@.       .@@@@@@@*.',
        '       .+@:    .+#@@*:   .:#@*',
        '    .*@@@#   +#@#+.         :@#',
        '   :@#..@*   @#      .:*.    :@+',
        '  :@*  .@+  .@:   .+#@@#@#.   #@',
        '  @#   :@.  :@:.*@@@*   .#@*  *@',
        ' :@:   +@   *@@@*.:#@:    .@@+#@',
        ' :@.   #@   #@.     :@#:    :@@*',
        ' .@+   #@+  @#       :@@#.    *@.',
        '  #@    +@#+@+       +@:*@*.   #@',
        '   ##.    *@@:       *@  .@@   :@.',
        '   *@@*    .*@*.    :@#   @#   .@:',
        '   @#.#@+    .#@++#@@@*   @*   :@.',
        '   @*  :@@+  .*@@#+ .@:  .@:   #@',
        '   @@    +@@@@*.    :@.  :@.  #@.',
        '   :@+     :.      .@@   *@:+@@.',
        '    *@*        .:#@@*.   #@@#:',
        '     :@@*:...+#@@*.     :@:',
        '       :*@@@@@#.       :@+',
        '             +@#+.  .+@@:',
        '              .+#@@@@#+',
        '',
),
    (
        '               .::..',
        '            .*@@##@@@+',
        '           *@*.     +@@.',
        '          *@.        :@@*+:.',
        '      +@@@@:    .:*#@@#**#@@#:',
        '    +@@:.#@   +@@@*+.      .*@#',
        '   *@:   @*   @#             .@#',
        '  :@:   +@.  :@.    .+#@@+    :@:',
        '  #@    @#   #@:*#@@@*+::@#.   @*',
        '  @#   .@:  .@@#*+.#@:   .#@:  @#',
        '  #@   +@:  +@.     +@*    +@*:@+',
        '  :@:   +@* @#       .@@.   .@@@',
        '   #@.   .@@@:       :@#@*    #@',
        '   @@@+    #@+       #@ :@#.  .@*',
        '  +@.:@#    +@#     .@+  .@*   #@',
        '  *@  .#@:   .@@+*@@@@.  :@.   *@',
        '  *@.   +@*+#@@@#*:.@#   #@    @#',
        '  .@*    .##+:     .@:  .@+   +@:',
        '   +@+            .#@   +@   +@+',
        '    +@#:     .+*@@@#:   @@:*@@:',
        '     .*@@@@@@@#*:.     +@@@*:',
        '        ..:#@:        :@+',
        '            *@#:.  .:#@+',
        '             .*@@@@@#+',
        '                 ..',
),
    (
        '                ..:.',
        '             .*@@@@@@@+',
        '            +@#.     +@@.',
        '       :*###@:         *@.',
        '     +@@*:*@+    ..:+**#@@#*.',
        '    *@+   #@   +@@@@#**+:.+*@@:',
        '   *@.   :@:   @#            +@*',
        '   @*    @#   *@       ...    :@+',
        '  .@:   +@.  .@@+*###@@@@@*    #@',
        '  .@:   @#   #@**++*@#   :@*   :@.',
        '   @*   +@+ :@:     +@+   :@#  +@.',
        '   #@:   +@*@#       :@*   .@# #@',
        '  :@#@+   :@@.       .@@*   .@@@:',
        '  @# +@+   :@*       #@:@#   .@#',
        ' .@+  +@*   .@*     :@: .@#   +@.',
        ' .@+   :@* ..*@@*###@#   *@.  .@:',
        '  @@    :@@@@#***+:#@.  .@*   .@:',
        '  .@*              @*   #@    *@.',
        '   :@#.          .#@   :@+   :@+',
        '    .*@@*++*##@@@@@:   @#   *@*',
        '       :+@@#::..      +@#*#@#.',
        '          ##.        +@***:.',
        '           #@#:.  .:@@:',
        '            .*@@@@@#+',
        '                .',
),
    (
        '                  ...',
        '               :#@@@@@#:',
        '         .::::@@+.   .+@@.',
        '      .#@@@#@@*         *@.',
        '     +@#.  .@*          .@@',
        '    *@:    @#   :@@@@@@@@@@@#:',
        '   .@+    #@.  .@#         .*@@.',
        '   +@.   *@.   ##             #@:',
        '   *@   :@+   *@#***+*****:    #@',
        '   :@.  .@*  +@*+***@@***#@:   .@+',
        '   *@#   +@::@+     :@+   *@.   @*',
        '  *@*@*   *@@*       +@:   #@   @*',
        ' .@* +@:   #@.        @@.  .@# +@.',
        ' +@.  *@.   @#       #@@#   .@#@*',
        ' +@.   #@   .@*     +@..@*   +@*',
        ' .@:   .@@###@@@###*@+  :@+   @*',
        '  #@.   .:::::::::*@*   :@+   @#',
        '   @@:            ##   .@*    @*',
        '    *@@+.........#@.   @#    +@.',
        '      +#@@@@@@@@@@.   #@    +@*',
        '        #@.          *@.  :#@+',
        '         #@.        *@@@@@@*.',
        '          *@#+. ..*@#....',
        '           .+#@@@@*.',
        '',
),
    (
        '',
        '                .+#@@@#+.',
        '        .*@@@@**@#:...:#@#',
        '      .#@*:..*@@.       .@@.',
        '     :@#    .##           #@',
        '    .@*    .@#   .#@@##*+:*@:',
        '    *@.   :@*   .@@..:+*###@@*.',
        '    #@   :@*   .@*          .*@*',
        '    #@   #@   .@@#++:..       .@#',
        '   +@@.  .@* :@*:+*#@@@@@@#.   :@+',
        '  *@+##   *@*@*     .@* .:@@    ##',
        ' .@+ :@+   @@+       *@   :@+   #@',
        ' *@   #@   +@.        @#   #@   @#',
        ' #@   .@*   #@       +@@.  .@* +@:',
        ' *@    *@*:.+@+     *@+##   *@*@*',
        ' .@*    +##@@@@@@#+#@: :@:   @@+',
        '  +@*         ...*@@.   @@   #@',
        '   :@@+.         *@.   *@:   #@',
        '     :@@@@@#**+:@@.   *@:    @#',
        '       @#.:++*###.   #@:    *@.',
        '       *@.          #@.   .#@:',
        '        #@+       .@@#::+#@#.',
        '         +@@*+::+#@*+*###+.',
        '           .*###*:',
        '',
),
    (
        '',
        '           .::..  .:***+.',
        '        :#@@##@@##@#*+*#@@:',
        '       #@*.    #@*       +@#',
        '      #@.    .@@.         .@#',
        '     +@:    +@*    +#*:.   +@.',
        '     #@   .#@:   .@@+*#@@@**@+',
        '     @#   @@.   :@*     .:*#@@+',
        '   :@@@   *@   #@@*..        :@@.',
        '  +@++@.  .@:.@@.:*@@@#*:.     #@.',
        ' .@+  @*   @@@*     .@@*@@@*    @*',
        ' #@   *@   +@:       *@   *@.   *@',
        ' @#   .@:  .@:       .@+  .@+   *@',
        ' #@    @@.  #@       :@#   #@   #@',
        ' :@:   :#@@#@@:     *@#@.  :@. +@:',
        '  #@:     .:*#@@#*:@@..@+   @*+@*',
        '   *@*.         :@@#   #@   *@@:',
        '    .#@@#*:.    *@:    #@   +@.',
        '     .@*+*@@@#*@@.   :@#.   #@',
        '      @#    .:*+    *@*    .@*',
        '      :@*         .#@.    .@#',
        '       +@#.      *@@.   .*@#',
        '        .*@@#*#@@#*@@@@@@#.',
        '           .:++.    ....',
        '',
),
    (
        '',
        '          .+*###+.    ..',
        '        .#@#*::+#@##@@@@@#+',
        '       .@#.     :@@+.   .+@@.',
        '      .@#     :@@+         *@:',
        '      *@    .#@*    .+.     #@',
        '     .@#   *@#.    *@@@@*:  .@:',
        '   .#@@#   @#    +@#.  .*@@#*@+',
        '  :@#.#@   #@  :@@@:      .+#@#.',
        ' .@#  +@   *@+@@+.*@@#:.     .#@:',
        ' *@.  :@.  :@@*     .#@@@*.    *@.',
        ' #@   .@+  .@+       +@.:#@@    @#',
        ' #@    @#   @*       .@.  +@.   *@',
        ' +@:   *@@*:@#       .@+  .@:   *@',
        '  #@.    :*@@@+     *@@*   @*   @#',
        '   #@:      .+@@#:+@@:##   @#  *@.',
        '    +@@#:      .#@@:  *@   *@.#@:',
        '    .@**@@#+. .#@+    +@.  +@@#.',
        '    .@+  .+#@@@*    .*@*   +@.',
        '     #@.     ..    *@#.    @#',
        '      #@.        +@@:     *@.',
        '       *@#:   .+@@+     .#@:',
        '        .*@@@@@#*@@****@@#.',
        '                  :+**+:',
        '',
),
)

CLAUDE_ASCII = (
    '        ..',
    '       .@@#      ##',
    '        @@@*    :@@     .',
    '        .@@@:   +@#   .*@#',
    '   .+:   :@@@   *@+  :@@@#',
    '   *@@#:  +@@#  #@. +@@@*',
    '    :#@@#: +@@+ @# *@@@*',
    '      :#@@#:#@@:@#*@@@+',
    '        .*@@@@@@@@@@@+   ..:+:',
    ' ...      .+@@@@@@@@@*#@@@@@#+',
    ' *@@@@####**#@@@@@@@@#*+:.',
    '      .....:#@@@@@@@#**++++::',
    '         .*@##@@@@@@*.:*#@@@@*',
    '      .+@@#::@**@@@@@#.    ..',
    '    .*@@*. :@* #*.@@++@*',
    '    *@+.  +@* .@+ :@@..#@:',
    '         *@+  :@:  +@@. :#*',
    '       .#@:   *@.   +@@.  .',
    '       :#.   .@@.    :*.',
    '             .@@',
    '              ..',
)

def _box(x, y, w, h, fill, r=0, stroke=None):
    edge = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r}" fill="{fill}"{edge}/>'


def _ascii_grid(rows, pitch=4.6, step=6.2, font_size=7.4, cx=CX, cy=CY, bed_opacity=0.22):
    """Render upright monospace ASCII rows + optional subtle pixel bed, inheriting fill from parent.

    Each non-space token is positioned as an individual <tspan> at exact grid x coordinates so
    SVG renderers (including Chromium <use> shadow trees) can NEVER collapse internal spaces.
    """
    width = max((len(r.rstrip()) for r in rows), default=0)
    x0 = cx - (width * pitch) / 2.0
    y0 = cy - (len(rows) * step) / 2.0
    bed = []
    ink = []
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        y = y0 + i * step
        if bed_opacity > 0:
            for run in re.finditer("[@#*]+", row):
                n = len(run[0])
                bed.append(f"M{run.start()} {i}h{n}v1h-{n}z")
        spans = []
        for m in re.finditer(r"\S+", row):
            tok = m.group(0)
            if len(tok) == 1:
                tx = x0 + (m.start() + 0.5) * pitch
                spans.append(f'<tspan x="{tx:.2f}" text-anchor="middle">{escape(tok)}</tspan>')
            else:
                tx = x0 + m.start() * pitch
                tw = len(tok) * pitch
                spans.append(
                    f'<tspan x="{tx:.2f}" textLength="{tw:.2f}" '
                    f'lengthAdjust="spacingAndGlyphs">{escape(tok)}</tspan>'
                )
        ink.append(f'<text y="{y + step * 0.86:.2f}">{"".join(spans)}</text>')
    parts = []
    if bed and bed_opacity > 0:
        parts.append(
            f'<path opacity="{bed_opacity:g}" transform="translate({x0:.2f} {y0:.2f}) scale({pitch} {step})" '
            f'd="{"".join(bed)}"/>'
        )
    parts.append(
        f'<g font-size="{font_size:g}" font-weight="700">'
        + "".join(ink)
        + "</g>"
    )
    return "".join(parts)


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


def gemini_art(P):
    """Official Google Gemini 4-color upright ASCII art + breathing pulse + ASCII sparkles."""
    return "".join([
        f'<circle class="gemini-ring" cx="{CX:g}" cy="{CY:g}" r="49" fill="none" stroke="#3186FF" stroke-width="1.2" stroke-dasharray="3 4"/>',
        '<g class="gemini-core">',
        '<use href="#gem-ascii-body" fill="url(#gem-4c)"/>',
        "</g>",
        '<text class="gem-twinkle-1 bold" x="148" y="34" font-size="13" fill="#3186FF" text-anchor="middle">✦</text>',
        '<text class="gem-twinkle-2 bold" x="42" y="130" font-size="12" fill="#08B962" text-anchor="middle">+</text>',
        '<text class="gem-twinkle-3 bold" x="149" y="128" font-size="11" fill="#FABC12" text-anchor="middle">*</text>',
    ])


def openai_art(P):
    """Official OpenAI 6-fold knot rendered as 8-frame upright ASCII shader spin (0..60deg seamless)."""
    fill = "#e6edf3" if P["name"] == "dark" else "#1f2328"
    frames_svg = []
    for k, rows in enumerate(OPENAI_FRAMES):
        grid = _ascii_grid(rows, pitch=4.35, step=5.85, font_size=6.8, cx=CX, cy=CY, bed_opacity=0.0)
        frames_svg.append(f'<g class="oai-frame oai-f{k}" fill="{fill}">{grid}</g>')
    return "".join(frames_svg)


def claude_art(P):
    """Official Claude #D97757 upright ASCII starburst + RGB chromatic glitch & HTTP 403 pill."""
    brand = "#D97757"
    return "".join([
        f'<g class="claude-ghost-c"><use href="#claude-ascii-body" fill="{P["cyan"]}"/></g>',
        f'<g class="claude-ghost-r"><use href="#claude-ascii-body" fill="{P["red"]}"/></g>',
        f'<g class="claude-core"><use href="#claude-ascii-body" fill="{brand}"/></g>',
        f'<g clip-path="url(#claude-tear-a)"><g class="claude-slice-a"><use href="#claude-ascii-body" fill="{brand}"/></g></g>',
        f'<g clip-path="url(#claude-tear-b)"><g class="claude-slice-b"><use href="#claude-ascii-body" fill="{P["cyan"]}"/></g></g>',
        '<g class="claude-badge">',
        _box(27, 129, 136, 22, P["pill_red_bg"], 4, P["pill_red_bd"]),
        f'<text x="{CX:g}" y="144" font-size="11" fill="{P["red"]}" text-anchor="middle" class="bold">HTTP 403 · BANNED</text>',
        "</g>",
    ])


PORTRAIT_CSS = """
.slide,.contact-sheet{opacity:0}.first{opacity:1}
.oai-frame{opacity:0}.oai-f0{opacity:1}
.crt-line,.claude-ghost-c,.claude-ghost-r,.claude-slice-a,.claude-slice-b{opacity:0}
.gemini-core{transform-origin:95px 78.5px}
.gemini-ring{transform-origin:95px 78.5px;opacity:.22}
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
  .oai-frame{animation:oai-tick 2s steps(1,end) infinite}
  .oai-f0{animation-delay:0s}
  .oai-f1{animation-delay:-1.75s}
  .oai-f2{animation-delay:-1.5s}
  .oai-f3{animation-delay:-1.25s}
  .oai-f4{animation-delay:-1s}
  .oai-f5{animation-delay:-.75s}
  .oai-f6{animation-delay:-.5s}
  .oai-f7{animation-delay:-.25s}
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
@keyframes gem-breathe{0%,100%{transform:scale(.95)}50%{transform:scale(1.04)}}
@keyframes gem-wave{0%{transform:scale(.78);opacity:.42}75%,100%{transform:scale(1.26);opacity:0}}
@keyframes twinkle-a{0%,100%{opacity:.28}50%{opacity:1}}
@keyframes oai-tick{0%{opacity:1}12.5%,100%{opacity:0}}
@keyframes cl-flicker{0%,29%,35%,67%,73%,100%{opacity:1}31%,69%{opacity:.78}}
@keyframes cl-rgb-c{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}29%,67%{opacity:.6;transform:translateX(-4px)}32%,70%{opacity:.4;transform:translateX(2.5px)}}
@keyframes cl-rgb-r{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}29%,67%{opacity:.6;transform:translateX(4px)}32%,70%{opacity:.4;transform:translateX(-2.5px)}}
@keyframes cl-tear-a{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}30%,68%{opacity:.95;transform:translateX(6px)}33%,71%{opacity:.95;transform:translateX(-4px)}}
@keyframes cl-tear-b{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}30%,68%{opacity:.9;transform:translateX(-5px)}33%,71%{opacity:.9;transform:translateX(3px)}}
@keyframes cl-badge{0%,29%,34%,67%,72%,100%{opacity:1}31%,69%{opacity:.35}}
@media(prefers-reduced-motion:reduce){.channels{display:none}.contact-sheet{opacity:1}}
"""


def build_mascot(P, x=24, y=22, w=268, h=242):
    """Render the 4-channel animated ASCII viewport for neofetch."""
    portraits = [
        ("meow", "CH 01 · MEOW", P["mint"], computer_cat(P)),
        ("gemini", "CH 02 · GEMINI", "#3186FF", gemini_art(P)),
        ("openai", "CH 03 · OPENAI", P["cyan"], openai_art(P)),
        ("claude", "CH 04 · CLAUDE 403", "#D97757", claude_art(P)),
    ]
    gem_grid = _ascii_grid(GEMINI_ASCII, pitch=4.65, step=6.1, font_size=7.4, cx=CX, cy=CY, bed_opacity=0.22)
    cla_grid = _ascii_grid(CLAUDE_ASCII, pitch=4.25, step=5.6, font_size=7.0, cx=CX, cy=64.0, bed_opacity=0.20)

    parts = [
        _box(x, y, w, h, P["panel"], 8, P["border"]),
        f'<path d="M{x+10} {y+1}h-4a5 5 0 0 0-5 5v4 M{x+w-10} {y+1}h4a5 5 0 0 1 5 5v4" fill="none" stroke="{P["muted"]}" stroke-opacity="0.35" stroke-width="1"/>',
        "<defs>",
        # Single vibrant Google 4-color gradient (Red -> Yellow -> Green -> Blue, zero muddy overlap)
        '<linearGradient id="gem-4c" gradientUnits="userSpaceOnUse" x1="36" y1="26" x2="146" y2="128">'
        '<stop offset="0%" stop-color="#F94543"/>'
        '<stop offset="28%" stop-color="#FABC12"/>'
        '<stop offset="56%" stop-color="#08B962"/>'
        '<stop offset="86%" stop-color="#3186FF"/>'
        '<stop offset="100%" stop-color="#58A6FF"/>'
        "</linearGradient>",
        '<clipPath id="claude-tear-a"><rect x="0" y="40" width="190" height="10"/></clipPath>',
        '<clipPath id="claude-tear-b"><rect x="0" y="80" width="190" height="8"/></clipPath>',
        f'<g id="gem-ascii-body">{gem_grid}</g>',
        f'<g id="claude-ascii-body">{cla_grid}</g>',
    ]
    for name, _, _, art in portraits:
        parts.append(f'<g id="portrait-{name}">{art}</g>')
    parts.append('</defs><g class="channels">')

    px = x + (w - 190) / 2
    py = y + 32
    dots_x0 = x + (w - (4 * 14 + 3 * 6)) / 2
    dots_y = y + h - 18

    for i, (name, label, color, _) in enumerate(portraits):
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
