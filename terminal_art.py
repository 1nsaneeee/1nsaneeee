"""Render the profile's terminal windows from its Markdown files and one GitHub activity snapshot."""
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
from math import cos, pi, sin
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote

OWNER = '1nsaneeee'
PROFILE = f'https://github.com/{OWNER}'
PROJECTS = ('ftb-quests-preview', 'url-to-markdown', 'fgo-np-calculator', 'Programming-Carrier')
BG, PANEL, BORDER = '#0d1117', '#161b22', '#30363d'
WHITE, GRAY = '#e6edf3', '#8b949e'
MINT, CYAN, GOLD, RED = '#7ee787', '#79c0ff', '#e3b341', '#f85149'
FONT = "'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,monospace"


def tx(x, y, value, size=14, color=WHITE, extra=''):
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{color}" {extra}>'
            f'{escape(str(value))}</text>')


def box(x, y, w, h, fill, radius=0, stroke=None):
    edge = f' stroke="{stroke}"' if stroke else ''
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius}" fill="{fill}"{edge}/>'


def rule(x1, x2, y):
    return f'<path d="M{x1} {y}H{x2}" stroke="{BORDER}"/>'


def cells(text):
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in text)


def shorten(text, limit):
    if cells(text) <= limit:
        return text
    used = 0
    for index, char in enumerate(text):
        used += cells(char)
        if used > limit - 1:
            return text[:index].rstrip() + '…'
    return text


def card(title, desc, height, body, css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{height}" '
            f'viewBox="0 0 860 {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
            f'<style>text{{font-family:{FONT}}}.bold{{font-weight:700}}.dim{{font-style:italic}}'
            f'a:hover text{{text-decoration:underline}}{css}</style>'
            + box(.5, .5, 859, height-1, BG, 10, BORDER) + ''.join(body) + '</svg>\n')


def chrome(command, right=''):
    # One terminal prompt and the same baseline tie the independent modules together.
    return (tx(22, 25, '❯', 16, MINT, 'class="bold"') + tx(43, 25, command, 14, CYAN)
            + tx(837, 25, right, 11.5, GRAY, 'text-anchor="end"') + rule(1, 859, 38.5))


# Original terminal signature. Each 5x7 glyph advances six cells and leans 0.24 cell per row.
GLYPHS = {
    '1': ('00110','01110','00110','00110','00110','00110','11111'),
    'n': ('00000','00000','11010','11111','11011','11011','11011'),
    's': ('00000','00000','01111','11000','01110','00011','11110'),
    'a': ('00000','00000','01110','00011','01111','11011','01111'),
    'e': ('00000','00000','01110','11011','11111','11000','01111'),
}


def signature():
    runs = []
    for i, char in enumerate(OWNER):
        for j, row in enumerate(GLYPHS[char]):
            for run in re.finditer('1+', row):
                n = len(run[0])
                runs.append(f'M{6*i+run.start()} {j}h{n}v1h-{n}z')
    return ('<defs><path id="name" d="' + ''.join(runs) + '"/>'
            '<linearGradient id="ink" x2="0" y2="1"><stop stop-color="'+MINT+'"/>'
            '<stop offset="1" stop-color="'+CYAN+'"/></linearGradient>'
            '<pattern id="scan" width="1" height=".5" patternUnits="userSpaceOnUse">'
            '<path d="M0 .46H1" stroke="#101e29" stroke-opacity=".21" stroke-width=".08"/></pattern>'
            '<clipPath id="face"><use href="#name"/></clipPath>'
            '<linearGradient id="glint"><stop stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".54" stop-color="#fff" stop-opacity=".45"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
            '<g aria-label="1nsaneeee" transform="translate(177.5 55) scale(9.36) matrix(1 0 -.24 1 1.68 0)">'
            '<use href="#name" fill="#284853" transform="translate(.36 .44)"/>'
            '<use href="#name" fill="url(#ink)"/><use href="#name" fill="url(#scan)"/>'
            '<g clip-path="url(#face)"><path class="glint" fill="url(#glint)" d="M-8 0h7l-2 7h-7z"/></g></g>')


def tip_pages(config):
    pages = []
    for line in config.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Long tips continue on the following slide at the same readable font size.
        while cells(line) > 78:
            width = last_break = 0
            for i, char in enumerate(line):
                width += cells(char)
                if width > 78:
                    break
                if char.isspace() or char in '，。！？；、,;.!?':
                    last_break = i+1
            split = last_break if last_break >= i//2 else i
            pages.append(line[:split].rstrip())
            line = line[split:].lstrip()
        if line:
            pages.append(line)
    return pages


def loading_tips(tips):
    height = 30
    body = [f'<svg x="30" y="44" width="800" height="{height}" overflow="hidden">'
            f'<g class="{"tip-reel" if len(tips)>1 else "single-tip"}" '
            f'style="--pages:{len(tips)};--cycle:{len(tips)*6}s;--travel:-{len(tips)*height}px">']
    for i,tip in enumerate(tips):
        body.append(f'<text x="400" y="{i*height+20}" text-anchor="middle" font-size="14">'
                    f'<tspan fill="{GOLD}" class="bold">TIP › </tspan>'
                    f'<tspan fill="{WHITE}">{escape(tip)}</tspan></text>')
    return ''.join(body)+'</g></svg>'


def banner(data):
    day = data['end'][:10]
    tips = tip_pages(Path(__file__).with_name('coldjokeconfig').read_text(encoding='utf-8-sig'))
    body = [chrome(f'{OWNER}@github: ~ — zsh', f'Last login: {day} on ttys000')]
    offset = 34 if tips else 0
    if tips:
        body.append(loading_tips(tips))
    body.extend([f'<g transform="translate(0 {offset})">', signature()])
    for i,(x,y,s) in enumerate([(67,89,1.3),(137,60,.65),(151,130,.85),(679,53,.7),(705,117,1.12),(812,109,.7)]):
        color = (CYAN, MINT, GOLD)[i%3]
        body.append(f'<g transform="translate({x} {y}) scale({s})"><path class="star" '
                    f'style="animation-delay:-{i*.61:.2f}s" fill="{color}" '
                    'd="M-1 -5h2v3h1v1h3v2H2v1H1v3h-2V2h-1V1h-3v-2h3v-1h1z"/></g>')
    cat = (tx(0,0,r'/\_/\ ',15,CYAN) + tx(-8,15,'( o.o )',15,WHITE,'class="eyes"')
           + tx(-8,15,'( -.- )',15,WHITE,'class="lid"') + tx(-6,30,'/',14,MINT)
           + '<g class="paw">'+tx(9,30,'>o',13,MINT)+'</g><g class="mote">'
           + tx(33,29,'✦',12,GOLD)+'</g>')
    body += [f'<g transform="translate(736 71)">{cat}</g>',
             tx(430,149,'写点工具，也做游戏 · MC Modding & FGO Math',16,WHITE,'text-anchor="middle"'),
             rule(22,838,165.5), tx(24,188,f'{OWNER}@github',14,MINT,'class="bold"'),
             tx(174,188,'~ ❯',14,CYAN),
             '<defs><clipPath id="type"><rect class="reveal" width="94" height="23" y="-17"/></clipPath></defs>',
             '<g transform="translate(214 188)"><g clip-path="url(#type)">'
             + tx(0,0,'cat ~/.plan',15,WHITE,'textLength="90" lengthAdjust="spacingAndGlyphs"')
             + '</g><g class="caret"><rect x="2" y="-12" width="8" height="15" fill="'+MINT+'" class="blink"/></g></g>',
             tx(24,213,'给 Minecraft 写模组，给 FGO 算伤害。',15,GRAY,'class="output"'),'</g>']
    css = """
.lid,.glint{opacity:0}.caret{transform:translateX(90px)}
@media(prefers-reduced-motion:no-preference){
.tip-reel{animation:tips var(--cycle) steps(var(--pages),end) infinite}
.tip-reel text{animation:tip-arrives 6s ease-out infinite}
.reveal{animation:type 1.08s steps(11,end) both}.caret{animation:travel 1.08s steps(11,end) both}
.blink{animation:blink 1.1s steps(1,end) infinite}.output{animation:answer .23s ease-out 1.08s backwards}
.eyes{animation:eyes 4s step-end infinite}.lid{animation:lid 4s step-end infinite}
.star{animation:twinkle 3.8s ease-in-out infinite}.glint{animation:shine 7.6s ease-in-out 1.5s infinite}
.paw{animation:reach 4s ease-in-out infinite}.mote{animation:dodge 4s ease-in-out infinite}}
@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes tips{from{transform:translateY(0)}to{transform:translateY(var(--travel))}}
@keyframes tip-arrives{0%{opacity:.4;transform:translateY(2px)}6%,94%{opacity:1;transform:translateY(0)}100%{opacity:.4}}
@keyframes travel{from{transform:translateX(0)}to{transform:translateX(90px)}}
@keyframes answer{from{opacity:0}to{opacity:1}}@keyframes blink{50%{opacity:0}}
@keyframes eyes{0%,96%{opacity:1}92%{opacity:0}}@keyframes lid{0%,96%{opacity:0}92%{opacity:1}}
@keyframes reach{0%,61%,85%,100%{transform:translateX(0)}73%{transform:translate(7px,-2px)}}
@keyframes dodge{0%,69%,92%,100%{transform:translate(0,0)}79%{transform:translate(5px,-4px)}}
@keyframes twinkle{0%,55%,100%{opacity:.38}70%{opacity:1}}
@keyframes shine{0%{opacity:1;transform:translateX(66px)}25%{opacity:1;transform:translateX(-2px)}26%,100%{opacity:0;transform:translateX(-2px)}}
"""
    return card(OWNER+' · zsh',f'写点工具，也做游戏。给 Minecraft 写模组，给 FGO 算伤害。Last login {day}.',230+offset,body,css)


GEMINI_HALF = (
    '+', '#', '+@+', '#@#', '.#@#.', '+@@@+', '+#@@@#+',
    '.#@@@@@#.', '+#@@@@@@@#+', '+#@@@@@@@@@#+',
    '.+#@@@@@@@@@@@@@#+.', '.:+#@@@@@@@@@@@@@@@@@@@#+:.',
    '.:+##@@@@@@@@@@@@@@@@@@@@@@@@@##+:.',
)
GEMINI_MARK = tuple(row.center(43) for row in
                    (*GEMINI_HALF, '..+##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@##+..', *reversed(GEMINI_HALF)))
OPENAI_MARK = (
    '             .+#@@@@@#:.',
    '           :@@@@##+#@@@@#..::::.',
    '         .@@@+.       +@@@@@@@@@@@+.',
    '        .@@#.       :#@@@#::..::#@@@+',
    '        @@#      .#@@@#:          +@@@.',
    '     .:#@@.   .+@@@#:.     ..      .@@#',
    '   .#@@@@@    @@@+.     .+@@@@+.    :@@:',
    '  +@@@:#@@    @@+    .:#@@@+#@@@#:.  @@#',
    ' +@@+  +@@    @@+  :#@@@#:    :#@@@#:#@#',
    ':@@:   +@@    @@#+@@@@@@@+.     .:#@@@@+',
    '#@#    +@@    @@@@@+. .+@@@@+.     .+@@@:',
    '@@+    +@@    @@#.       .#@@@#:.     +@@:',
    '@@+    +@@    @@+         +@@#@@@#:    +@@.',
    '#@@    :@@@#: @@+         +@@  :#@@+    @@#',
    '.@@#    .+@@@@@@+         +@@    @@+    +@@',
    ' .@@#.     .+@@@@:       :@@@    @@+    +@@',
    '  .@@@#:      .#@@@#: :#@@@@@    @@+    @@#',
    '   #@@@@@#:      :#@@@@@#:+@@    @@+   +@@.',
    '   #@# :@@@@+.  .+@@@@+.  +@@    @@+ .#@@:',
    '   #@@   .+@@@@@@@@+.     +@@    @@##@@@:',
    '   :@@:     .+@@#:      :#@@@    @@@@@:',
    '    #@@:             :#@@@#:    :@@:.',
    '     #@@#.        .+@@@#:      .@@#',
    '      :@@@@#++++#@@@@+.       :@@@',
    '        .+@@@@@@@@@@#:     .:#@@+',
    '            ....  +@@@@@@@@@@@+.',
    '                    .:+####+:',
)
CLAUDE_MARK = (
    '          #.            ##',
    '         .##.   +@+    .@+',
    '          .##.  .##    +@.',
    '           .##.  #@.  .##.',
    '            .##+ +@#  +@#   #@+',
    '             .#@+.##. #@+ .#@+       .#',
    '        @#.   .#@++@+.##..#@+     +#@#+.',
    '        .#@#+. .#@+@#+@#+@@+  .+#@#+.',
    '          .+#@#+.#@#@#@+@#+.+#@#+.',
    '             .#@@##@@#@@###@##.',
    ' ###+++++++++++++#@@@@@@@@#.',
    ' .+++++######@@@@@@@@@@@@@@@######+++..',
    '             .+#@@@@@@@@@#++++++#######',
    '          .+#@@##@@+@@#@@#@@#.',
    '      .+#@@#+.+@@#.#@#@.#@#+#@#+.',
    '     #@#+.  +#@#. .###@+.#@#..+#@#.',
    '          .#@#.   +@##@+  +@#.  .#@#+.',
    '         +@#.     #@++@+   .##+    .#@#+',
    '       +##+      .##.+@#    .#@       +',
    '       #+        +@+ .##',
    '                 ##.  ##.',
    '                 ##   ##.',
    '                      +@.',
    '                      .@+',
)


def computer_cat():
    # The cat is the monitor: ears and whiskers meet the bezel, and a power LED sits on its chin.
    parts = []
    def shape(d, fill):
        return f'<path d="{d}" fill="{fill}"/>'
    parts += [shape('M24 49V8h9v7h9v7h9v7h9v6h72v-6h9v-7h9v-7h9V8h9v41h8v78h-8v9H24v-9h-8V49z','#516d83'),
              shape('M32 37V22h6v7h8v8zm116 0h12V22h-5v7h-7z',CYAN),
              box(21,42,150,84,'#9bb9c4',5),box(27,48,138,71,'#233341',4),box(32,53,128,60,'#152530',3),
              shape('M37 57h32v3H40v20h-3z','#314b57'),
              shape('M50 74h7v-5h23v5h4v16H50zm60 0h5v-5h23v5h5v16h-33z',MINT),
              '<g class="pupils">'+shape('M67 73h7v13h-7zm60 0h7v13h-7z','#172a30')+'</g>',
              shape('M90 88h13v4h-4v4h-5v-4h-4z',GOLD),
              shape('M83 95h4v4h7v-3h5v3h8v-4h4v7h-10v-2h-8v2H83z','#9bb9c4'),
              shape('M7 83h20v4H7zm-5 13h23v4H2zm161-13h21v4h-21zm2 13h23v4h-23z',CYAN),
              box(34,129,31,2,'#8da6b4'),box(151,127,7,4,MINT),
              shape('M81 136h29v9h15v6H65v-6h16z','#516d83'),
              box(52,151,90,4,'#344653')]
    return ''.join(parts)


def ascii_mark(rows,color):
    # A fixed text advance keeps the negative space in the knot and starburst stable.
    pitch=4.45
    step=5.9
    width=max(len(row.rstrip()) for row in rows)
    x0=(190-width*pitch)/2
    y0=(157-len(rows)*step)/2
    ink=[]
    bed=[]
    for i,row in enumerate(rows):
        if not row.strip():
            continue
        value=row.strip()
        left=len(row)-len(row.lstrip())
        y=y0+i*step
        for run in re.finditer('[@#]+',row):
            n=len(run[0])
            bed.append(f'M{run.start()} {i}h{n}v1h-{n}z')
        ink.append(f'<text x="{x0+left*pitch:g}" y="{y+5.55:g}" textLength="{len(value)*pitch:.2f}" '
                   f'lengthAdjust="spacingAndGlyphs">{escape(value)}</text>')
    return (f'<path fill="{color}" opacity=".27" transform="translate({x0:g} {y0:g}) scale({pitch} {step})" '
            f'd="{"".join(bed)}"/><g fill="{color}" font-size="7.5" font-weight="700" xml:space="preserve">'
            +''.join(ink)+'</g>')


PORTRAIT_CSS = """
.slide,.contact-sheet{opacity:0}.first{opacity:1}
.crt-line,.fault-band{opacity:0}
@media(prefers-reduced-motion:no-preference){
.slide{animation:channel 12s linear infinite;animation-delay:var(--offset)}
.crt-line{animation:crt-pass 3s linear infinite}
.gemini-mark,.openai-mark{transform-box:fill-box;transform-origin:center}
.gemini-mark{animation:stellar 3s ease-in-out infinite}
.openai-mark{animation:knot-turn 3s ease-in-out infinite}
.claude-mark{animation:signal-drop 3s steps(1,end) infinite}
.fault-band{animation:bad-scan 3s steps(1,end) infinite}}
@keyframes channel{0%,23.6%{opacity:1}25%,98.6%{opacity:0}100%{opacity:1}}
@keyframes crt-pass{0%,12%{opacity:0;transform:translateY(0)}18%{opacity:.55}65%,100%{opacity:0;transform:translateY(53px)}}
@keyframes stellar{0%,100%{transform:scale(.84) rotate(-6deg)}51%{transform:scale(1.04) rotate(9deg)}}
@keyframes knot-turn{0%,13%{transform:rotate(-30deg) scale(.82)}81%,100%{transform:rotate(30deg) scale(.82)}}
@keyframes signal-drop{0%,37%,47%,100%{opacity:1}34%,44%{opacity:.73}}
@keyframes bad-scan{0%,100%{opacity:0}32%,42%{opacity:1;transform:translateX(5px)}35%,46%{opacity:1;transform:translateX(-3px)}38%,49%{opacity:0}}
@media(prefers-reduced-motion:reduce){.channels{display:none}.contact-sheet{opacity:1}}
"""


def mascot():
    portraits=[('meow','MEOW',MINT,computer_cat()),
               ('gemini','GEMINI',MINT,ascii_mark(GEMINI_MARK,MINT)),
               ('openai','OPENAI',CYAN,ascii_mark(OPENAI_MARK,CYAN)),
               ('claude','CLAUDE / 403',RED,ascii_mark(CLAUDE_MARK,RED))]
    parts=[box(20,53,268,230,BG,8,BORDER),'<defs>',
           '<clipPath id="glitch-slice"><path d="M0 46h190v9H0z M0 100h190v4H0z"/></clipPath>']
    for name,_,_,art in portraits:
        parts.append(f'<g id="portrait-{name}">{art}</g>')
    parts.append('</defs><g class="channels">')
    for i,(name,label,color,_) in enumerate(portraits):
        offset=3*i-12 if i else 0
        parts.append(f'<g class="slide{" first" if not i else ""}" style="--offset:{offset}s">')
        parts.append(tx(270,74,label,11,color,'text-anchor="end"'))
        parts.append(f'<g transform="translate(61 83)"><g class="{name}-mark"><use href="#portrait-{name}"/></g>')
        if name=='meow':
            parts.append(f'<rect class="crt-line" x="34" y="55" width="122" height="1.5" fill="{MINT}"/>')
        if name=='claude':
            parts.append('<g clip-path="url(#glitch-slice)"><g class="fault-band">'
                         +box(-7,0,204,159,BG)+'<use href="#portrait-claude"/></g></g>')
        parts.append('</g>')
        for j in range(4):
            parts.append(box(123+j*17,264,12,3,color if i==j else BORDER,1))
        parts.append('</g>')
    parts.append('</g><g class="contact-sheet">')
    for i,(name,label,color,_) in enumerate(portraits):
        x,y=36+(i%2)*124,66+(i//2)*107
        parts.append(f'<use href="#portrait-{name}" transform="translate({x+17} {y}) scale(.46)"/>')
        parts.append(tx(x+61,y+89,label,10.5,color,'text-anchor="middle"'))
    return ''.join(parts)+'</g><!-- crawler.note: 1nsaneeee / 10x dev, powered by coffee. -->'


def spinner(x,y):
    frames = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    parts=[]
    coords=[(2,2),(2,5),(2,8),(5,2),(5,5),(5,8),(2,11),(5,11)]
    for i,ch in enumerate(frames):
        dots=''.join(f'<circle cx="{cx}" cy="{cy+14*i}" r="1.3"/>' for b,(cx,cy) in enumerate(coords) if (ord(ch)-0x2800)&(1<<b))
        parts.append(dots)
    return (f'<svg x="{x}" y="{y-12}" width="8" height="14" viewBox="0 0 8 14" overflow="hidden">'
            f'<g fill="{MINT}" class="spinner">{"".join(parts)}</g></svg>')


def languages(totals):
    x,y,w = 331,248,506
    entries = sorted(((name,n) for name,n in totals.items() if n>0),key=lambda item:(-item[1],item[0]))
    total = sum(n for _,n in entries)
    palette = (MINT,CYAN,GOLD,GRAY,PANEL,WHITE)
    parts=[box(x,y,w,7,PANEL,3.5)]
    if total:
        segments=entries[:3]
        if len(entries)>3:
            segments.append(('Other',sum(n for _,n in entries[3:])))
        parts.append(f'<defs><clipPath id="langs">{box(x,y,w,7,WHITE,3.5)}</clipPath></defs><g clip-path="url(#langs)">')
        pos=x
        labels=[]
        for (name,n),color in zip(segments,palette):
            width=w*n/total
            parts.append(box(pos,y,width,7,color))
            pos+=width
            labels.append(f'{shorten(name,13)} {100*n/total:.0f}%')
        parts.append('</g>')
        caption=' · '.join(labels)
    else:
        caption='Languages: —'
    parts.append(tx(x,277,shorten(caption,55),11,GRAY))
    for i,color in enumerate(palette):
        parts.append(box(748+i*15,267,11,11,color,1,BORDER if color==PANEL else None))
    return ''.join(parts)


def game_ink():
    # Text tiles act as the ink. Each face of the cube has its own grain direction.
    materials = [
        ('grass',MINT,.29,MINT,'v,"',"'v;"), ('loam','#cdab83',.29,'#cdab83','+%:','#.+'),
        ('soil','#a2876d',.29,'#a2876d','/:#','+/.'),
    ]
    parts=['<defs>']
    for name,base,opacity,ink,a,b in materials:
        glyphs='class="bold" xml:space="preserve" textLength="10.5" lengthAdjust="spacingAndGlyphs"'
        parts.append(f'<pattern id="ink-{name}" width="10.5" height="10" patternUnits="userSpaceOnUse">'
                     +f'<rect width="10.5" height="10" fill="{base}" opacity="{opacity}"/>'
                     +tx(0,4.6,a,5.6,ink,glyphs) +tx(0,9.6,b,5.6,ink,glyphs)
                     +'</pattern>')
    return ''.join(parts)+'</defs>'


def game_shape(outline,ink,edge):
    return f'<path d="{outline}" fill="url(#ink-{ink})" stroke="{edge}" stroke-width=".95" stroke-linejoin="round"/>'


# ASCII palette and silhouette sampled from the supplied crowned Artoria portrait.
SABER_INKS = (
    ('A', "#f9eed7", ':'),
    ('B', "#f8e1c4", '-'),
    ('C', "#f8daaf", '='),
    ('D', "#fad298", '#'),
    ('E', "#fece8d", '/'),
    ('F', "#f7c484", '\\'),
    ('G', "#ebd8bf", ':'),
    ('H', "#ebc89b", '#'),
    ('I', "#eabb83", '/'),
    ('J', "#e0c5aa", ':'),
    ('K', "#c8c5ce", '.'),
    ('L', "#e6af6f", '#'),
    ('M', "#ddaf7c", '/'),
    ('N', "#e0a869", '\\'),
    ('O', "#dca465", '='),
    ('P', "#d5a677", '#'),
    ('Q', "#bba79f", '-'),
    ('R', "#d09c6d", '\\'),
    ('S', "#cc9562", '='),
    ('T', "#b69684", '-'),
    ('U', "#b28767", '/'),
    ('V', "#836358", ':'),
    ('W', "#265e57", 'o'),
    ('X', "#419287", 'o'),
    ('Y', "#7cd6c4", 'o'),
    ('Z', "#343136", '='),
    ('0', "#f2f1e5", '.'),
)
SABER_ROWS = (
    '  DDPHCHMMPHCHHPHCDMRRRRRRPRRRRH',
    '  CCPPHGPJJIHPRPDDDDPPPRPRPPRRRHHDCAH',
    '   HJ00BRPHHHRRMDDCDPPMPPMMMPRRPBADFGJ',
    '   00AIPRPPPRMPPMDCDPIIMPMIMPRSSIICCHJ',
    '  00 PPSRPPRRRPMMICCIIIIMHIPPPSLLHHLCHC',
    '  00 TPRRRMRPPPPIMCCCDDDIIMMRSOLLLIGFCEC',
    ' 0B  ISRSUPPPRMMPDCCCDHIIHMSSSONLONLBCBFJ',
    ' A   GPUUURPPPMHDDDDHDDDMSSSONNOONONLAACJ',
    'AJ    JUUSRPMMIIIHDDHDPSSSSONONLOOOPINAAIH',
    'BQ    KMUUSRPPMIDDIMRSSSONNONLONILOOIINBAIC',
    'H      JRURRPPPRSSSSSOONNNLLONIONILOOCMNBAD',
    'Q      HAHPUSSSUSOOOLNNNNLNLLOLIONMIONASOCBM',
    'T     KDAHRLOOLSNNLNLLNNNLLNFLOFLONMIOHJSSIG',
    '      JAHHOINNISLNFNLFLLLLFILFNLFNOOILOAHIRNH',
    '      HAIONLLLINLNFLLEFEFLEEFIFNFFOOSIOHHGHM',
    '     KBDIOLLLIMLFNEFLEFFEEFEEFFLIFIOSSLOGLBIH',
    '     Q0LMOILLFMLELFFFEEFFEEEEEFENFFLOUNOJSHCMQ',
    '     JANMOFNIEPNEIFFFEEEIEEEEEEELLFFOSSLMPOGJQ',
    '     GBOLNFSFEPOEELFFEEEFFEEEIEEFSFFLSSSOQOICQQ',
    '     GCNLLFSEEPSEELEFEDDDPDDEREEESLFFOUSSPSOCJQ',
    '    KGHMLLFSFEPSEDFEDDDDDIMDDIREEPUFFLUSSRSSICQQ',
    '    KGHMLLFUFEPUFDDFDDDDDDUEDDSMEIUSFFUSOSSSOBJQ',
    '    KJHMILFUIEPRMDHEDDDDDDPRDDPRMFUSSFSSOOSOSIGKK',
    '    KMHSHNFUOEPPRDIDEDDDDIIPPEPRRMUUOUUSOOOOPOAKG',
    '    KPMSJOFSSEMRRDDRDDDDDMDPUTMUVVVUSUUUOONNNRCB0G',
    '    KPPSJOISUFIRPPDRIEDDDIPTJUVZVQVUSOUSSOLLOMMG00J',
    '    KLQSRILRRUIUURIMPIEEDPQPUUZZZQUSSFUSUONIOHSAG0K',
    '    JLJSSJLPPSMUPTUIMMIEEEGUJUWZWVTPSFSSSSNILMPGG00G',
    '    JLBTOUISRVTTZVTPMHMIEEJTG0XXXTPISESSSSNILOJM0G0K',
    '   KML JOUSRUSQJVZVQTHHJIIHGGGVXVJPHSEOUSSLFIOJUAJGG',
    '   QGO ANSVSVRT0QWXTHIHGGGJBBBJJBGMHRFNVSSLEFOJVT0UG',
    '   KGS  IOUUVVMAQXYTHPHGBBBBBBBBBBMHPINVVONEFOHVVQGK',
    '   KG   HNUUSVTMAVUJHPHGBBBBBBBBBBMIPINKVOPEENCVVVQQ',
    '   QG   IMOUUPVJHJJCJPCGBBBBBBBBBBJMUIL0TUPEELBVV 0K',
    '   KK    INSSUPTJJGGGJGBBBBBBBBBBGJSVIP KVPDDIA0000K',
    '    K    ILLSSKTJJCGGGGBBBBBBBBBBGHUVIP  TPDDHG00KKK',
    '    K0    FLLOKKQGGGBBBBBBBBGBBBBJUUVDQ  KPDDGJKK00K',
    '    KG     FLLTKKKQBGGBGJBBBBBBBJVVVVDQ  0PDDGTKKKKQ',
    '     K0    FEFMQKKKQGGGGBBBABBBJVUUVVMT  KTFDKTQQQKQ',
    '     QA     EDDMKKKKKQGGGBBBBBJVUVVVVUVTQQTPDQKQQKKT',
    '      K      EDCJ00KKKJQJBBBGUVUSONUUUUVQQTQPKKKKKKQ',
    '              HCCQQQQKQQTUJMUURLFFOVVUVVQQQQQK0KKKKK',
    '                CTQQQQQQTUUUTQQQQTZZZUUVQKKKKK000KKQ',
    '                 MQTTTTTQ000000KQKVZZVTQQK00KK00',
    '                 GQVTQVQK          ZZZQKK0000',
    '                   WTT               VQKK0',
)


SABER_LID_Y = 24
SABER_LIDS = (
    '                               HHJT',
    '                             PJBBGJ',
    '                           MJBBBJVT',
    '             R R           M BJTVJP',
    '            PQQGJ          QVVVTJB',
    '             VUGBG           BBBBG',
    '             PVTGBJ           BB',
    '              HTVVQJ',
    '               JGJJ',
)


def portrait_strokes(rows,code):
    return ''.join(f'M{run.start()} {y}h{len(run[0])}'
                   for y,row in enumerate(rows) for run in re.finditer(code+'+',row))


def artoria():
    # Paint the sampled colours continuously; a transparent ASCII tile adds the
    # character grain without introducing dark seams between neighbouring pixels.
    defs=[]
    glyph_ids={}
    layers=[([],[]),([],[])]
    for code,color,glyph in SABER_INKS:
        if glyph not in glyph_ids:
            tile='saber-glyph-'+str(len(glyph_ids))
            glyph_ids[glyph]=tile
            defs.append(f'<pattern id="{tile}" patternUnits="userSpaceOnUse" width="1.6" height="1.6" '
                        'viewBox="0 0 6 7" preserveAspectRatio="none">'
                        +tx(0,6,glyph,7,'#3c2f29','font-weight="700" opacity=".32"')+'</pattern>')
        for i,rows in enumerate((SABER_ROWS,SABER_LIDS)):
            strokes=portrait_strokes(rows,code)
            if not strokes:
                continue
            ink='saber-'+str(i)+code
            defs.append(f'<path id="{ink}" d="{strokes}"/>')
            base,letters=layers[i]
            base.append(f'<use href="#{ink}" stroke="{color}"/>')
            letters.append(f'<use href="#{ink}" stroke="url(#{glyph_ids[glyph]})"/>')
    painted=['<g shape-rendering="crispEdges">'+''.join(base)+'</g>'+''.join(letters) for base,letters in layers]
    return ('<defs>'+''.join(defs)+'</defs><g transform="translate(0 3) scale(2.12 2.29)" '
            'fill="none" stroke-width="1.015">'+painted[0]
            +f'<g class="saber-lids" transform="translate(0 {SABER_LID_Y})">'+painted[1]+'</g></g>')





def cube_pose(angle):
    # Orthographic isometric camera; a face is a textured unit square with a 100x100 UV grid.
    c,s=cos(angle),sin(angle)
    corners=[]
    for x,z in ((-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)):
        corners.append((55+65.05*(x*c-z*s),34.5+37.56*(x*s+z*c)))
    px,py=corners[0]
    poses=[(True,((corners[1][0]-px)/100,(corners[1][1]-py)/100,
                  (corners[3][0]-px)/100,(corners[3][1]-py)/100,px,py))]
    for i,(end_x,end_y) in enumerate(corners):
        x,y=corners[(i+1)%4]
        poses.append((end_x>x+0.001,((end_x-x)/100,(end_y-y)/100,0,.5312,x,y)))
    return poses


def grass_block():
    # Patches of lighter and darker texels break up the repeating character grain.
    grass_pixels='<path d="M3 9h13v7H3z M20 13h9v8h-9z M53 4h12v8H53z M72 27h10v9H72z M4 44h10v8H4z M31 58h16v9H31z M80 76h9v14h-9z M47 89h11v7H47z" fill="#20472c" opacity=".5"/>'
    dirt_pixels='<path d="M3 37h11v7H3z M28 29h8v10h-8z M55 44h14v8H55z M81 37h11v6H81z M15 62h15v11H15z M42 73h9v6h-9z M73 86h14v8H73z M5 90h11v8H5z" fill="#654833" opacity=".6"/>'
    top=(box(0,0,100,100,'url(#ink-grass)')
         +grass_pixels
         +'<path d="M9 16h6v3H9z M69 11h5v3h-5z M43 30h8v3h-8z M18 72h6v3h-6z M75 83h8v3h-8z" fill="#9ace83"/>')
    fringe='M0 0h100v15h-8v4h-8v-6h-9v10h-7v-8h-9v5h-9v-7h-9v13h-6v-8h-9v-5h-8v7h-9v-6H0z'
    side=(box(0,0,100,100,'url(#ink-loam)')+dirt_pixels+game_shape(fringe,'grass','#568350')
          +'<path d="M9 41h8v4H9z M46 70h6v4h-6z M78 54h9v3h-9z" fill="#9c7a53"/>')
    parts=['<defs><g id="block-top">'+top+'</g><g id="block-wall">'+side+'</g></defs>']
    frames=72
    poses=[cube_pose(pi/4+2*pi*f/frames) for f in range(frames+1)]
    css=[]
    for face in range(5):
        keys=[]
        hidden=False
        for f,pose in enumerate(poses):
            visible,matrix=pose[face]
            transform='matrix('+','.join(f'{n:.3f}'.rstrip('0').rstrip('.') for n in matrix)+')'
            if f==0:
                ref='block-top' if face==0 else 'block-wall'
                parts.append(f'<g class="cube-face-{face}" visibility="{"visible" if visible else "hidden"}" transform="{transform}">'
                             f'<use href="#{ref}"/>')
                if face in (1,3):
                    parts.append('<rect width="100" height="100" fill="#17232a" opacity=".24"/>')
                parts.append('</g>')
            if not visible and hidden and f!=frames:
                continue
            style=f'visibility:visible;transform:{transform}' if visible else 'visibility:hidden'
            keys.append(f'{100*f/frames:.2f}%{{{style}}}')
            hidden=not visible
        css.append(f'@keyframes yaw-{face}{{{"".join(keys)}}}'
                   f'@media(prefers-reduced-motion:no-preference){{.cube-face-{face}{{animation:yaw-{face} 6s step-end infinite}}}}')
    return '<style>'+''.join(css)+'</style>'+''.join(parts)


def read_save(relative):
    """Read the heading and full-width-colon Markdown fields displayed by cat."""
    lines=(Path(__file__).parent/relative).read_text(encoding='utf-8-sig').splitlines()
    title=next(line[2:].strip() for line in lines if line.startswith('# '))
    fields={}
    for line in lines:
        if line.startswith('- ') and '：' in line:
            key,value=line[2:].split('：',1)
            fields[key.strip()]=value.strip()
    return title,fields


def file_header(relative,mode):
    return anchor(f'{PROFILE}/{OWNER}/blob/main/{relative}',relative,
                  chrome('cat ~/'+relative,mode))


def master_record(data):
    relative='chaldeas/AGENTS.md'
    title,profile=read_save(relative)
    joined=date.fromisoformat(profile['入坑日期'])
    elapsed=(date.fromisoformat(data['end'][:10])-joined).days+1
    gold='#b69b62'
    body=[
        file_header(relative,'FGO / MASTER FILE'),
        '<path d="M21 51h156l10 10v152H30l-9-9z" fill="#171918" stroke="#716246"/>',
        '<path d="M21 74V51h23m118 0h15l10 10v18m0 115v19h-22m-120 0H30l-9-9v-11" fill="none" stroke="#d8b779" stroke-width="1.5"/>',
        '<g transform="translate(26 54) scale(1.37)">'+artoria()+'</g>',
        '<path d="M22 193h164v19H30l-8-8z" fill="#20221f"/>',
        tx(104,207,'阿尔托莉雅 / SABER',11,WHITE,'text-anchor="middle"'),
        tx(213,68,'# '+shorten(title,24),14,gold),
        tx(213,101,shorten(profile['最推从者'],16),26,WHITE,'class="bold"'),
        tx(213,122,'最推从者',12,GRAY),
        '<g transform="translate(438 67)" fill="none" stroke="#b39b71" stroke-width="1.4">'
        '<path d="M0 0q32 4 38 34L0 0l14 34z M1 29L33 2m-8 1 8-1-2 8"/></g>',
        rule(213,503,134.5),
        tx(213,166,shorten(profile['御主等级'],5),26,GOLD,'class="bold"'),
        tx(352,166,shorten(profile['五星从者'],5),26,GOLD,'class="bold"'),
        tx(214,186,'御主等级',12,GRAY),tx(352,186,'五星从者 / 骑',12,GRAY),
        tx(213,212,f'{joined:%Y.%m.%d} '+shorten(profile['入坑备注'],18),13,WHITE),
        '<path d="M526 55v155" stroke="#383b39"/>',
        tx(551,69,'NP / 宝具试算',14,CYAN,'class="bold"'),
        box(552,84,221,8,'#263640',2),box(552,84,218.8,8,'#82bde2',2),
        '<rect class="np-last" x="769" y="84" width="4" height="8" fill="#f7d875"/>',
        tx(832,93,'99%',14,CYAN,'class="np-low" text-anchor="end"'),
        tx(832,93,'100%',14,GOLD,'class="np-full" text-anchor="end"'),
        tx(551,116,'伤害区间 · NP 回收 · 三回合连发',13,GRAY),
        anchor(PROFILE+'/fgo-np-calculator','宝具伤害计算器',tx(551,139,'~/fgo-np-calculator/ ↗',13,CYAN)),
        rule(551,837,153.5),tx(551,179,f'入坑第 {elapsed:,} 天',16,GOLD),
        tx(551,208,'# '+shorten(profile['吐槽'],31),12.5,GRAY,'class="dim"'),
    ]
    desc=f"{title}。最推 {profile['最推从者']}，御主 Lv.{profile['御主等级']}，五星从者 {profile['五星从者']} 骑。{joined} {profile['入坑备注']}。"
    return card(title,desc,233,body,GAME_MOTION)


def quest_book(data):
    relative='Minecraft/SKILL.md'
    title,profile=read_save(relative)
    packs=[s.strip() for s in profile['整合包'].split('/') if s.strip()]
    mods=[s.strip() for s in profile['熟悉的模组'].split('/') if s.strip()]
    icons={
        'Mekanism':('M0 2h12v10H0z M3 5v4h6V5z',CYAN,'矿物处理'),
        '工业先锋':('M0 5h3V2h3v3h3V1h3v11H0z',GOLD,'工业自动化'),
        '资源蜜蜂':('M1 2h3l3 2 2-2h3v3l-2 1v4H3V6L1 5z M5 6v3h1V6z',GOLD,'资源生产'),
        'AE2':('M1 0h10v12H1z M3 2v2h6V2z M3 6v2h6V6z',MINT,'ME 网络'),
    }
    parts=[file_header(relative,'MINECRAFT / QUEST BOOK'),game_ink(),
           '<g transform="translate(28 56) scale(1.34)">'+grass_block()+'</g>',
           tx(103,222,'minecraft:grass_block',11,GRAY,'text-anchor="middle"'),
           '<path d="M192 53v170" stroke="#304438"/>',
           tx(215,72,'# '+shorten(title,33),20,WHITE,'class="bold"'),tx(215,102,'PACKS',11,GRAY)]
    cursor=262
    pack_y=86
    for pack in packs:
        label=shorten(pack,19)
        width=cells(label)*7+20
        if cursor+width>838:
            cursor=262
            pack_y+=28
        parts.extend([box(cursor,pack_y,width,22,'#1d3027',3),tx(cursor+10,pack_y+15,label,12,MINT)])
        cursor+=width+7
    shift=pack_y-86
    parts.extend([rule(215,837,119.5+shift),tx(215,140+shift,'MODS',11,GRAY)])
    columns=4
    rows=(len(mods)+columns-1)//columns
    for i,mod in enumerate(mods):
        x=215+(i%columns)*157;y=162+(i//columns)*48+shift
        shape,color,caption=icons.get(mod,('M0 0h10v10H0z',MINT,''))
        parts.extend([f'<g class="quest-entry" style="--wait:{i*.09:.2f}s">'
                      f'<path transform="translate({x} {y-11})" d="{shape}" fill="{color}" fill-rule="evenodd"/>'
                      +tx(x+20,y,shorten(mod,16),14,WHITE)+tx(x+20,y+18,caption,11.5,GRAY)+'</g>'])
    footer=190+shift+max(0,rows-1)*48
    parts.extend([rule(215,837,footer),tx(215,footer+25,'# '+shorten(profile['玩家笔记'],41),13,MINT,'class="dim"'),
                  anchor(PROFILE+'/ftb-quests-preview','FTB Quests 任务编辑器',
                         tx(837,footer+25,'~/ftb-quests-preview/ ↗',12,CYAN,'text-anchor="end"'))])
    css=('@media(prefers-reduced-motion:no-preference){.quest-entry{animation:entry .35s ease-out var(--wait) backwards}}'
         '@keyframes entry{from{opacity:.25;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}')
    return card(title,'整合包：'+profile['整合包']+'。模组：'+profile['熟悉的模组']+'。'+profile['玩家笔记'],
                footer+46,parts,css)





GAME_MOTION = """
.saber-lids,.np-last,.np-full{opacity:0}
@media(prefers-reduced-motion:no-preference){
.saber-lids{animation:saber-blink 8.8s linear infinite}
.np-last,.np-full{animation:charged 7.6s step-end infinite}
.np-low{animation:charging 7.6s step-end infinite}}
@keyframes saber-blink{0%,32%,35.8%,82%,85.8%,100%{opacity:0}33.3%,34.5%,83.3%,84.5%{opacity:1}}
@keyframes charged{0%,76%,100%{opacity:0}77%,96%{opacity:1}}
@keyframes charging{0%,76%,100%{opacity:1}77%,96%{opacity:0}}
"""





def neofetch(data):
    end = datetime.fromisoformat(data['end'])
    created = data.get('created_at')
    uptime = f"{max(0,(end-datetime.fromisoformat(created.replace('Z','+00:00'))).days)} days" if created else '—'
    repos = sum(not repo.get('private',False) for repo in data['repositories']) if 'repositories' in data else data['owned']
    fields = [('user','Insaneeee · Tom Chou',WHITE), ('stack','TypeScript · JavaScript · C#',WHITE),
              ('uptime',uptime,GOLD),('repos',f"{repos} public · {len(data['commits'])} commits",WHITE),
              ('gemini','● active (thinking) · AIza-CaffeineOrCoke',MINT),
              ('openai','● active (coding) · sk-FightingWithKubejs',CYAN),
              ('claude','× failed (403 banned) · said-hi-and-got-banned',RED),
              ('thought','> 403 on claude, falling back to gemini & caffeine.',GRAY)]
    body=[chrome('neofetch --config ~/.config/ai-agents.conf'),mascot()]
    for i,(key,value,color) in enumerate(fields):
        y=68+i*22.6
        body += [tx(329,y,key,14,CYAN),tx(407,y,value,13 if key=='thought' else 14,color,'class="dim"' if key=='thought' else '')]
        if key=='gemini':
            body.append(spinner(386,y))
    body.append(languages(data.get('language_bytes',{})))
    css=('@media(prefers-reduced-motion:no-preference){.spinner{animation:spin 1.25s steps(10,end) infinite}'
         '.pupils{animation:glance 6.8s steps(2,end) infinite}}@keyframes spin{to{transform:translateY(-140px)}}'
         '@keyframes glance{0%,66%,89%,100%{transform:translateX(0)}72%,83%{transform:translateX(5px)}}')
    desc = '; '.join(f'{key}: {value}' for key,value,_ in fields)
    return card('neofetch · AI agents',desc+'; MEOW, Gemini, OpenAI, Claude.',300,body,css+PORTRAIT_CSS)


def heatmap(first,last,counts):
    monday=first-timedelta(days=first.weekday())
    weeks=(last-monday).days//7+1
    x,y=224,70
    pitch=min(11.6,612/weeks)
    colors=('#202731','#194937','#237249','#42a967',MINT)
    parts=[f'<defs><rect id="day" width="{pitch-1.9:.2f}" height="9.7" rx="1.7"/></defs>',
           f'<g id="calendar" data-start="{first}" data-end="{last}" fill="{colors[0]}">']
    labels=[]
    for week in range(weeks):
        start=monday+timedelta(weeks=week)
        for k in range(7):
            day=start+timedelta(days=k)
            if not first<=day<=last:
                continue
            if day.day==1 and week<weeks-1:
                labels.append(tx(x+week*pitch,61,day.strftime('%b'),11,GRAY))
            n=counts[day.isoformat()]
            fill=f' fill="{colors[1 if n==1 else 2 if n<5 else 3 if n<10 else 4]}"' if n else ''
            tag=f'<use href="#day" x="{x+week*pitch:.2f}" y="{y+11.5*k:g}"{fill}'
            parts.append(tag+f' data-count="{n}"><title>{day} · {n}</title></use>' if n else tag+'/>')
    return ''.join(parts+['</g>',*labels])


def age(value,end):
    secs=max(0,int((end-datetime.fromisoformat(value.replace('Z','+00:00'))).total_seconds()))
    for scale,unit in ((86400,'d'),(3600,'h'),(60,'m')):
        if secs>=scale:
            return f'{secs//scale}{unit} ago'
    return 'now'


def anchor(url,title,body):
    return f'<a href="{escape(url,quote=True)}"><title>{escape(title)}</title>{body}</a>'


def activity(data):
    first=date.fromisoformat(data['start'])
    end=datetime.fromisoformat(data['end'])
    rows=data['commits']
    counts=Counter(row['time'][:10] for row in rows)
    metrics=[(len(rows),'commits'),(len(counts),'active days'),(len({r['repo'] for r in rows}),'repos')]
    body=[chrome('cat activity/365d.ansi',f'{first} .. {end.date()}')]
    for i,(n,label) in enumerate(metrics):
        y=72+32*i
        body.extend([tx(24,y,shorten(str(n),8),23,WHITE,'class="bold"'),tx(101,y-1,label,12,GRAY)])
    body += [heatmap(first,end.date(),counts),rule(22,838,158.5),tx(23,180,'❯ git log -4 --oneline',14,CYAN)]
    recent=rows[:4]
    tags=[shorten(r['repo'],20) for r in recent]
    repo_width=max((cells(tag) for tag in tags),default=0)*7.6+22
    msg_x=124+repo_width+13
    for i,(row,tag) in enumerate(zip(recent,tags)):
        y=202+i*22
        badge='['+tag+']'
        line=(f'<circle cx="28" cy="{y-4}" r="3.2" fill="{MINT if not i else GRAY}"/>'
              +tx(44,y,row['sha'][:7],13,MINT)
              +tx(124,y,badge,12.5,CYAN)
              +tx(msg_x,y,shorten(row['title'],int((758-msg_x)/(13.3*.63))),13.3)
              +tx(836,y,age(row['time'],end),12,GRAY,'text-anchor="end"'))
        body.append(anchor(row['url'],row['title'],line))
    if not recent:
        body.append(tx(44,209,'(no public commits in the last 365 days)',13,GRAY))
    body.extend([rule(22,838,280.5),tx(23,304,'❯ ls ~/projects',13,GRAY)])
    available={r['name'] for r in data['repositories']} if 'repositories' in data else set(PROJECTS)
    x=166
    for name,color in zip(PROJECTS,(MINT,CYAN,GOLD,CYAN)):
        if name not in available:
            continue
        body.append(anchor(PROFILE+'/'+quote(name),name,tx(x,304,name+'/',12.5,color)))
        x+=(len(name)+1)*7.6+19
    desc=' · '.join(f'{n} {label}' for n,label in metrics)
    return card('365d · git log · projects',desc+'; '+'; '.join(r['title'] for r in recent),321,body)


def render_terminal(data,assets,write):
    target=Path(assets)/'terminal'
    target.mkdir(parents=True,exist_ok=True)
    for name,render in [('banner',banner),('neofetch',neofetch),('chaldeas',master_record),('minecraft',quest_book),('activity',activity)]:
        write(target/(name+'.svg'),render(data))
    badges=[]
    # Use the official flat-square Shields PNGs locally so GitHub's image proxy is not in the request path.
    for label,file,repo in [('TypeScript','typescript','url-to-markdown'),('C#','csharp','Programming-Carrier'),
                           ('ftb-quests-preview','ftb-quests-preview','ftb-quests-preview'),
                           ('fgo-np-calculator','fgo-np-calculator','fgo-np-calculator')]:
        badges.append(f'[![{label}](./assets/badges/{file}.png)]({PROFILE}/{repo})')
    return ('![1nsaneeee · 写点工具，也做游戏](./assets/terminal/banner.svg)\n\n'
            +' '.join(badges)+'\n\n![neofetch · Tom Chou 与三位 AI](./assets/terminal/neofetch.svg)\n\n'
            +'[![迦勒底御主档案](./assets/terminal/chaldeas.svg)]'
            +f'(https://raw.githubusercontent.com/{OWNER}/{OWNER}/main/assets/terminal/chaldeas.svg)\n\n'
            +'[![Minecraft 任务手册](./assets/terminal/minecraft.svg)]'
            +f'(https://raw.githubusercontent.com/{OWNER}/{OWNER}/main/assets/terminal/minecraft.svg)\n\n'
            +'[![365 天活跃度、最近四条提交与项目目录](./assets/terminal/activity.svg)]'
            +f'(https://raw.githubusercontent.com/{OWNER}/{OWNER}/main/assets/terminal/activity.svg)\n')
