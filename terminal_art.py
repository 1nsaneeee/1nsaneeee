"""Render the profile's Oh My Zsh terminal cards (Dark & Light) and README.md."""
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
from math import cos, pi, sin
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote

from ai_icons import PORTRAIT_CSS, build_mascot
from themes import THEMES

OWNER = "1nsaneeee"
PROFILE = f"https://github.com/{OWNER}"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{OWNER}/main"
FONT = "'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,monospace"

W = 860
MARGIN = 8
TITLE_H = 34


def tx(x, y, value, size=14, color="#e6edf3", extra=""):
    return (
        f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{color}" {extra}>'
        f"{escape(str(value))}</text>"
    )


def box(x, y, w, h, fill, radius=0, stroke=None):
    edge = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius}" fill="{fill}"{edge}/>'


def rule(x1, x2, y, color):
    return f'<path d="M{x1:g} {y:g}H{x2:g}" stroke="{color}"/>'


def cells(text):
    return sum(
        0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in "WF" else 1
        for c in text
    )


def text_px(text, size):
    """Estimate rendered monospace width in px (CJK ~1.0em, ASCII ~0.6em)."""
    total = 0.0
    for c in text:
        if unicodedata.combining(c):
            continue
        if unicodedata.east_asian_width(c) in "WF":
            total += size * 1.0
        else:
            total += size * 0.605
    return total


def shorten(text, limit):
    if cells(text) <= limit:
        return text
    used = 0
    for index, char in enumerate(text):
        used += cells(char)
        if used > limit - 1:
            return text[:index].rstrip() + "…"
    return text


def omz_card(P, title, desc, body_h, body, cmd_title, right_tag="", css=""):
    """Wrap content in a unified Oh My Zsh macOS-style terminal window with soft shadow."""
    wx, wy = MARGIN, MARGIN
    ww = W - 2 * MARGIN
    wh = TITLE_H + body_h
    H = wh + 2 * MARGIN
    shadow = (
        f'<defs><filter id="win-shadow" x="-4%" y="-6%" width="108%" height="118%">'
        f'<feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="{P["shadow"]}" '
        f'flood-opacity="{P["shadow_op"]}"/></filter></defs>'
    )
    frame = "".join([
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="11" fill="{P["bg"]}" filter="url(#win-shadow)"/>',
        f'<path d="M{wx},{wy + TITLE_H} V{wy + 11} a11,11 0 0 1 11,-11 H{wx + ww - 11} '
        f'a11,11 0 0 1 11,11 V{wy + TITLE_H} Z" fill="{P["mantle"]}"/>',
        rule(wx, wx + ww, wy + TITLE_H + 0.5, P["border"]),
        f'<rect x="{wx + .5}" y="{wy + .5}" width="{ww - 1}" height="{wh - 1}" rx="10.5" '
        f'fill="none" stroke="{P["border"]}"/>',
        # Traffic-light dots
        f'<circle cx="{wx + 20}" cy="{wy + TITLE_H / 2:g}" r="5.3" fill="{P["dot_r"]}"/>',
        f'<circle cx="{wx + 38}" cy="{wy + TITLE_H / 2:g}" r="5.3" fill="{P["dot_y"]}"/>',
        f'<circle cx="{wx + 56}" cy="{wy + TITLE_H / 2:g}" r="5.3" fill="{P["dot_g"]}"/>',
        # Centered window title + optional right tag
        tx(W / 2, wy + 21.5, cmd_title, 12.5, P["muted"], 'text-anchor="middle"'),
        tx(wx + ww - 18, wy + 21, right_tag, 11, P["dim"], 'text-anchor="end"') if right_tag else "",
    ])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
        f"<style>text{{font-family:{FONT}}}.bold{{font-weight:700}}.dim{{font-style:italic}}"
        f"a:hover text{{text-decoration:underline}}{css}</style>"
        f"{shadow}{frame}"
        f'<g transform="translate(0 {wy + TITLE_H})">{"".join(body)}</g>'
        f"</svg>\n"
    )


# ----------------------------------------------------------------- 1. BANNER

GLYPHS = {
    "1": ("00110", "01110", "00110", "00110", "00110", "00110", "11111"),
    "n": ("00000", "00000", "11010", "11111", "11011", "11011", "11011"),
    "s": ("00000", "00000", "01111", "11000", "01110", "00011", "11110"),
    "a": ("00000", "00000", "01110", "00011", "01111", "11011", "01111"),
    "e": ("00000", "00000", "01110", "11011", "11111", "11000", "01111"),
}


def signature(P):
    runs = []
    for i, char in enumerate(OWNER):
        for j, row in enumerate(GLYPHS[char]):
            for run in re.finditer("1+", row):
                n = len(run[0])
                runs.append(f"M{6 * i + run.start()} {j}h{n}v1h-{n}z")
    return (
        '<defs><path id="name" d="' + "".join(runs) + '"/>'
        f'<linearGradient id="ink" x2="0" y2="1"><stop stop-color="{P["mint"]}"/>'
        f'<stop offset="1" stop-color="{P["cyan"]}"/></linearGradient>'
        '<pattern id="scan" width="1" height=".5" patternUnits="userSpaceOnUse">'
        f'<path d="M0 .46H1" stroke="{P["scan_stroke"]}" stroke-opacity="{P["scan_op"]}" stroke-width=".08"/></pattern>'
        '<clipPath id="face"><use href="#name"/></clipPath>'
        '<linearGradient id="glint"><stop stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".54" stop-color="#fff" stop-opacity=".5"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
        '<g aria-label="1nsaneeee" transform="translate(177.5 52) scale(9.36) matrix(1 0 -.24 1 1.68 0)">'
        f'<use href="#name" fill="{P["word_shadow"]}" transform="translate(.36 .44)"/>'
        '<use href="#name" fill="url(#ink)"/><use href="#name" fill="url(#scan)"/>'
        '<g clip-path="url(#face)"><path class="glint" fill="url(#glint)" d="M-8 0h7l-2 7h-7z"/></g></g>'
    )


def tip_pages(config):
    pages = []
    for line in config.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        while cells(line) > 74:
            width = last_break = 0
            for i, char in enumerate(line):
                width += cells(char)
                if width > 74:
                    break
                if char.isspace() or char in "，。！？；、,;.!?":
                    last_break = i + 1
            split = last_break if last_break >= i // 2 else i
            pages.append(line[:split].rstrip())
            line = line[split:].lstrip()
        if line:
            pages.append(line)
    return pages


def loading_tips(tips, P):
    height = 28
    body = [
        f'<svg x="30" y="10" width="800" height="{height}" overflow="hidden">'
        f'<g class="{"tip-reel" if len(tips) > 1 else "single-tip"}" '
        f'style="--pages:{len(tips)};--cycle:{len(tips) * 6}s;--travel:-{len(tips) * height}px">'
    ]
    for i, tip in enumerate(tips):
        body.append(
            f'<text x="400" y="{i * height + 19}" text-anchor="middle" font-size="13.5">'
            f'<tspan fill="{P["gold"]}" class="bold">TIP › </tspan>'
            f'<tspan fill="{P["text"]}">{escape(tip)}</tspan></text>'
        )
    return "".join(body) + "</g></svg>"


def banner(data, P):
    day = data["end"][:10]
    tips = tip_pages(Path(__file__).with_name("coldjokeconfig").read_text(encoding="utf-8-sig"))
    offset = 32 if tips else 0
    body = []
    if tips:
        body.append(loading_tips(tips, P))

    body.extend([f'<g transform="translate(0 {offset})">', signature(P)])
    stars = [
        (68, 86, 1.25), (137, 56, 0.65), (150, 126, 0.85),
        (679, 50, 0.70), (705, 114, 1.10), (806, 106, 0.72),
    ]
    for i, (x, y, s) in enumerate(stars):
        color = (P["cyan"], P["mint"], P["gold"])[i % 3]
        body.append(
            f'<g transform="translate({x} {y}) scale({s})"><path class="star" '
            f'style="animation-delay:-{i * .61:.2f}s" fill="{color}" '
            'd="M-1 -5h2v3h1v1h3v2H2v1H1v3h-2V2h-1V1h-3v-2h3v-1h1z"/></g>'
        )

    cat = (
        tx(0, 0, r"/\_/\ ", 15, P["cyan"])
        + tx(-8, 15, "( o.o )", 15, P["text"], 'class="eyes"')
        + tx(-8, 15, "( -.- )", 15, P["text"], 'class="lid"')
        + tx(-6, 30, "/", 14, P["mint"])
        + '<g class="paw">' + tx(9, 30, ">o", 13, P["mint"]) + "</g>"
        + '<g class="mote">' + tx(33, 29, "✦", 12, P["gold"]) + "</g>"
    )
    body.extend([
        f'<g transform="translate(734 68)">{cat}</g>',
        tx(430, 144, "写点工具，也做游戏 · AI Agents · MC Modding · FGO Math", 15, P["text"], 'text-anchor="middle"'),
        rule(28, 832, 162.5, P["border"]),
    ])

    # Oh My Zsh robbyrussell prompt cycling 3 commands (18s loop = 6s each)
    cmds = [
        ("cat ~/.plan", "给 Minecraft 写模组，给 AI 造身体，给 FGO 算伤害。"),
        ("echo $FOCUS", "AI Agents (MCP / Voice) · TypeScript · Java · Python · C#"),
        ("whoami --vibe", "Tom Chou · 科技水槽包玩家 · 迦勒底御主 · 咖啡因驱动"),
    ]
    py = 188
    # Static OMZ prompt prefix: ➜  ~ git:(main) ✗
    body.extend([
        tx(28, py, "➜", 14.5, P["mint"], 'class="bold"'),
        tx(48, py, "~", 14, P["cyan"], 'class="bold"'),
        tx(66, py, "git:(", 13.5, P["blue"], 'class="bold"'),
        tx(108, py, "main", 13.5, P["red"], 'class="bold"'),
        tx(141, py, ")", 13.5, P["blue"], 'class="bold"'),
        tx(155, py, "✗", 13.5, P["gold"], 'class="bold"'),
    ])
    cmd_x = 176
    for i, (cmd, out) in enumerate(cmds):
        cw = round(text_px(cmd, 14.5) + 4)
        offset_s = 6 * i - 18 if i else 0
        body.append(
            f'<g class="cmd-slot{" cmd-first" if i == 0 else ""}" style="--co:{offset_s}s">'
            f'<defs><clipPath id="cp-{i}"><rect class="cmd-reveal" style="--co:{offset_s}s" x="0" y="-17" width="{cw}" height="24"/></clipPath></defs>'
            f'<g transform="translate({cmd_x} {py})">'
            f'<g clip-path="url(#cp-{i})">'
            + tx(0, 0, cmd, 14.5, P["text"])
            + "</g>"
            f'<g class="cmd-caret" style="--co:{offset_s}s;--cx:{cw}px">'
            f'<rect x="2" y="-12" width="8" height="15" rx="1" fill="{P["mint"]}" class="blink"/></g>'
            "</g>"
            + tx(28, py + 25, out, 14, P["muted"], f'class="cmd-out" style="--co:{offset_s}s"')
            + "</g>"
        )
    body.append("</g>")

    css = """
.lid,.glint,.cmd-slot{opacity:0}.cmd-first{opacity:1}
.cmd-caret{transform:translateX(var(--cx))}
@media(prefers-reduced-motion:no-preference){
  .tip-reel{animation:tips var(--cycle) steps(var(--pages),end) infinite}
  .tip-reel text{animation:tip-arrives 6s ease-out infinite}
  .eyes{animation:eyes 4.4s step-end infinite}.lid{animation:lid 4.4s step-end infinite}
  .star{animation:twinkle 3.8s ease-in-out infinite}.glint{animation:shine 7.6s ease-in-out 1.5s infinite}
  .paw{animation:reach 4.4s ease-in-out infinite}.mote{animation:dodge 4.4s ease-in-out infinite}
  .blink{animation:blink 1.05s steps(1,end) infinite}
  .cmd-slot{animation:slot-vis 18s linear var(--co) infinite}
  .cmd-reveal{animation:cmd-type 18s steps(14,end) var(--co) infinite}
  .cmd-caret{animation:caret-move 18s steps(14,end) var(--co) infinite}
  .cmd-out{animation:out-pop 18s ease-out var(--co) infinite}
}
@keyframes tips{from{transform:translateY(0)}to{transform:translateY(var(--travel))}}
@keyframes tip-arrives{0%{opacity:.35;transform:translateY(2px)}7%,93%{opacity:1;transform:translateY(0)}100%{opacity:.35}}
@keyframes eyes{0%,96%{opacity:1}92%{opacity:0}}@keyframes lid{0%,96%{opacity:0}92%{opacity:1}}
@keyframes reach{0%,61%,85%,100%{transform:translateX(0)}73%{transform:translate(7px,-2px)}}
@keyframes dodge{0%,69%,92%,100%{transform:translate(0,0)}79%{transform:translate(5px,-4px)}}
@keyframes twinkle{0%,55%,100%{opacity:.35}70%{opacity:1}}
@keyframes shine{0%{opacity:1;transform:translateX(66px)}25%{opacity:1;transform:translateX(-2px)}26%,100%{opacity:0;transform:translateX(-2px)}}
@keyframes blink{50%{opacity:0}}
@keyframes slot-vis{0%,32%{opacity:1}33.3%,99.5%{opacity:0}100%{opacity:1}}
@keyframes cmd-type{0%{transform:scaleX(0)}6.5%,33.3%,100%{transform:scaleX(1)}}
@keyframes caret-move{0%{transform:translateX(0)}6.5%,33.3%,100%{transform:translateX(var(--cx))}}
@keyframes out-pop{0%,6.5%{opacity:0;transform:translateY(2px)}9%,32%{opacity:1;transform:translateY(0)}33.3%,100%{opacity:0}}
"""
    return omz_card(
        P,
        f"{OWNER} · zsh",
        f"写点工具，也做游戏 · AI Agents · MC Modding · FGO Math. Last login {day}.",
        228 + offset,
        body,
        f"{OWNER}@github: ~ — zsh",
        f"Last login: {day}",
        css,
    )


# ----------------------------------------------------------------- 2. BADGES

def badge_svg(P, slug, left, right, tone):
    """Compact dual-theme terminal-style SVG pill badge (height=28)."""
    accent = P[tone]
    rbg = P[f"pill_{tone}_bg"]
    rbd = P[f"pill_{tone}_bd"]
    lw = round(text_px(left, 11.5) + 24)
    rw = round(text_px(right, 11.5) + 20)
    w = lw + rw
    h = 28
    cid = f"bclip-{slug}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{escape(left)}: {escape(right)}">'
        f"<style>text{{font-family:{FONT}}}.bold{{font-weight:700}}</style>"
        f'<clipPath id="{cid}"><rect width="{w}" height="{h}" rx="6"/></clipPath>'
        f'<g clip-path="url(#{cid})">'
        f'<rect width="{lw}" height="{h}" fill="{P["mantle"]}"/>'
        f'<rect x="{lw}" width="{rw}" height="{h}" fill="{rbg}"/>'
        f"</g>"
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="5.5" fill="none" stroke="{rbd}"/>'
        f'<path d="M{lw}.5 1V{h - 1}" stroke="{rbd}"/>'
        f'<circle cx="11" cy="{h / 2:g}" r="3.2" fill="{accent}"/>'
        f'<text x="19" y="18" font-size="11.5" fill="{P["muted"]}">{escape(left)}</text>'
        f'<text x="{lw + rw / 2:g}" y="18" font-size="11.5" fill="{accent}" text-anchor="middle" class="bold">{escape(right)}</text>'
        f"</svg>\n"
    )


# ----------------------------------------------------------------- 3. NEOFETCH

def spinner(x, y, P):
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    parts = []
    coords = [(2, 2), (2, 5), (2, 8), (5, 2), (5, 5), (5, 8), (2, 11), (5, 11)]
    for i, ch in enumerate(frames):
        dots = "".join(
            f'<circle cx="{cx}" cy="{cy + 14 * i}" r="1.3"/>'
            for b, (cx, cy) in enumerate(coords)
            if (ord(ch) - 0x2800) & (1 << b)
        )
        parts.append(dots)
    return (
        f'<svg x="{x}" y="{y - 12}" width="8" height="14" viewBox="0 0 8 14" overflow="hidden">'
        f'<g fill="{P["mint"]}" class="spinner">{"".join(parts)}</g></svg>'
    )


def languages_bar(totals, P, x=322, y=248, w=504):
    entries = sorted(((name, n) for name, n in totals.items() if n > 0), key=lambda item: (-item[1], item[0]))
    total = sum(n for _, n in entries)
    palette = (P["mint"], P["cyan"], P["gold"], P["mauve"], P["muted"])
    parts = [box(x, y, w, 7.5, P["subtle"], 3.75)]
    if total:
        segments = entries[:4]
        if len(entries) > 4:
            segments.append(("Other", sum(n for _, n in entries[4:])))
        parts.append(f'<defs><clipPath id="langs">{box(x, y, w, 7.5, "#fff", 3.75)}</clipPath></defs><g clip-path="url(#langs)">')
        pos = x
        labels = []
        for (name, n), color in zip(segments, palette):
            width = w * n / total
            parts.append(box(pos, y, width, 7.5, color))
            pos += width
            labels.append(f"{shorten(name, 11)} {100 * n / total:.0f}%")
        parts.append("</g>")
        caption = " · ".join(labels)
    else:
        caption = "Languages: —"
    parts.append(tx(x, y + 26, shorten(caption, 64), 11, P["muted"]))
    swatches = (P["mint"], P["cyan"], P["gold"], P["mauve"], P["red"], P["text"])
    for i, color in enumerate(swatches):
        parts.append(box(742 + i * 14, y + 16, 10, 10, color, 2))
    return "".join(parts)


def neofetch(data, P):
    end = datetime.fromisoformat(data["end"])
    created = data.get("created_at")
    uptime = f"{max(0, (end - datetime.fromisoformat(created.replace('Z', '+00:00'))).days)} days" if created else "—"
    repos = sum(not repo.get("private", False) for repo in data["repositories"]) if "repositories" in data else data["owned"]
    fields = [
        ("user", "1nsaneeee · Tom Chou", P["text"]),
        ("role", "Toolmaker · AI Agent & Game Builder", P["text"]),
        ("stack", "TypeScript · Java · Python · C#", P["text"]),
        ("uptime", f"{uptime}  ·  {repos} public repos · {len(data['commits'])} commits", P["gold"]),
        ("gemini", "● active (thinking) · AIza-CaffeineOrCoke", P["mint"]),
        ("openai", "● active (coding) · sk-FightingWithKubejs", P["cyan"]),
        ("claude", "× failed (403 banned) · said-hi-and-got-banned", P["red"]),
        ("thought", "> 403 on claude, falling back to gemini & caffeine.", P["muted"]),
    ]
    body = [build_mascot(P, x=24, y=22, w=268, h=242)]
    for i, (key, value, color) in enumerate(fields):
        y = 38 + i * 24.5
        body.append(tx(322, y, key, 13.5, P["cyan"], 'class="bold"'))
        body.append(tx(402, y, value, 12.8 if key == "thought" else 13.5, color, 'class="dim"' if key == "thought" else ""))
        if key == "gemini":
            body.append(spinner(382, y, P))
    body.append(languages_bar(data.get("language_bytes", {}), P, x=322, y=236, w=504))
    css = (
        "@media(prefers-reduced-motion:no-preference){.spinner{animation:spin 1.25s steps(10,end) infinite}}"
        "@keyframes spin{to{transform:translateY(-140px)}}"
        + PORTRAIT_CSS
    )
    desc = "; ".join(f"{k}: {v}" for k, v, _ in fields)
    return omz_card(
        P,
        "neofetch · AI agents",
        desc + "; MEOW, Gemini, OpenAI, Claude.",
        282,
        body,
        "neofetch --config ~/.config/ai-agents.conf",
        "4 channels",
        css,
    )


# ----------------------------------------------------------------- 4. SKILLS

def skills_card(P):
    """ls -l ~/skills — clean developer capability snapshot."""
    groups = [
        ("drwxr-xr-x", "languages/", "mint", ["TypeScript", "JavaScript", "Java", "Python", "C#"]),
        ("drwxr-xr-x", "ai_agents/", "cyan", ["MCP Protocol", "Voice Pipeline", "Agent Skills", "LLM Tooling"]),
        ("drwxr-xr-x", "game_dev/", "gold", ["Minecraft / NeoForge", "KubeJS", "FTB Quests", "Unity 2D"]),
        ("drwxr-xr-x", "workflow/", "mauve", ["VS Code Ext", "Node.js CLI", "GitHub Actions", "SVG Animation"]),
    ]
    body = [
        tx(28, 30, "➜", 14, P["mint"], 'class="bold"'),
        tx(48, 30, "~/skills", 13.5, P["cyan"], 'class="bold"'),
        tx(120, 30, "ls -la", 13.5, P["text"]),
        tx(830, 30, "total 4 directories", 11.5, P["dim"], 'text-anchor="end"'),
        rule(28, 832, 43.5, P["border"]),
    ]
    for row_i, (perm, dirname, tone, tags) in enumerate(groups):
        y = 72 + row_i * 38
        accent = P[tone]
        pbg = P[f"pill_{tone}_bg"]
        pbd = P[f"pill_{tone}_bd"]
        body.append(tx(28, y, perm, 12, P["dim"]))
        body.append(tx(114, y, dirname, 13.5, accent, 'class="bold"'))
        cx = 224
        for tag in tags:
            tw = round(text_px(tag, 12) + 20)
            body.append(box(cx, y - 16, tw, 24, pbg, 5, pbd))
            body.append(tx(cx + tw / 2, y, tag, 12, accent, 'text-anchor="middle"'))
            cx += tw + 8
    return omz_card(
        P,
        "ls -la ~/skills",
        "Languages: TypeScript, JavaScript, Java, Python, C#. AI Agents, Game Dev, and Tooling.",
        214,
        body,
        "ls -la ~/skills",
        "TOOLKIT",
    )


# ----------------------------------------------------------------- 5. CHALDEAS (FGO)

SABER_INKS = (
    ("A", "#f9eed7", ":"), ("B", "#f8e1c4", "-"), ("C", "#f8daaf", "="), ("D", "#fad298", "#"),
    ("E", "#fece8d", "/"), ("F", "#f7c484", "\\"), ("G", "#ebd8bf", ":"), ("H", "#ebc89b", "#"),
    ("I", "#eabb83", "/"), ("J", "#e0c5aa", ":"), ("K", "#c8c5ce", "."), ("L", "#e6af6f", "#"),
    ("M", "#ddaf7c", "/"), ("N", "#e0a869", "\\"), ("O", "#dca465", "="), ("P", "#d5a677", "#"),
    ("Q", "#bba79f", "-"), ("R", "#d09c6d", "\\"), ("S", "#cc9562", "="), ("T", "#b69684", "-"),
    ("U", "#b28767", "/"), ("V", "#836358", ":"), ("W", "#265e57", "o"), ("X", "#419287", "o"),
    ("Y", "#7cd6c4", "o"), ("Z", "#343136", "="), ("0", "#f2f1e5", "."),
)
SABER_ROWS = (
    "  DDPHCHMMPHCHHPHCDMRRRRRRPRRRRH",
    "  CCPPHGPJJIHPRPDDDDPPPRPRPPRRRHHDCAH",
    "   HJ00BRPHHHRRMDDCDPPMPPMMMPRRPBADFGJ",
    "   00AIPRPPPRMPPMDCDPIIMPMIMPRSSIICCHJ",
    "  00 PPSRPPRRRPMMICCIIIIMHIPPPSLLHHLCHC",
    "  00 TPRRRMRPPPPIMCCCDDDIIMMRSOLLLIGFCEC",
    " 0B  ISRSUPPPRMMPDCCCDHIIHMSSSONLONLBCBFJ",
    " A   GPUUURPPPMHDDDDHDDDMSSSONNOONONLAACJ",
    "AJ    JUUSRPMMIIIHDDHDPSSSSONONLOOOPINAAIH",
    "BQ    KMUUSRPPMIDDIMRSSSONNONLONILOOIINBAIC",
    "H      JRURRPPPRSSSSSOONNNLLONIONILOOCMNBAD",
    "Q      HAHPUSSSUSOOOLNNNNLNLLOLIONMIONASOCBM",
    "T     KDAHRLOOLSNNLNLLNNNLLNFLOFLONMIOHJSSIG",
    "      JAHHOINNISLNFNLFLLLLFILFNLFNOOILOAHIRNH",
    "      HAIONLLLINLNFLLEFEFLEEFIFNFFOOSIOHHGHM",
    "     KBDIOLLLIMLFNEFLEFFEEFEEFFLIFIOSSLOGLBIH",
    "     Q0LMOILLFMLELFFFEEFFEEEEEFENFFLOUNOJSHCMQ",
    "     JANMOFNIEPNEIFFFEEEIEEEEEEELLFFOSSLMPOGJQ",
    "     GBOLNFSFEPOEELFFEEEFFEEEIEEFSFFLSSSOQOICQQ",
    "     GCNLLFSEEPSEELEFEDDDPDDEREEESLFFOUSSPSOCJQ",
    "    KGHMLLFSFEPSEDFEDDDDDIMDDIREEPUFFLUSSRSSICQQ",
    "    KGHMLLFUFEPUFDDFDDDDDDUEDDSMEIUSFFUSOSSSOBJQ",
    "    KJHMILFUIEPRMDHEDDDDDDPRDDPRMFUSSFSSOOSOSIGKK",
    "    KMHSHNFUOEPPRDIDEDDDDIIPPEPRRMUUOUUSOOOOPOAKG",
    "    KPMSJOFSSEMRRDDRDDDDDMDPUTMUVVVUSUUUOONNNRCB0G",
    "    KPPSJOISUFIRPPDRIEDDDIPTJUVZVQVUSOUSSOLLOMMG00J",
    "    KLQSRILRRUIUURIMPIEEDPQPUUZZZQUSSFUSUONIOHSAG0K",
    "    JLJSSJLPPSMUPTUIMMIEEEGUJUWZWVTPSFSSSSNILMPGG00G",
    "    JLBTOUISRVTTZVTPMHMIEEJTG0XXXTPISESSSSNILOJM0G0K",
    "   KML JOUSRUSQJVZVQTHHJIIHGGGVXVJPHSEOUSSLFIOJUAJGG",
    "   QGO ANSVSVRT0QWXTHIHGGGJBBBJJBGMHRFNVSSLEFOJVT0UG",
    "   KGS  IOUUVVMAQXYTHPHGBBBBBBBBBBMHPINVVONEFOHVVQGK",
    "   KG   HNUUSVTMAVUJHPHGBBBBBBBBBBMIPINKVOPEENCVVVQQ",
    "   QG   IMOUUPVJHJJCJPCGBBBBBBBBBBJMUIL0TUPEELBVV 0K",
    "   KK    INSSUPTJJGGGJGBBBBBBBBBBGJSVIP KVPDDIA0000K",
    "    K    ILLSSKTJJCGGGGBBBBBBBBBBGHUVIP  TPDDHG00KKK",
    "    K0    FLLOKKQGGGBBBBBBBBGBBBBJUUVDQ  KPDDGJKK00K",
    "    KG     FLLTKKKQBGGBGJBBBBBBBJVVVVDQ  0PDDGTKKKKQ",
    "     K0    FEFMQKKKQGGGGBBBABBBJVUUVVMT  KTFDKTQQQKQ",
    "     QA     EDDMKKKKKQGGGBBBBBJVUVVVVUVTQQTPDQKQQKKT",
    "      K      EDCJ00KKKJQJBBBGUVUSONUUUUVQQTQPKKKKKKQ",
    "              HCCQQQQKQQTUJMUURLFFOVVUVVQQQQQK0KKKKK",
    "                CTQQQQQQTUUUTQQQQTZZZUUVQKKKKK000KKQ",
    "                 MQTTTTTQ000000KQKVZZVTQQK00KK00",
    "                 GQVTQVQK          ZZZQKK0000",
    "                   WTT               VQKK0",
)
SABER_LID_Y = 24
SABER_LIDS = (
    "                               HHJT",
    "                             PJBBGJ",
    "                           MJBBBJVT",
    "             R R           M BJTVJP",
    "            PQQGJ          QVVVTJB",
    "             VUGBG           BBBBG",
    "             PVTGBJ           BB",
    "              HTVVQJ",
    "               JGJJ",
)


def _portrait_strokes(rows, code):
    return "".join(
        f"M{run.start()} {y}h{len(run[0])}"
        for y, row in enumerate(rows)
        for run in re.finditer(code + "+", row)
    )


def artoria():
    defs = []
    glyph_ids = {}
    layers = [([], []), ([], [])]
    for code, color, glyph in SABER_INKS:
        if glyph not in glyph_ids:
            tile = "saber-glyph-" + str(len(glyph_ids))
            glyph_ids[glyph] = tile
            defs.append(
                f'<pattern id="{tile}" patternUnits="userSpaceOnUse" width="1.6" height="1.6" '
                'viewBox="0 0 6 7" preserveAspectRatio="none">'
                + tx(0, 6, glyph, 7, "#3c2f29", 'font-weight="700" opacity=".32"')
                + "</pattern>"
            )
        for i, rows in enumerate((SABER_ROWS, SABER_LIDS)):
            strokes = _portrait_strokes(rows, code)
            if not strokes:
                continue
            ink = "saber-" + str(i) + code
            defs.append(f'<path id="{ink}" d="{strokes}"/>')
            base, letters = layers[i]
            base.append(f'<use href="#{ink}" stroke="{color}"/>')
            letters.append(f'<use href="#{ink}" stroke="url(#{glyph_ids[glyph]})"/>')
    painted = ['<g shape-rendering="crispEdges">' + "".join(base) + "</g>" + "".join(letters) for base, letters in layers]
    return (
        "<defs>" + "".join(defs) + '</defs><g transform="translate(0 3) scale(2.12 2.29)" '
        'fill="none" stroke-width="1.015">'
        + painted[0]
        + f'<g class="saber-lids" transform="translate(0 {SABER_LID_Y})">'
        + painted[1]
        + "</g></g>"
    )


def read_save(relative):
    lines = (Path(__file__).parent / relative).read_text(encoding="utf-8-sig").splitlines()
    title = next(line[2:].strip() for line in lines if line.startswith("# "))
    fields = {}
    for line in lines:
        if line.startswith("- ") and "：" in line:
            key, value = line[2:].split("：", 1)
            fields[key.strip()] = value.strip()
    return title, fields


GAME_MOTION = """
.saber-lids,.np-last,.np-full{opacity:0}
@media(prefers-reduced-motion:no-preference){
  .saber-lids{animation:saber-blink 8.8s linear infinite}
  .np-last,.np-full{animation:charged 7.6s step-end infinite}
  .np-low{animation:charging 7.6s step-end infinite}
}
@keyframes saber-blink{0%,32%,35.8%,82%,85.8%,100%{opacity:0}33.3%,34.5%,83.3%,84.5%{opacity:1}}
@keyframes charged{0%,76%,100%{opacity:0}77%,96%{opacity:1}}
@keyframes charging{0%,76%,100%{opacity:1}77%,96%{opacity:0}}
"""


def chaldeas_card(data, P):
    relative = "chaldeas/AGENTS.md"
    title, profile = read_save(relative)
    joined = date.fromisoformat(profile["入坑日期"])
    elapsed = (date.fromisoformat(data["end"][:10]) - joined).days + 1
    body = [
        f'<path d="M24 18h156l10 10v152H33l-9-9z" fill="{P["fgo_card_bg"]}" stroke="{P["fgo_card_bd"]}"/>',
        f'<path d="M24 41V18h23m118 0h15l10 10v18m0 115v19h-22m-120 0H33l-9-9v-11" '
        f'fill="none" stroke="{P["fgo_accent"]}" stroke-width="1.5"/>',
        '<g transform="translate(29 21) scale(1.37)">' + artoria() + "</g>",
        f'<path d="M25 160h164v19H33l-8-8z" fill="{P["fgo_label_bg"]}"/>',
        tx(107, 174, "阿尔托莉雅 / SABER", 11, "#f2efe9", 'text-anchor="middle"'),
        tx(216, 36, "# " + shorten(title, 24), 14, P["fgo_accent"], 'class="bold"'),
        tx(216, 69, shorten(profile["最推从者"], 16), 26, P["text"], 'class="bold"'),
        tx(216, 89, "最推从者 · 看板娘是呆毛王", 12, P["muted"]),
        f'<g transform="translate(438 34)" fill="none" stroke="{P["fgo_accent"]}" stroke-width="1.5">'
        '<path d="M0 0q32 4 38 34L0 0l14 34z M1 29L33 2m-8 1 8-1-2 8"/></g>',
        rule(216, 502, 102.5, P["border"]),
        tx(216, 134, shorten(profile["御主等级"], 5), 26, P["gold"], 'class="bold"'),
        tx(354, 134, shorten(profile["五星从者"], 5), 26, P["gold"], 'class="bold"'),
        tx(217, 154, "御主等级", 12, P["muted"]),
        tx(354, 154, "五星从者 / 骑", 12, P["muted"]),
        tx(216, 179, f"{joined:%Y.%m.%d} " + shorten(profile["入坑备注"], 18), 13, P["text"]),
        f'<path d="M526 22v155" stroke="{P["fgo_divider"]}"/>',
        tx(550, 36, "NP / 宝具试算", 14, P["cyan"], 'class="bold"'),
        box(550, 51, 222, 8, P["fgo_bar_track"], 2),
        box(550, 51, 219.8, 8, P["fgo_bar_fill"], 2),
        f'<rect class="np-last" x="768" y="51" width="4" height="8" fill="{P["gold"]}"/>',
        tx(832, 60, "99%", 14, P["cyan"], 'class="np-low bold" text-anchor="end"'),
        tx(832, 60, "100%", 14, P["gold"], 'class="np-full bold" text-anchor="end"'),
        tx(550, 84, "伤害区间 · NP 回收 · 三回合连发", 13, P["muted"]),
        tx(550, 107, "1nsaneeee.github.io/fgo-np-calculator ↗", 11.5, P["cyan"]),
        rule(550, 834, 121.5, P["border"]),
        tx(550, 148, f"入坑第 {elapsed:,} 天", 16, P["gold"], 'class="bold"'),
        tx(550, 176, "# " + shorten(profile["吐槽"], 31), 12.5, P["muted"], 'class="dim"'),
    ]
    desc = f"{title}。最推 {profile['最推从者']}，御主 Lv.{profile['御主等级']}，五星从者 {profile['五星从者']} 骑。"
    return omz_card(P, title, desc, 200, body, "cat ~/chaldeas/AGENTS.md", "FGO / MASTER", GAME_MOTION)


# ----------------------------------------------------------------- 6. MINECRAFT

def _game_ink(P):
    is_light = P["name"] == "light"
    materials = [
        ("grass", P["mint"], 0.40 if is_light else 0.30, P["mint"], 'v,"', "'v;"),
        ("loam", "#b58b5b" if is_light else "#c8a377", 0.48 if is_light else 0.32, "#7f5b34" if is_light else "#cdab83", "+%:", "#.+"),
    ]
    parts = ["<defs>"]
    for name, base, opacity, ink, a, b in materials:
        glyphs = 'class="bold" xml:space="preserve" textLength="10.5" lengthAdjust="spacingAndGlyphs"'
        parts.append(
            f'<pattern id="ink-{name}" width="10.5" height="10" patternUnits="userSpaceOnUse">'
            f'<rect width="10.5" height="10" fill="{base}" opacity="{opacity}"/>'
            + tx(0, 4.6, a, 5.6, ink, glyphs)
            + tx(0, 9.6, b, 5.6, ink, glyphs)
            + "</pattern>"
        )
    return "".join(parts) + "</defs>"


def _cube_pose(angle):
    c, s = cos(angle), sin(angle)
    corners = [(55 + 65.05 * (x * c - z * s), 34.5 + 37.56 * (x * s + z * c)) for x, z in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
    px, py = corners[0]
    poses = [(True, ((corners[1][0] - px) / 100, (corners[1][1] - py) / 100, (corners[3][0] - px) / 100, (corners[3][1] - py) / 100, px, py))]
    for i, (end_x, end_y) in enumerate(corners):
        x, y = corners[(i + 1) % 4]
        poses.append((end_x > x + 0.001, ((end_x - x) / 100, (end_y - y) / 100, 0, 0.5312, x, y)))
    return poses


def grass_block(P):
    grass_pixels = '<path d="M3 9h13v7H3z M20 13h9v8h-9z M53 4h12v8H53z M72 27h10v9H72z M4 44h10v8H4z M31 58h16v9H31z M80 76h9v14h-9z M47 89h11v7H47z" fill="#20472c" opacity=".48"/>'
    dirt_pixels = '<path d="M3 37h11v7H3z M28 29h8v10h-8z M55 44h14v8H55z M81 37h11v6H81z M15 62h15v11H15z M42 73h9v6h-9z M73 86h14v8H73z M5 90h11v8H5z" fill="#654833" opacity=".55"/>'
    top = (
        box(0, 0, 100, 100, "url(#ink-grass)")
        + grass_pixels
        + '<path d="M9 16h6v3H9z M69 11h5v3h-5z M43 30h8v3h-8z M18 72h6v3h-6z M75 83h8v3h-8z" fill="#9ace83"/>'
    )
    fringe = "M0 0h100v15h-8v4h-8v-6h-9v10h-7v-8h-9v5h-9v-7h-9v13h-6v-8h-9v-5h-8v7h-9v-6H0z"
    side = (
        box(0, 0, 100, 100, "url(#ink-loam)")
        + dirt_pixels
        + f'<path d="{fringe}" fill="url(#ink-grass)" stroke="#568350" stroke-width=".95" stroke-linejoin="round"/>'
        + '<path d="M9 41h8v4H9z M46 70h6v4h-6z M78 54h9v3h-9z" fill="#9c7a53"/>'
    )
    parts = ['<defs><g id="block-top">' + top + '</g><g id="block-wall">' + side + "</g></defs>"]
    frames = 72
    poses = [_cube_pose(pi / 4 + 2 * pi * f / frames) for f in range(frames + 1)]
    css = []
    for face in range(5):
        keys = []
        hidden = False
        for f, pose in enumerate(poses):
            visible, matrix = pose[face]
            transform = "matrix(" + ",".join(f"{n:.3f}".rstrip("0").rstrip(".") for n in matrix) + ")"
            if f == 0:
                ref = "block-top" if face == 0 else "block-wall"
                parts.append(
                    f'<g class="cube-face-{face}" visibility="{"visible" if visible else "hidden"}" transform="{transform}">'
                    f'<use href="#{ref}"/>'
                )
                if face in (1, 3):
                    parts.append(f'<rect width="100" height="100" fill="{P["cube_shade"]}" opacity="{P["cube_shade_op"]}"/>')
                parts.append("</g>")
            if not visible and hidden and f != frames:
                continue
            style = f"visibility:visible;transform:{transform}" if visible else "visibility:hidden"
            keys.append(f"{100 * f / frames:.2f}%{{{style}}}")
            hidden = not visible
        css.append(
            f"@keyframes yaw-{face}{{{''.join(keys)}}}"
            f"@media(prefers-reduced-motion:no-preference){{.cube-face-{face}{{animation:yaw-{face} 6s step-end infinite}}}}"
        )
    return "<style>" + "".join(css) + "</style>" + "".join(parts)


def minecraft_card(P):
    relative = "Minecraft/SKILL.md"
    title, profile = read_save(relative)
    packs = [s.strip() for s in profile["整合包"].split("/") if s.strip()]
    mods = [s.strip() for s in profile["熟悉的模组"].split("/") if s.strip()]
    icons = {
        "Mekanism": ("M0 2h12v10H0z M3 5v4h6V5z", P["cyan"], "矿物处理"),
        "工业先锋": ("M0 5h3V2h3v3h3V1h3v11H0z", P["gold"], "工业自动化"),
        "资源蜜蜂": ("M1 2h3l3 2 2-2h3v3l-2 1v4H3V6L1 5z M5 6v3h1V6z", P["gold"], "资源生产"),
        "AE2": ("M1 0h10v12H1z M3 2v2h6V2z M3 6v2h6V6z", P["mint"], "ME 网络"),
    }
    parts = [
        _game_ink(P),
        '<g transform="translate(30 22) scale(1.34)">' + grass_block(P) + "</g>",
        tx(105, 188, "minecraft:grass_block", 11, P["muted"], 'text-anchor="middle"'),
        f'<path d="M194 20v168" stroke="{P["mc_divider"]}"/>',
        tx(218, 40, "# " + shorten(title, 33), 19, P["text"], 'class="bold"'),
        tx(218, 69, "PACKS", 11, P["muted"]),
    ]
    cursor = 266
    pack_y = 53
    for pack in packs:
        label = shorten(pack, 19)
        width = round(text_px(label, 12) + 20)
        if cursor + width > 834:
            cursor = 266
            pack_y += 28
        parts.extend([
            box(cursor, pack_y, width, 22, P["pill_mint_bg"], 4, P["pill_mint_bd"]),
            tx(cursor + width / 2, pack_y + 15, label, 12, P["mint"], 'text-anchor="middle"'),
        ])
        cursor += width + 8
    shift = pack_y - 53
    parts.extend([rule(218, 834, 87.5 + shift, P["border"]), tx(218, 108 + shift, "MODS", 11, P["muted"])])
    columns = 4
    rows = (len(mods) + columns - 1) // columns
    for i, mod in enumerate(mods):
        x = 218 + (i % columns) * 155
        y = 130 + (i // columns) * 48 + shift
        shape, color, caption = icons.get(mod, ("M0 0h10v10H0z", P["mint"], ""))
        parts.append(
            f'<g class="quest-entry" style="--wait:{i * .09:.2f}s">'
            f'<path transform="translate({x} {y - 11})" d="{shape}" fill="{color}" fill-rule="evenodd"/>'
            + tx(x + 20, y, shorten(mod, 16), 14, P["text"])
            + tx(x + 20, y + 18, caption, 11.5, P["muted"])
            + "</g>"
        )
    footer_y = 158 + shift + max(0, rows - 1) * 48
    parts.extend([
        rule(218, 834, footer_y, P["border"]),
        tx(218, footer_y + 24, "# " + shorten(profile["玩家笔记"], 36), 13, P["mint"], 'class="dim"'),
        tx(834, footer_y + 24, "~/agentinminecraft · ~/ftb-quests-preview ↗", 11.5, P["cyan"], 'text-anchor="end"'),
    ])
    css = (
        "@media(prefers-reduced-motion:no-preference){.quest-entry{animation:entry .35s ease-out var(--wait) backwards}}"
        "@keyframes entry{from{opacity:.75;transform:translateY(3px)}to{opacity:1;transform:translateY(0)}}"
    )
    return omz_card(
        P,
        title,
        "整合包：" + profile["整合包"] + "。模组：" + profile["熟悉的模组"] + "。" + profile["玩家笔记"],
        footer_y + 44,
        parts,
        "cat ~/Minecraft/SKILL.md",
        "MC / QUEST BOOK",
        css,
    )


# ----------------------------------------------------------------- 7. SHIPPED & FOOTER

def _age(value, end):
    secs = max(0, int((end - datetime.fromisoformat(value.replace("Z", "+00:00"))).total_seconds()))
    for scale, unit in ((86400, "d"), (3600, "h"), (60, "m")):
        if secs >= scale:
            return f"{secs // scale}{unit} ago"
    return "now"


def shipped_footer(data, P):
    """Recent real project commits (excluding profile meta-repo) + Oh My Zsh closing sign-off."""
    end = datetime.fromisoformat(data["end"])
    all_rows = data["commits"]
    # Prioritize real project commits over self-updates to the profile repo
    proj_rows = [r for r in all_rows if r["repo"].lower() != OWNER.lower()]
    recent = (proj_rows if proj_rows else all_rows)[:4]

    body = [
        tx(28, 30, "➜", 14, P["mint"], 'class="bold"'),
        tx(48, 30, "~/projects", 13.5, P["cyan"], 'class="bold"'),
        tx(136, 30, "git log --all -n 4 --oneline", 13.5, P["text"]),
        tx(830, 30, f"updated {end.strftime('%Y-%m-%d')}", 11, P["dim"], 'text-anchor="end"'),
        rule(28, 832, 43.5, P["border"]),
    ]

    tags = [shorten(r["repo"], 19) for r in recent]
    repo_px = max((text_px("[" + t + "]", 12.5) for t in tags), default=0)
    msg_x = 122 + repo_px + 14

    for i, (row, tag) in enumerate(zip(recent, tags)):
        y = 68 + i * 24
        dot_color = P["mint"] if i == 0 else P["dim"]
        max_cells = max(18, int((754 - msg_x) / 7.8))
        body.append(
            f'<circle cx="33" cy="{y - 4}" r="3.2" fill="{dot_color}"/>'
            + tx(48, y, row["sha"][:7], 13, P["mint"], 'class="bold"' if i == 0 else "")
            + tx(122, y, f"[{tag}]", 12.5, P["cyan"])
            + tx(msg_x, y, shorten(row["title"], max_cells), 13, P["text"])
            + tx(830, y, _age(row["time"], end), 12, P["muted"], 'text-anchor="end"')
        )
    if not recent:
        body.append(tx(48, 72, "(no public project commits yet)", 13, P["muted"]))

    foot_y = 162
    signoff = 'echo "Just do it — 欢迎提 Issue / PR，或聊聊 AI、MC 与 FGO"'
    sign_w = round(text_px(signoff, 13.5) + 4)
    body.extend([
        rule(28, 832, foot_y - 14, P["border"]),
        tx(28, foot_y + 10, "➜", 14, P["mint"], 'class="bold"'),
        tx(48, foot_y + 10, "~", 13.5, P["cyan"], 'class="bold"'),
        tx(68, foot_y + 10, signoff, 13.5, P["muted"]),
        f'<rect x="{68 + sign_w}" y="{foot_y - 2}" width="7.5" height="14" rx="1" fill="{P["mint"]}" class="blink"/>',
        box(768, foot_y - 6, 62, 22, P["pill_mint_bg"], 5, P["pill_mint_bd"]),
        tx(799, foot_y + 9, "exit 0", 11.5, P["mint"], 'text-anchor="middle" class="bold"'),
    ])
    css = "@media(prefers-reduced-motion:no-preference){.blink{animation:blink 1.05s steps(1,end) infinite}}@keyframes blink{50%{opacity:0}}"
    desc = "Recent project commits and terminal sign-off: " + "; ".join(f"{r['repo']}: {r['title']}" for r in recent)
    return omz_card(P, "git log · exit 0", desc, foot_y + 30, body, "git log --all · ~/projects", "HEAD", css)


# ----------------------------------------------------------------- RENDER ALL + README

BADGE_SPECS = [
    ("agentinminecraft", "AI × MC", "agentinminecraft", "mint", f"{PROFILE}/agentinminecraft"),
    ("openjarvis", "Voice AI", "OpenJarvis", "cyan", f"{PROFILE}/OpenJarvis"),
    ("fgo-demo", "Live Demo", "FGO 宝具计算器 ↗", "gold", "https://1nsaneeee.github.io/fgo-np-calculator/"),
    ("pixart-demo", "Live Demo", "PixArt 像素画 ↗", "mauve", "https://1nsaneeee.github.io/pixart-pixel-tool/"),
]


def _pic(rel_dark, rel_light, alt, extra='width="100%"'):
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="./{rel_dark}">\n'
        f'  <img alt="{escape(alt, quote=True)}" src="./{rel_light}" {extra}>\n'
        "</picture>"
    )


def render_terminal(data, assets, write):
    term_dir = Path(assets) / "terminal"
    badge_dir = Path(assets) / "badges"
    term_dir.mkdir(parents=True, exist_ok=True)
    badge_dir.mkdir(parents=True, exist_ok=True)

    for mode, P in THEMES.items():
        write(term_dir / f"banner-{mode}.svg", banner(data, P))
        write(term_dir / f"neofetch-{mode}.svg", neofetch(data, P))
        write(term_dir / f"skills-{mode}.svg", skills_card(P))
        write(term_dir / f"chaldeas-{mode}.svg", chaldeas_card(data, P))
        write(term_dir / f"minecraft-{mode}.svg", minecraft_card(P))
        write(term_dir / f"shipped-{mode}.svg", shipped_footer(data, P))
        for slug, left, right, tone, _ in BADGE_SPECS:
            write(badge_dir / f"badge-{slug}-{mode}.svg", badge_svg(P, slug, left, right, tone))

    badge_links = []
    for slug, left, right, _, href in BADGE_SPECS:
        pic = (
            f'<a href="{href}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="./assets/badges/badge-{slug}-dark.svg">'
            f'<img alt="{escape(left + ": " + right, quote=True)}" src="./assets/badges/badge-{slug}-light.svg" height="28" align="middle">'
            f"</picture></a>"
        )
        badge_links.append(pic)

    skill_icons = (
        "<picture>\n"
        '  <source media="(prefers-color-scheme: dark)" srcset="https://skillicons.dev/icons?i=ts%2Cjs%2Cjava%2Cpy%2Ccs%2Cunity%2Cnodejs%2Cvscode%2Cgit%2Cgithub&amp;theme=dark">\n'
        '  <img alt="TypeScript, JavaScript, Java, Python, C#, Unity, Node.js, VS Code, Git, GitHub" '
        'src="https://skillicons.dev/icons?i=ts,js,java,py,cs,unity,nodejs,vscode,git,github&amp;theme=light">\n'
        "</picture>"
    )

    readme = f"""<!--
  Oh My Zsh terminal profile for {OWNER}.
  Edit `coldjokeconfig`, `chaldeas/AGENTS.md`, or `Minecraft/SKILL.md` and push —
  GitHub Actions regenerates all Dark & Light SVG cards automatically.
-->

<div align="center">

{_pic("assets/terminal/banner-dark.svg", "assets/terminal/banner-light.svg", "1nsaneeee · Oh My Zsh Terminal Banner")}

<p align="center">
  {"&nbsp; ".join(badge_links)}
</p>

{_pic("assets/terminal/neofetch-dark.svg", "assets/terminal/neofetch-light.svg", "neofetch · Tom Chou & AI Agents")}

</div>

### `➜ ~/projects` · Featured Builds

| Project | What it does | Stack | Links |
| :--- | :--- | :--- | :--- |
| **[agentinminecraft]({PROFILE}/agentinminecraft)** | NeoForge 1.21.1 Mod：MCP（35 工具）+ WebSocket 桥接，给 AI Agent 一具能在 MC 里走路、挖矿、造世界、聊天的真实玩家身体 | `Java` `MCP` | [Repo]({PROFILE}/agentinminecraft) |
| **[OpenJarvis]({PROFILE}/OpenJarvis)** | 本地优先、模型无关的开源桌面语音 AI 助手框架（唤醒词 → ASR → LLM → MCP 工具执行） | `Python` `MCP` | [Repo]({PROFILE}/OpenJarvis) |
| **[ftb-quests-preview]({PROFILE}/ftb-quests-preview)** | 本地 FTB Quests 任务书可视化预览编辑器 + Headless CLI（节点拖拽、格式码补全、AI JSON Patch） | `JS` `CLI` | [Repo]({PROFILE}/ftb-quests-preview) |
| **[fgo-np-calculator]({PROFILE}/fgo-np-calculator)** | FGO 宝具伤害计算器 v2.0：伤害区间、NP 回收、三回合周回连发试算 | `JS` `Web` | [Repo]({PROFILE}/fgo-np-calculator) · [**Demo**](https://1nsaneeee.github.io/fgo-np-calculator/) |
| **[url-to-markdown]({PROFILE}/url-to-markdown)** | VS Code 扩展：输入网址智能提取正文（Readability）并转换为干净的 Markdown | `TS` `VS Code` | [Repo]({PROFILE}/url-to-markdown) |
| **[Programming-Carrier]({PROFILE}/Programming-Carrier)** | Unity 2D 类银河战士恶魔城 RPG 毕业设计（战斗、探索、技能系统） | `C#` `Unity` | [Repo]({PROFILE}/Programming-Carrier) |
| **[pixart-pixel-tool]({PROFILE}/pixart-pixel-tool)** | 24×24 像素画参照工具：图片转 40 色限定像素网格，零依赖单文件 | `JS` `Canvas` | [Repo]({PROFILE}/pixart-pixel-tool) · [**Demo**](https://1nsaneeee.github.io/pixart-pixel-tool/) |
| **[doc-router]({PROFILE}/doc-router)** | Agent Skill：Context7 + `llms.txt` 文档检索路由管线 | `PS1` `Skill` | [Repo]({PROFILE}/doc-router) |

<div align="center">

{_pic("assets/terminal/skills-dark.svg", "assets/terminal/skills-light.svg", "ls -la ~/skills")}

{skill_icons}

<br/>

<a href="https://1nsaneeee.github.io/fgo-np-calculator/">
{_pic("assets/terminal/chaldeas-dark.svg", "assets/terminal/chaldeas-light.svg", "迦勒底御主档案 · FGO Master File")}
</a>

<sub><code>cat ~/chaldeas/AGENTS.md</code> · <a href="./chaldeas/AGENTS.md">御主档案源文件</a> · <a href="https://1nsaneeee.github.io/fgo-np-calculator/">在线打开宝具计算器</a> · <a href="{PROFILE}/fgo-np-calculator">源码仓库</a></sub>

<br/><br/>

<a href="{PROFILE}/ftb-quests-preview">
{_pic("assets/terminal/minecraft-dark.svg", "assets/terminal/minecraft-light.svg", "Minecraft 科技水槽包任务手册")}
</a>

<sub><code>cat ~/Minecraft/SKILL.md</code> · <a href="./Minecraft/SKILL.md">任务手册源文件</a> · <a href="{PROFILE}/agentinminecraft">AI 进 MC 模组</a> · <a href="{PROFILE}/ftb-quests-preview">FTB 任务编辑器</a></sub>

<br/><br/>

{_pic("assets/terminal/shipped-dark.svg", "assets/terminal/shipped-light.svg", "Recent project commits & exit 0")}

</div>
"""
    return readme
