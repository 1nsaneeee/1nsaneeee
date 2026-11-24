"""Three self-contained SVG cards for a GitHub profile, rendered from one activity snapshot."""
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
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
.reveal{animation:type 1.08s steps(11,end) both}.caret{animation:travel 1.08s steps(11,end) both}
.blink{animation:blink 1.1s steps(1,end) infinite}.output{animation:answer .23s ease-out 1.08s backwards}
.eyes{animation:eyes 4s step-end infinite}.lid{animation:lid 4s step-end infinite}
.star{animation:twinkle 3.8s ease-in-out infinite}.glint{animation:shine 7.6s ease-in-out 1.5s infinite}
.paw{animation:reach 4s ease-in-out infinite}.mote{animation:dodge 4s ease-in-out infinite}}
@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes tips{from{transform:translateY(0)}to{transform:translateY(var(--travel))}}
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
@media(prefers-reduced-motion:no-preference){
.slide{animation:channel 12s linear infinite;animation-delay:var(--offset)}}
@keyframes channel{0%,23.6%{opacity:1}25%,98.6%{opacity:0}100%{opacity:1}}
@media(prefers-reduced-motion:reduce){.channels{display:none}.contact-sheet{opacity:1}}
"""


def mascot():
    portraits=[('meow','MEOW',MINT,computer_cat()),
               ('gemini','GEMINI',MINT,ascii_mark(GEMINI_MARK,MINT)),
               ('openai','OPENAI',CYAN,ascii_mark(OPENAI_MARK,CYAN)),
               ('claude','CLAUDE / 403',RED,ascii_mark(CLAUDE_MARK,RED))]
    parts=[box(20,53,268,230,BG,8,BORDER),'<defs>']
    for name,_,_,art in portraits:
        parts.append(f'<g id="portrait-{name}">{art}</g>')
    parts.append('</defs><g class="channels">')
    for i,(name,label,color,_) in enumerate(portraits):
        offset=3*i-12 if i else 0
        parts.append(f'<g class="slide{" first" if not i else ""}" style="--offset:{offset}s">')
        parts.append(tx(270,74,label,11,color,'text-anchor="end"'))
        parts.append(f'<use href="#portrait-{name}" transform="translate(61 83)"/>')
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


def artoria():
    # Each cell samples the supplied FGO portrait. Draw same-ink runs together so
    # the crown, eyes and fur retain their shape without embedding a bitmap or font.
    tiles=['<pattern id="saber-cell" patternUnits="userSpaceOnUse" width="1" height="1" '
           'viewBox="0 0 6 7" preserveAspectRatio="none"/>']
    glyph_ids={}
    faces=[]
    for code,color,glyph in SABER_INKS:
        runs=[]
        for y,row in enumerate(SABER_ROWS):
            for run in re.finditer(code+'+',row):
                runs.append(f'M{run.start()} {y}h{len(run[0])}')
        if not runs:
            continue
        if glyph not in glyph_ids:
            glyph_ids[glyph]='char-'+str(len(glyph_ids))
            tiles.append(tx(0,6,glyph,7,'#322727',
                            f'id="{glyph_ids[glyph]}" font-weight="700" opacity=".23"'))
        tile='saber-'+code
        tiles.append(f'<pattern id="{tile}" href="#saber-cell"><path d="M0 0h6v7H0z" fill="{color}"/>'
                     f'<use href="#{glyph_ids[glyph]}"/></pattern>')
        faces.append(f'<path stroke="url(#{tile})" d="{"".join(runs)}"/>')
    return ('<defs>'+''.join(tiles)+'</defs><g transform="translate(0 3) scale(2.12 2.29)" '
            'fill="none" stroke-width="1.015">'+''.join(faces)+'</g>')


def grass_block():
    return ''.join([
        # All three projected edges are 53.1 units, at 30, 150 and 270 degrees.
        game_shape('M9 33.56L55 60.12V113.24L9 86.68Z','loam','#9b846d'),
        game_shape('M55 60.12L101 33.56V86.68L55 113.24Z','soil','#826b57'),
        game_shape('M9 33.56L55 7L101 33.56L55 60.12Z','grass','#84bc78'),
        game_shape('M9 33.56L55 60.12V68L49 65V70L45 68V62L37 57V62L31 58V53L23 49V53L18 50V46L9 41Z',
                   'grass','#76a76c'),
        game_shape('M55 60.12L101 33.56V42L95 46V50L89 54V49L79 55V60L73 64V60L64 65V71L55 75Z',
                   'grass','#598a61'),
        tx(17,72,'+.',7,'#e1c099'),tx(34,80,'#',7,'#93785d'),
        tx(65,82,'/+',7,'#c3a88b'),tx(84,69,'::',7,'#c3a88b'),
        '<path d="M56 28l12-6 13 6-13 6z" fill="#708394" stroke="#a3b8c3"/>'
        '<path d="M56 28l12 6v11l-12-6z" fill="#334553" stroke="#79909f"/>'
        '<path d="M68 34l13-6v11l-13 6z" fill="#1c303e" stroke="#79909f"/>',
        tx(58,38,'=',8,CYAN),tx(70,40,'::',7,MINT),
        '<g class="machine-hop" stroke-linejoin="round">'
        +box(65,10,7,7,'#e1bd96')+box(65,10,7,2,'#705438')+box(70,13,1.4,1.4,'#483c38')
        +'<path d="M66 17h5v6h-5zM63 18h3v5h-3zM71 17h4v3h-4z" fill="#75c4cb"/>'
        '<path d="M66 23h5v6h-2v-4h-1v4h-2z" fill="#94aacf"/></g>',
    ])


def game_saves():
    parts=[game_ink(),rule(22,838,295.5),f'<path d="M431 312v118" stroke="{BORDER}"/>']
    summaries=[]
    saves=[
        (24,artoria(),'阿尔托莉雅 / Saber','~/saves/chaldea','FGO · 最推 EMIYA',GOLD,
         '2018.08.27 被骗入迦勒底。','御主 Lv.155 · 五星从者 60 骑','宝具伤害有公式，抽卡没有。'),
        (443,grass_block(),'minecraft:grass_block','~/saves/overworld','MC · 科技水槽包爱好者',MINT,
         'ATM · 迷厄路 · FTB Series','Mekanism · 工业先锋 · 资源蜜蜂 · AE2','喜欢在机器上蹦蹦跳跳'),
    ]
    for x,art,caption,slot,name,color,line1,line2,aside in saves:
        label_x=x+124
        summaries.append(' '.join((name,line1,line2,aside)))
        parts.extend([f'<g transform="translate({x} 309)">{art}</g>',
                      tx(x+54,437,caption,9,GRAY,'text-anchor="middle"'),
                      tx(label_x,326,slot,12,GRAY),tx(label_x,352,name,16,color,'class="bold"'),
                      tx(label_x,377,line1,14,WHITE),tx(label_x,397,line2,13,WHITE),
                      tx(label_x,424,'# '+aside,13,GRAY,'class="dim"')])
    return ''.join(parts),'；'.join(summaries)


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
    saves_svg,saves_desc=game_saves()
    body.append(saves_svg)
    css=('@media(prefers-reduced-motion:no-preference){.spinner{animation:spin 1.25s steps(10,end) infinite}'
         '.pupils{animation:glance 6.8s steps(2,end) infinite}'
         '.machine-hop{animation:hop 4.2s ease-in-out infinite}}@keyframes spin{to{transform:translateY(-140px)}}'
         '@keyframes hop{0%,9%,26%,31%,46%,100%{transform:translateY(0)}17%{transform:translateY(-8px)}39%{transform:translateY(-5px)}}'
         '@keyframes glance{0%,66%,89%,100%{transform:translateX(0)}72%,83%{transform:translateX(5px)}}')
    desc = '; '.join(f'{key}: {value}' for key,value,_ in fields)
    return card('neofetch · AI agents',desc+'; MEOW, Gemini, OpenAI, Claude; '+saves_desc,453,body,css+PORTRAIT_CSS)


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
    for name,render in [('banner',banner),('neofetch',neofetch),('activity',activity)]:
        write(target/(name+'.svg'),render(data))
    badges=[]
    # Use the official flat-square Shields PNGs locally so GitHub's image proxy is not in the request path.
    for label,file,repo in [('TypeScript','typescript','url-to-markdown'),('C#','csharp','Programming-Carrier'),
                           ('ftb-quests-preview','ftb-quests-preview','ftb-quests-preview'),
                           ('fgo-np-calculator','fgo-np-calculator','fgo-np-calculator')]:
        badges.append(f'[![{label}](./assets/badges/{file}.png)]({PROFILE}/{repo})')
    return ('![1nsaneeee · 写点工具，也做游戏](./assets/terminal/banner.svg)\n\n'
            +' '.join(badges)+'\n\n![neofetch · Tom Chou、AI agents 与 FGO / Minecraft 游戏存档](./assets/terminal/neofetch.svg)\n\n'
            +'[![365 天活跃度、最近四条提交与项目目录](./assets/terminal/activity.svg)]'
            +f'(https://raw.githubusercontent.com/{OWNER}/{OWNER}/main/assets/terminal/activity.svg)\n')
