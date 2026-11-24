"""Render the profile's Oh My Zsh terminal cards (Dark & Light) and README.md."""
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
from math import cos, pi, sin
from pathlib import Path
import logging
import random
import re
import unicodedata
from urllib.parse import quote

from ai_icons import PORTRAIT_CSS, build_mascot
from themes import THEMES
from terminal_detail import (FATE_CSS, FORGE_CSS, SKILL_CSS, TREE_CSS,
                             fate_background, forge_background)

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


def omz_card(P, title, desc, body_h, body, cmd_title, right_tag="", css="", title_ink=None):
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
        f'a11,11 0 0 1 11,11 V{wy + TITLE_H} Z" fill="{title_ink or P["mantle"]}"/>',
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


TIP_PAGE_BUDGET = 24


def wrap_tip(line):
    pages = []
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


def tip_pages(config, page_budget=TIP_PAGE_BUDGET):
    blocks = []
    group = None
    for line in config.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "===":
            if group is None:
                group = []
                blocks.append(group)
            else:
                group = None
        elif group is None:
            blocks.append(wrap_tip(line))
        else:
            group.extend(wrap_tip(line))

    blocks = [block for block in blocks if block]
    if page_budget is not None:
        oversized = sum(len(block) > page_budget for block in blocks)
        if oversized:
            logging.getLogger(__name__).warning(
                "Skipping %d complete tip block(s) larger than the %d-page budget.", oversized, page_budget)
    random.shuffle(blocks)
    pages = []
    for block in blocks:
        if page_budget is not None and len(pages) + len(block) > page_budget:
            continue
        pages.extend(block)
    return pages


def read_tip_pages():
    return tip_pages(Path(__file__).with_name("coldjokeconfig").read_text(encoding="utf-8-sig"))


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


def banner(data, P, tips=None):
    day = data["end"][:10]
    if tips is None:
        tips = read_tip_pages()
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
        title_ink=P["terminal_title"],
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
    body = [_omz_prompt_row(P, "~/skills", "main", "ls -la", "total 4 directories")]
    for row_i, (perm, dirname, tone, tags) in enumerate(groups):
        y = 72 + row_i * 38
        accent = P[tone]
        pbg = P[f"pill_{tone}_bg"]
        pbd = P[f"pill_{tone}_bd"]
        body.append(tx(28, y, perm, 12, P["dim"], f'class="perm" style="--delay:{row_i*.12:.2f}s"'))
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
        SKILL_CSS,
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


def _omz_prompt_row(P, path, branch, cmd, right=""):
    """Shared Oh My Zsh prompt header line inside terminal windows (pixel-exact tspan spacing)."""
    line = (
        f'<text x="28" y="30" font-size="13.5">'
        f'<tspan fill="{P["mint"]}" class="bold">➜</tspan>'
        f'<tspan fill="{P["cyan"]}" class="bold">  {escape(path)} </tspan>'
        f'<tspan fill="{P["blue"]}" class="bold">git:(</tspan>'
        f'<tspan fill="{P["red"]}" class="bold">{escape(branch)}</tspan>'
        f'<tspan fill="{P["blue"]}" class="bold">)</tspan>'
        f'<tspan fill="{P["gold"]}" class="bold"> ✗ </tspan>'
        f'<tspan fill="{P["text"]}">{escape(cmd)}</tspan>'
        f"</text>"
    )
    parts = [line]
    if right:
        parts.append(tx(830, 30, right, 11, P["dim"], 'text-anchor="end"'))
    parts.append(rule(28, 832, 43.5, P["border"]))
    return "".join(parts)


# ----------------------------------------------------------------- 4b. FEATURED PROJECTS

FEATURED_PROJECTS = [
    ("agentinminecraft", "NeoForge 1.21.1 Mod：MCP + WebSocket 给 AI 一具 MC 实体", "Java · MCP", "mint", f"{PROFILE}/agentinminecraft", None),
    ("OpenJarvis", "本地优先、模型无关的开源桌面语音 AI 助手框架", "Python · MCP", "cyan", f"{PROFILE}/OpenJarvis", None),
    ("ftb-quests-preview", "本地 FTB Quests 任务书可视化预览编辑器 + Headless CLI", "JS · CLI", "mint", f"{PROFILE}/ftb-quests-preview", None),
    ("fgo-np-calculator", "FGO 宝具伤害计算器 v2.0：伤害区间、NP 回收、3T 连发试算", "JS · DEMO", "gold", f"{PROFILE}/fgo-np-calculator", "https://1nsaneeee.github.io/fgo-np-calculator/"),
    ("url-to-markdown", "VS Code 扩展：输入网址智能提取正文并转为干净 Markdown", "TS · VSCode", "cyan", f"{PROFILE}/url-to-markdown", None),
    ("Programming-Carrier", "Unity 2D 类银河战士恶魔城 RPG 毕业设计（战斗与探索）", "C# · Unity", "mauve", f"{PROFILE}/Programming-Carrier", None),
    ("pixart-pixel-tool", "24×24 像素画参照工具：图片转 40 色网格，零依赖单文件", "JS · DEMO", "mauve", f"{PROFILE}/pixart-pixel-tool", "https://1nsaneeee.github.io/pixart-pixel-tool/"),
    ("doc-router", "Agent Skill：Context7 + llms.txt 文档检索路由管线", "PS1 · Skill", "gold", f"{PROFILE}/doc-router", None),
]


def projects_card(P):
    """Dedicated Oh My Zsh terminal window for Featured Builds."""
    body = [_omz_prompt_row(P, "~/projects", "main", "tree -L 1 --featured", f"{len(FEATURED_PROJECTS)} builds")]
    n = len(FEATURED_PROJECTS)
    for i, (name, summary, tag, tone, _, _) in enumerate(FEATURED_PROJECTS):
        y = 70 + i * 30
        branch = "└──" if i == n - 1 else "├──"
        accent = P[tone]
        pbg = P[f"pill_{tone}_bg"]
        pbd = P[f"pill_{tone}_bd"]
        pw = round(text_px(tag, 11) + 18)
        px = 830 - pw
        body.extend([
            tx(28, y, branch, 13, P["dim"], f'class="tree-guide" style="--delay:{i*.35:.2f}s;color:{accent}"'),
            tx(60, y, name + "/", 13.2, accent, 'class="bold"'),
            tx(236, y, shorten(summary, 66), 12.5, P["muted"]),
            box(px, y - 14.5, pw, 20, pbg, 4, pbd),
            tx(px + pw / 2, y - 0.5, tag, 11, accent, 'text-anchor="middle" class="bold"'),
        ])
    body_h = 70 + n * 30 - 6
    desc = "Featured projects: " + ", ".join(p[0] for p in FEATURED_PROJECTS)
    return omz_card(P, "tree ~/projects --featured", desc, body_h, body, "tree -L 1 ~/projects --featured", "PROJECTS", TREE_CSS)


# ----------------------------------------------------------------- 5. CHALDEAS (FGO ZSH TUI)

def chaldeas_card(data, P):
    relative = "chaldeas/AGENTS.md"
    title, profile = read_save(relative)
    joined = date.fromisoformat(profile["入坑日期"])
    elapsed = (date.fromisoformat(data["end"][:10]) - joined).days + 1

    vx, vy, vw, vh = 28, 56, 206, 188
    viewport = [
        box(vx, vy, vw, vh, P["panel"], 8, P["border"]),
        f'<circle cx="{vx + 14}" cy="{vy + 16}" r="3" fill="{P["gold"]}"/>',
        tx(vx + 24, vy + 19.5, "SABER · ARTORIA", 10.5, P["gold"], 'class="bold"'),
        f'<defs><clipPath id="saber-window"><rect x="{vx+1}" y="{vy+1}" width="{vw-2}" height="{vh-2}" rx="7"/></clipPath></defs>',
        f'<g clip-path="url(#saber-window)"><g transform="translate({vx + 12} {vy + 22}) scale(1.62)">'
        + artoria() + "</g></g>",
    ]

    kx, vx_r = 258, 354
    np_y = 148
    bar_x = vx_r
    cells_svg = []
    for idx in range(20):
        cx = bar_x + idx * 12.5
        if idx < 19:
            cells_svg.append(box(cx, np_y - 11, 9.5, 13, P["cyan"], 1.5))
        else:
            cells_svg.append(box(cx, np_y - 11, 9.5, 13, P["subtle"], 1.5))
            cells_svg.append(f'<rect class="np-last" x="{cx:g}" y="{np_y - 11:g}" width="9.5" height="13" rx="1.5" fill="{P["gold"]}"/>')

    master = escape(shorten(profile.get("御主名", OWNER), 18))
    lv = escape(shorten(profile["御主等级"], 5))
    ssr = escape(shorten(profile["五星从者"], 5))
    fav = shorten(profile["最推从者"], 14)
    join_note = escape(shorten(profile["入坑备注"], 14))

    body = [
        _omz_prompt_row(P, "~/chaldeas", "master", "fgo-fetch --profile", "chaldea-os"),
        fate_background(P),
        *viewport,
        tx(kx, 76, "master", 13.5, P["cyan"], 'class="bold"'),
        f'<text x="{vx_r}" y="76" font-size="13.5">'
        f'<tspan fill="{P["fgo_master"]}" class="bold">{master}</tspan>'
        f'<tspan fill="{P["dim"]}"> · </tspan>'
        f'<tspan fill="{P["gold"]}" class="bold">Lv.{lv} · {ssr}★5</tspan></text>',
        tx(kx, 100, "favorite", 13.5, P["cyan"], 'class="bold"'),
        tx(vx_r, 100, fav, 13.5, P["text"], 'class="bold"'),
        tx(kx, 124, "joined", 13.5, P["cyan"], 'class="bold"'),
        f'<text x="{vx_r}" y="124" font-size="13.5">'
        f'<tspan fill="{P["gold"]}">{joined:%Y-%m-%d} · Day {elapsed:,}</tspan>'
        f'<tspan fill="{P["muted"]}" font-size="12.5">  ({join_note})</tspan></text>',
        tx(kx, np_y, "np_gauge", 13.5, P["cyan"], 'class="bold"'),
        *cells_svg,
        tx(bar_x + 20 * 12.5 + 10, np_y, "99%", 13.5, P["cyan"], 'class="np-low bold"'),
        tx(bar_x + 20 * 12.5 + 10, np_y, "100%", 13.5, P["gold"], 'class="np-full bold"'),
        tx(kx, 174, "tool", 13.5, P["cyan"], 'class="bold"'),
        f'<text x="{vx_r}" y="174" font-size="13.2">'
        f'<tspan fill="{P["mint"]}" class="bold">~/fgo-np-calculator</tspan>'
        f'<tspan fill="{P["muted"]}" font-size="12.5">  伤害区间 · NP 回收 · 3T 连发</tspan></text>',
        rule(kx, 830, 194.5, P["border"]),
        tx(kx, 218, "# " + shorten(profile["吐槽"], 42), 13, P["muted"], 'class="dim"'),
        box(714, 203, 116, 22, P["pill_gold_bg"], 4, P["pill_gold_bd"]),
        tx(772, 218, "Live Demo ↗", 11.5, P["gold"], 'text-anchor="middle" class="bold"'),
    ]
    desc = f"{title}。最推 {profile['最推从者']}，御主 Lv.{profile['御主等级']}，五星从者 {profile['五星从者']} 骑。"
    return omz_card(P, f"fgo-fetch · {title}", desc, 258, body, "fgo-fetch --profile", "FGO / TUI", GAME_MOTION + FATE_CSS, title_ink=P["fgo_title"])


# ----------------------------------------------------------------- 6. MINECRAFT (ZSH TUI)

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
    mod_tones = {"Mekanism": "cyan", "工业先锋": "gold", "资源蜜蜂": "gold", "AE2": "mint"}

    vx, vy, vw, vh = 28, 56, 206, 188
    parts = [
        _omz_prompt_row(P, "~/minecraft", "1.21.1", "mc-fetch --modpack", "neoforge"),
        forge_background(P),
        _game_ink(P),
        box(vx, vy, vw, vh, P["panel"], 8, P["border"]),
        f'<circle cx="{vx + 14}" cy="{vy + 16}" r="3" fill="{P["mint"]}"/>',
        tx(vx + 24, vy + 19.5, "grass_block · 3D", 10.5, P["mint"], 'class="bold"'),
        f'<g transform="translate({vx + 36} {vy + 31}) scale(1.22)">' + grass_block(P) + "</g>",
    ]

    kx, vx_r = 258, 354
    parts.extend([
        tx(kx, 76, "player", 13.5, P["cyan"], 'class="bold"'),
        f'<text x="{vx_r}" y="76" font-size="13.5">'
        f'<tspan fill="{P["text"]}" class="bold">{escape(shorten(title, 24))}</tspan>'
        f'<tspan fill="{P["muted"]}" font-size="12.5">  · Tech Modpacks</tspan></text>',
        tx(kx, 105, "packs", 13.5, P["cyan"], 'class="bold"'),
    ])
    cx = vx_r
    for pack in packs:
        label = shorten(pack, 18)
        pw = round(text_px(label, 12) + 20)
        parts.extend([
            box(cx, 89, pw, 22, P["pill_mint_bg"], 4, P["pill_mint_bd"]),
            tx(cx + pw / 2, 104, label, 12, P["mint"], 'text-anchor="middle"'),
        ])
        cx += pw + 8

    parts.append(tx(kx, 137, "mods", 13.5, P["cyan"], 'class="bold"'))
    cx = vx_r
    for mod in mods:
        label = shorten(mod, 14)
        tone = mod_tones.get(mod, "cyan")
        pw = round(text_px(label, 12) + 20)
        parts.extend([
            box(cx, 121, pw, 22, P[f"pill_{tone}_bg"], 4, P[f"pill_{tone}_bd"]),
            tx(cx + pw / 2, 136, label, 12, P[tone], 'text-anchor="middle"'),
        ])
        cx += pw + 8

    parts.extend([
        tx(kx, 166, "builds", 13.5, P["cyan"], 'class="bold"'),
        f'<text x="{vx_r}" y="166" font-size="13.2">'
        f'<tspan fill="{P["mint"]}" class="bold">~/agentinminecraft</tspan>'
        f'<tspan fill="{P["dim"]}"> · </tspan>'
        f'<tspan fill="{P["cyan"]}" class="bold">~/ftb-quests-preview</tspan></text>',
        rule(kx, 830, 194.5, P["border"]),
        tx(kx, 218, "# " + shorten(profile["玩家笔记"], 36), 13, P["mint"], 'class="dim"'),
        tx(830, 218, "● 蜜蜂在上班，我在看 JEI", 12, P["muted"], 'text-anchor="end"'),
    ])
    return omz_card(
        P,
        f"mc-fetch · {title}",
        "整合包：" + profile["整合包"] + "。模组：" + profile["熟悉的模组"] + "。" + profile["玩家笔记"],
        258,
        parts,
        "mc-fetch --modpack",
        "MC / TUI",
        FORGE_CSS,
        title_ink=P["mc_title"],
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
    proj_rows = [r for r in all_rows if r["repo"].lower() != OWNER.lower()]
    recent = (proj_rows if proj_rows else all_rows)[:4]

    body = [
        _omz_prompt_row(P, "~/projects", "main", "git log --all -n 4 --oneline", f"updated {end.strftime('%Y-%m-%d')}"),
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

    tips = read_tip_pages()
    for mode, P in THEMES.items():
        write(term_dir / f"banner-{mode}.svg", banner(data, P, tips))
        write(term_dir / f"neofetch-{mode}.svg", neofetch(data, P))
        write(term_dir / f"projects-{mode}.svg", projects_card(P))
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

    quick_links = []
    for name, _, _, _, repo_url, demo_url in FEATURED_PROJECTS:
        if demo_url:
            quick_links.append(f'<a href="{repo_url}">{name}</a> (<a href="{demo_url}">Demo</a>)')
        else:
            quick_links.append(f'<a href="{repo_url}">{name}</a>')

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

{_pic("assets/terminal/projects-dark.svg", "assets/terminal/projects-light.svg", "tree -L 1 ~/projects --featured")}

<sub><code>cd ~/projects</code> · {" · ".join(quick_links)}</sub>

<br/><br/>

{_pic("assets/terminal/skills-dark.svg", "assets/terminal/skills-light.svg", "ls -la ~/skills")}

{skill_icons}

<br/><br/>

<a href="https://1nsaneeee.github.io/fgo-np-calculator/">
{_pic("assets/terminal/chaldeas-dark.svg", "assets/terminal/chaldeas-light.svg", "fgo-fetch · 迦勒底御主档案")}
</a>

<sub><code>cat ~/chaldeas/AGENTS.md</code> · <a href="./chaldeas/AGENTS.md">御主档案源文件</a> · <a href="https://1nsaneeee.github.io/fgo-np-calculator/">在线打开宝具计算器</a> · <a href="{PROFILE}/fgo-np-calculator">源码仓库</a></sub>

<br/><br/>

<a href="{PROFILE}/ftb-quests-preview">
{_pic("assets/terminal/minecraft-dark.svg", "assets/terminal/minecraft-light.svg", "mc-fetch · Minecraft 科技水槽包任务手册")}
</a>

<sub><code>cat ~/Minecraft/SKILL.md</code> · <a href="./Minecraft/SKILL.md">任务手册源文件</a> · <a href="{PROFILE}/agentinminecraft">AI 进 MC 模组</a> · <a href="{PROFILE}/ftb-quests-preview">FTB 任务编辑器</a></sub>

<br/><br/>

{_pic("assets/terminal/shipped-dark.svg", "assets/terminal/shipped-light.svg", "Recent project commits & exit 0")}

</div>
"""
    return readme
