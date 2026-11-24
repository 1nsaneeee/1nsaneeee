"""Official brand SVG portraits & smooth terminal animations for neofetch.

Channels (190 x 157 local coordinate space, center = (95, 78.5)):
  0. MEOW         — Pixel CRT monitor cat with glancing pupils & scanline
  1. GEMINI       — Official Google Gemini 4-color path, smooth breathing pulse
  2. OPENAI       — Official OpenAI 6-fold knot path, seamless 0->60deg continuous spin
  3. CLAUDE / 403 — Official Claude starburst path (#D97757) + RGB glitch & HTTP 403 badge
"""

CX, CY = 95.0, 78.5

# Exact official 24x24 paths from @lobehub/icons
GEMINI_D = (
    "M20.616 10.835a14.147 14.147 0 01-4.45-3.001 14.111 14.111 0 01-3.678-6.452"
    ".503.503 0 00-.975 0 14.134 14.134 0 01-3.679 6.452 14.155 14.155 0 01-4.45 3.001"
    "c-.65.28-1.318.505-2.002.678a.502.502 0 000 .975c.684.172 1.35.397 2.002.677"
    "a14.147 14.147 0 014.45 3.001 14.112 14.112 0 013.679 6.453.502.502 0 00.975 0"
    "c.172-.685.397-1.351.677-2.003a14.145 14.145 0 013.001-4.45 14.113 14.113 0 016.453-3.678"
    ".503.503 0 000-.975 13.245 13.245 0 01-2.003-.678z"
)

OPENAI_D = (
    "M9.205 8.658v-2.26c0-.19.072-.333.238-.428l4.543-2.616c.619-.357 1.356-.523 2.117-.523 "
    "2.854 0 4.662 2.212 4.662 4.566 0 .167 0 .357-.024.547l-4.71-2.759a.797.797 0 00-.856 0"
    "l-5.97 3.473zm10.609 8.8V12.06c0-.333-.143-.57-.429-.737l-5.97-3.473 1.95-1.118"
    "a.433.433 0 01.476 0l4.543 2.617c1.309.76 2.189 2.378 2.189 3.948 0 1.808-1.07 3.473-2.76 4.163z"
    "M7.802 12.703l-1.95-1.142c-.167-.095-.239-.238-.239-.428V5.899c0-2.545 1.95-4.472 4.591-4.472 "
    "1 0 1.927.333 2.712.928L8.23 5.067c-.285.166-.428.404-.428.737v6.898z"
    "M12 15.128l-2.795-1.57v-3.33L12 8.658l2.795 1.57v3.33L12 15.128z"
    "m1.796 7.23c-1 0-1.927-.332-2.712-.927l4.686-2.712c.285-.166.428-.404.428-.737v-6.898"
    "l1.974 1.142c.167.095.238.238.238.428v5.233c0 2.545-1.974 4.472-4.614 4.472z"
    "m-5.637-5.303l-4.544-2.617c-1.308-.761-2.188-2.378-2.188-3.948A4.482 4.482 0 014.21 6.327v5.423"
    "c0 .333.143.571.428.738l5.947 3.449-1.95 1.118a.432.432 0 01-.476 0z"
    "m-.262 3.9c-2.688 0-4.662-2.021-4.662-4.519 0-.19.024-.38.047-.57l4.686 2.71"
    "c.286.167.571.167.856 0l5.97-3.448v2.26c0 .19-.07.333-.237.428l-4.543 2.616"
    "c-.619.357-1.356.523-2.117.523zm5.899 2.83a5.947 5.947 0 005.827-4.756"
    "C22.287 18.339 24 15.84 24 13.296c0-1.665-.713-3.282-1.998-4.448.119-.5.19-.999.19-1.498 "
    "0-3.401-2.759-5.947-5.946-5.947-.642 0-1.26.095-1.88.31A5.962 5.962 0 0010.205 0"
    "a5.947 5.947 0 00-5.827 4.757C1.713 5.447 0 7.945 0 10.49c0 1.666.713 3.283 1.998 4.448"
    "-.119.5-.19 1-.19 1.499 0 3.401 2.759 5.946 5.946 5.946.642 0 1.26-.095 1.88-.309"
    "a5.96 5.96 0 004.162 1.713z"
)

CLAUDE_D = (
    "M4.709 15.955l4.72-2.647.08-.23-.08-.128H9.2l-.79-.048-2.698-.073-2.339-.097-2.266-.122"
    "-.571-.121L0 11.784l.055-.352.48-.321.686.06 1.52.103 2.278.158 1.652.097 2.449.255h.389"
    "l.055-.157-.134-.098-.103-.097-2.358-1.596-2.552-1.688-1.336-.972-.724-.491-.364-.462"
    "-.158-1.008.656-.722.881.06.225.061.893.686 1.908 1.476 2.491 1.833.365.304.145-.103"
    ".019-.073-.164-.274-1.355-2.446-1.446-2.49-.644-1.032-.17-.619a2.97 2.97 0 01-.104-.729"
    "L6.283.134 6.696 0l.996.134.42.364.62 1.414 1.002 2.229 1.555 3.03.456.898.243.832"
    ".091.255h.158V9.01l.128-1.706.237-2.095.23-2.695.08-.76.376-.91.747-.492.584.28.48.685"
    "-.067.444-.286 1.851-.559 2.903-.364 1.942h.212l.243-.242.985-1.306 1.652-2.064.73-.82"
    ".85-.904.547-.431h1.033l.76 1.129-.34 1.166-1.064 1.347-.881 1.142-1.264 1.7-.79 1.36"
    ".073.11.188-.02 2.856-.606 1.543-.28 1.841-.315.833.388.091.395-.328.807-1.969.486"
    "-2.309.462-3.439.813-.042.03.049.061 1.549.146.662.036h1.622l3.02.225.79.522.474.638"
    "-.079.485-1.215.62-1.64-.389-3.829-.91-1.312-.329h-.182v.11l1.093 1.068 2.006 1.81"
    " 2.509 2.33.127.578-.322.455-.34-.049-2.205-1.657-.851-.747-1.926-1.62h-.128v.17"
    "l.444.649 2.345 3.521.122 1.08-.17.353-.608.213-.668-.122-1.374-1.925-1.415-2.167"
    "-1.143-1.943-.14.08-.674 7.254-.316.37-.729.28-.607-.461-.322-.747.322-1.476.389-1.924"
    ".315-1.53.286-1.9.17-.632-.012-.042-.14.018-1.434 1.967-2.18 2.945-1.726 1.845-.414.164"
    "-.717-.37.067-.662.401-.589 2.388-3.036 1.44-1.882.93-1.086-.006-.158h-.055L4.132 18.56"
    "l-1.13.146-.487-.456.061-.746.231-.243 1.908-1.312-.006.006z"
)


def _box(x, y, w, h, fill, r=0, stroke=None):
    edge = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r}" fill="{fill}"{edge}/>'


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
    """Exact official Google Gemini 4-color icon with smooth breathing pulse & twinkling mini stars."""
    # Scale 24x24 -> 112x112 centered at (95, 78.5)
    s = 4.75
    return "".join([
        f'<circle class="gemini-ring" cx="{CX:g}" cy="{CY:g}" r="48" fill="none" stroke="#3186FF" stroke-width="1.2" stroke-dasharray="3 4"/>',
        f'<g class="gemini-core">',
        f'<g transform="translate({CX:g} {CY:g}) scale({s}) translate(-12 -12)">',
        f'<path d="{GEMINI_D}" fill="#3186FF"/>',
        f'<path d="{GEMINI_D}" fill="url(#gem-g0)"/>',
        f'<path d="{GEMINI_D}" fill="url(#gem-g1)"/>',
        f'<path d="{GEMINI_D}" fill="url(#gem-g2)"/>',
        "</g></g>",
        # Subtle companion sparkles using exact scaled Gemini silhouette
        f'<g class="gem-twinkle-1" transform="translate(148 30) scale(0.85) translate(-12 -12)"><path d="{GEMINI_D}" fill="#3186FF"/></g>',
        f'<g class="gem-twinkle-2" transform="translate(42 126) scale(0.65) translate(-12 -12)"><path d="{GEMINI_D}" fill="#08B962"/></g>',
        f'<g class="gem-twinkle-3" transform="translate(148 124) scale(0.5) translate(-12 -12)"><path d="{GEMINI_D}" fill="#FABC12"/></g>',
    ])


def openai_art(P):
    """Exact official OpenAI 6-fold knot with 100% seamless 0->60deg continuous spin."""
    # Exact center of official 24x24 OpenAI knot is (12.0, 12.0); scale 4.5 -> 108px
    s = 4.5
    fill = "#e6edf3" if P["name"] == "dark" else "#1f2328"
    return "".join([
        f'<g class="openai-rotor">',
        f'<g transform="translate({CX:g} {CY:g}) scale({s}) translate(-12 -12)">',
        f'<path d="{OPENAI_D}" fill="{P["cyan"]}" fill-rule="evenodd" opacity="0.18" transform="scale(1.06)" transform-origin="12 12"/>',
        f'<path d="{OPENAI_D}" fill="{fill}" fill-rule="evenodd"/>',
        "</g></g>",
    ])


def claude_art(P):
    """Exact official Claude starburst (#D97757) with RGB chromatic glitch + HTTP 403 pill."""
    cy = 65.0
    s = 4.15
    tr = f"translate({CX:g} {cy:g}) scale({s}) translate(-12 -12)"
    brand = "#D97757"
    return "".join([
        f'<g class="claude-ghost-c"><g transform="{tr}"><path d="{CLAUDE_D}" fill="{P["cyan"]}"/></g></g>',
        f'<g class="claude-ghost-r"><g transform="{tr}"><path d="{CLAUDE_D}" fill="{P["red"]}"/></g></g>',
        f'<g class="claude-core"><g transform="{tr}"><path d="{CLAUDE_D}" fill="{brand}"/></g></g>',
        f'<g clip-path="url(#claude-tear-a)"><g class="claude-slice-a"><g transform="{tr}"><path d="{CLAUDE_D}" fill="{brand}"/></g></g></g>',
        f'<g clip-path="url(#claude-tear-b)"><g class="claude-slice-b"><g transform="{tr}"><path d="{CLAUDE_D}" fill="{P["cyan"]}"/></g></g></g>',
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
@keyframes gem-breathe{0%,100%{transform:scale(.94)}50%{transform:scale(1.04)}}
@keyframes gem-wave{0%{transform:scale(.78);opacity:.42}75%,100%{transform:scale(1.26);opacity:0}}
@keyframes twinkle-a{0%,100%{opacity:.28}50%{opacity:1}}
@keyframes oai-spin{from{transform:rotate(0deg)}to{transform:rotate(60deg)}}
@keyframes cl-flicker{0%,29%,35%,67%,73%,100%{opacity:1}31%,69%{opacity:.78}}
@keyframes cl-rgb-c{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}29%,67%{opacity:.6;transform:translateX(-4px)}32%,70%{opacity:.4;transform:translateX(2.5px)}}
@keyframes cl-rgb-r{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}29%,67%{opacity:.6;transform:translateX(4px)}32%,70%{opacity:.4;transform:translateX(-2.5px)}}
@keyframes cl-tear-a{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}30%,68%{opacity:.95;transform:translateX(6px)}33%,71%{opacity:.95;transform:translateX(-4px)}}
@keyframes cl-tear-b{0%,28%,35%,66%,73%,100%{opacity:0;transform:translateX(0)}30%,68%{opacity:.9;transform:translateX(-5px)}33%,71%{opacity:.9;transform:translateX(3px)}}
@keyframes cl-badge{0%,29%,34%,67%,72%,100%{opacity:1}31%,69%{opacity:.35}}
@media(prefers-reduced-motion:reduce){.channels{display:none}.contact-sheet{opacity:1}}
"""


def build_mascot(P, x=24, y=22, w=268, h=242):
    """Render the 4-channel animated viewport for neofetch."""
    portraits = [
        ("meow", "CH 01 · MEOW", P["mint"], computer_cat(P)),
        ("gemini", "CH 02 · GEMINI", "#3186FF", gemini_art(P)),
        ("openai", "CH 03 · OPENAI", P["cyan"], openai_art(P)),
        ("claude", "CH 04 · CLAUDE 403", "#D97757", claude_art(P)),
    ]
    parts = [
        _box(x, y, w, h, P["panel"], 8, P["border"]),
        f'<path d="M{x+10} {y+1}h-4a5 5 0 0 0-5 5v4 M{x+w-10} {y+1}h4a5 5 0 0 1 5 5v4" fill="none" stroke="{P["muted"]}" stroke-opacity="0.35" stroke-width="1"/>',
        "<defs>",
        # Official Google Gemini 4-color gradients (in 24x24 icon userSpace)
        '<linearGradient id="gem-g0" gradientUnits="userSpaceOnUse" x1="7" x2="11" y1="15.5" y2="12">'
        '<stop stop-color="#08B962"/><stop offset="1" stop-color="#08B962" stop-opacity="0"/></linearGradient>',
        '<linearGradient id="gem-g1" gradientUnits="userSpaceOnUse" x1="8" x2="11.5" y1="5.5" y2="11">'
        '<stop stop-color="#F94543"/><stop offset="1" stop-color="#F94543" stop-opacity="0"/></linearGradient>',
        '<linearGradient id="gem-g2" gradientUnits="userSpaceOnUse" x1="3.5" x2="17.5" y1="13.5" y2="12">'
        '<stop stop-color="#FABC12"/><stop offset=".46" stop-color="#FABC12" stop-opacity="0"/></linearGradient>',
        '<clipPath id="claude-tear-a"><rect x="0" y="42" width="190" height="10"/></clipPath>',
        '<clipPath id="claude-tear-b"><rect x="0" y="82" width="190" height="8"/></clipPath>',
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
