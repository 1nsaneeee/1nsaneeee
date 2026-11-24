"""Pure SVG rendering of a tiled desktop, including responsive crops for GitHub Markdown."""
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
import re
import unicodedata
from xml.etree import ElementTree as ET

BG = '#0c1411'
PANEL = '#101b16'
BAR = '#17271f'
BORDER = '#354b3e'
MINT = '#9bdfbe'
MID = '#75b998'
INK = '#d3e3d9'
DIM = '#91aa9a'
LOW = '#65816f'
RED = '#e06c75'
FONT = "'JetBrains Mono','Fira Code','Cascadia Code',ui-monospace,monospace"
PROJECTS = ('ftb-quests-preview', 'url-to-markdown', 'fgo-np-calculator', 'Programming-Carrier')
PROFILE = 'https://github.com/1nsaneeee'
NOTES = [
    '> checking minecraft mod mixins & fgo np damage formula...',
    '> warn: claude.service crashed (403 banned). falling back to gemini & caffeine.',
    '> conclusion: ship it first, fix bugs in next commit.',
]
ENV = [('GEMINI', 'CaffeineOrCoke-ThatsAQuestion', '[200 OK]'),
       ('OPENAI', 'ModdingMCAndFightingWithKubejs', '[200 OK]'),
       ('CLAUDE', 'said-hi-and-got-instantly-banned', '[403 BANNED]')]
BRAILLE = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'


def cells(value):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in value)


def wrap(value, limit):
    lines, line = [], ''
    for token in re.findall(r'\S+\s*', value):
        if line and cells(line+token.rstrip()) > limit:
            lines.append(line.rstrip())
            line = ''
        for c in token:
            if cells(line+c)>limit:
                if line.strip():
                    lines.append(line.rstrip())
                line=''
            line += c
    if line.strip():
        lines.append(line.rstrip())
    return lines or ['']


def shorten(value, limit):
    if cells(value)<=limit:
        return value
    line = ''
    for c in value:
        if cells(line+c)>limit-1:
            break
        line += c
    return line+'…'


def t(x, y, value, size=13, color=INK, *, bold=False, anchor='start', cls='', attrs=''):
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{700 if bold else 400}" class="{cls}" {attrs}>{escape(str(value))}</text>')


def rect(x,y,w,h,fill,extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def path(d, color=BORDER, width=1, extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'


def link(url, content, label):
    target='' if url.startswith('#') else ' target="_blank" rel="noopener"'
    return f'<a href="{escape(url,quote=True)}"{target} aria-label="{escape(label,quote=True)}"><title>{escape(label)}</title>{content}</a>'


def icon(kind,x,y,r=6,color=MINT):
    if kind=='gemini':
        shape='<path d="M0 -7Q1 -1 7 0Q1 1 0 7Q-1 1 -7 0Q-1 -1 0 -7Z" fill="currentColor"/>'
    elif kind=='openai':
        shape=(path('M0 -7L6 -3.5V3.5L0 7L-6 3.5V-3.5Z M-3 -2L0 -4L3 -2V2L0 4L-3 2Z','currentColor',1.25))
    else:
        shape=''.join(path('M0 -6.5V-2','currentColor',1.5,f'transform="rotate({angle})"') for angle in range(0,360,45))
    return f'<g transform="translate({x} {y}) scale({r/7:.3f})" color="{color}">{shape}</g>'


def spinner(x,y,key,animated):
    # Braille glyphs as vector dots: identical metrics even on systems without a Braille font.
    pts=[(0,0),(0,3),(0,6),(3,0),(3,3),(3,6),(0,9),(3,9)]
    glyphs=[]
    for i,ch in enumerate(BRAILLE if animated else BRAILLE[:1]):
        bits=ord(ch)-0x2800
        dots=''.join(f'<circle cx="{px+2}" cy="{py+2}" r="1.25" fill="{MINT}"/>' for b,(px,py) in enumerate(pts) if bits&(1<<b))
        glyphs.append(f'<g transform="translate(0 {i*14})">{dots}</g>')
    return (f'<svg x="{x}" y="{y-12}" width="9" height="14" viewBox="0 0 9 14" overflow="hidden">'
            f'<title>{BRAILLE[0]}</title><g class="spin" id="spin-{key}">'+''.join(glyphs)+'</g></svg>')


def command(x,y,cmd,size=14,typed=False,animated=True):
    cell=size*.6
    n=len(cmd)
    width=n*cell
    tokens=[]
    for token in re.finditer(r'\S+',cmd):
        val=token[0]
        color=MINT if token.start()==0 else DIM if val in ('|','--user','-5','--graph') else INK
        tokens.append(t(token.start()*cell,0,val,size,color,attrs=f'textLength="{len(val)*cell:.2f}" lengthAdjust="spacingAndGlyphs"'))
    prefix=t(x,y,'❯',size,MID,bold=True)
    content=''.join(tokens)
    if typed:
        content=(f'<defs><clipPath id="type-mask"><rect y="{-size}" width="{width+1}" height="{size+5}" '
                 f'class="reveal"/></clipPath></defs><g clip-path="url(#type-mask)">{content}</g>'
                 f'<g class="type-caret" style="transform:translateX({width}px)">'
                 +rect(2,-size+3,6,size,MINT,'class="blink"')+'</g>')
    return prefix+f'<g transform="translate({x+17} {y})">{content}</g>'


def stylesheet(animated):
    base=('text{font-family:'+FONT+'}a{text-decoration:none}a:hover .ref{text-decoration:underline}'
          '.note{font-style:italic}.fold-show{display:none}#thoughts-folded:target~g .thoughts{display:none}'
          '#thoughts-folded:target~g .fold-show{display:inline}#thoughts-folded:target~g .fold-hide{display:none}')
    if animated:
        base+=('@media(prefers-reduced-motion:no-preference){'
               '.reveal{animation:typing 1.05s steps(15,end) .06s both}'
               '.type-caret{animation:travel 1.05s steps(15,end) .06s both}'
               '.blink{animation:blink 1.1s steps(1,end) infinite}'
               '.spin{animation:spin 1.4s steps(10,end) infinite}'
               '.open-eye{animation:eye 4.7s step-end infinite}.closed-eye{animation:lid 4.7s step-end infinite}'
               '.paw-long{animation:paw 4.7s step-end infinite}.paw-short{animation:rest 4.7s step-end infinite}'
               '.prey{animation:prey 4.7s step-end infinite}'
               '.sweep{animation:sweep 5.4s linear 1.15s infinite}'
               '.restore{animation:restore .32s ease-out var(--delay,.14s) backwards}'
               '.note{animation:stream .22s ease-out var(--delay,1.1s) backwards}}'
               '@keyframes typing{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
               '@keyframes travel{from{transform:translateX(0)}to{transform:translateX(126px)}}'
               '@keyframes blink{50%{opacity:0}}@keyframes spin{to{transform:translateY(-140px)}}'
               '@keyframes eye{0%,97%{opacity:1}94%{opacity:0}}@keyframes lid{0%,97%{opacity:0}94%{opacity:1}}'
               '@keyframes sweep{0%{transform:translateX(70px)}36%,100%{transform:translateX(-2px)}}'
               '@keyframes paw{0%,70%{opacity:0}40%{opacity:1}}@keyframes rest{0%,70%{opacity:1}40%{opacity:0}}'
               '@keyframes prey{0%,80%{transform:translateX(5px)}40%{transform:translateX(0)}70%{transform:translateX(-14px)}}'
               '@keyframes restore{from{opacity:.35}to{opacity:1}}@keyframes stream{from{opacity:0}to{opacity:1}}')
    return '<style>'+base+'</style>'


# A pixel alphabet gives the title a portable silhouette independent of installed fonts.
GLYPHS={'I':['11111','00100','00100','00100','00100','00100','11111'],
        'n':['00000','00000','11110','11011','11011','11011','11011'],
        's':['00000','00000','01111','11000','01110','00011','11110'],
        'a':['00000','00000','01110','00011','01111','11011','01111'],
        'e':['00000','00000','01110','11011','11111','11000','01111']}
def wordmark(x,y,w):
    d=[]
    for k,ch in enumerate('Insaneeee'):
        for j,row in enumerate(GLYPHS[ch]):
            for run in re.finditer('1+',row):
                d.append(f'M{k*6+run.start()} {j}h{len(run[0])}v1h-{len(run[0])}Z')
    letters=''.join(d)
    mark=['10001','00100','01110','10001','00100']
    pixels=''.join(rect(59+i,j+.35,1,1,MID) for j,row in enumerate(mark) for i,q in enumerate(row) if q=='1')
    return (f'<g transform="translate({x} {y}) scale({w/65:.4f})"><defs>'
            '<filter id="phosphor" x="-9%" y="-45%" width="118%" height="200%">'
            f'<feDropShadow dx="0" dy="0" stdDeviation=".34" flood-color="{MINT}" flood-opacity=".36"/></filter>'
            f'<clipPath id="letters"><path d="{letters}"/></clipPath>'
            f'<linearGradient id="shine"><stop stop-color="{MINT}" stop-opacity="0"/>'
            '<stop offset=".55" stop-color="#dbf8e7"/><stop offset="1" stop-color="#a4dfc0" stop-opacity="0"/></linearGradient>'
            f'</defs><path d="{letters}" fill="#345746" transform="translate(.4 .5)"/>'
            f'<path d="{letters}" fill="{MINT}" filter="url(#phosphor)"/>'
            '<g clip-path="url(#letters)"><g transform="translate(0 0)">'
            '<path class="sweep" style="transform-box:fill-box;transform:translateX(120px)" '
            'd="M-11 -1H0L-2 8H-13Z" fill="url(#shine)"/></g></g>'+pixels+'</g>')


@dataclass
class Item:
    top:float
    bottom:float
    svg:str


class Pane:
    def __init__(self,width,name,number,*,focus=False,delay=.0):
        self.w,self.name,self.num,self.focus,self.delay=width,name,number,focus,delay
        self.items=[]
        self.h=0
        self.targets=[]

    def add(self,top,bottom,svg):
        self.items.append(Item(top,bottom,svg))
        self.h=max(self.h,bottom)

    def target(self,key,top,bottom,url,alt):
        self.targets.append((key,top,bottom,url,alt))

    def render(self,x,y,start,end):
        if y+self.h<=start or y>=end:
            return ''
        edge=MINT if self.focus else BORDER
        frame=rect(.5,.5,self.w-1,self.h-1,PANEL,f'fill-opacity=".88" stroke="{edge}" stroke-width="1"')
        chrome=(rect(1,1,self.w-2,28,BAR)+path(f'M1 29H{self.w-1}')+
                rect(12,9,8,8,edge,'rx="1"')+t(28,19,f'{self.num:02} / {self.name}',12,INK,bold=True)+
                t(self.w-14,19,'FOCUSED' if self.focus else ('' if self.num==3 else 'zsh'),10,MINT if self.focus else DIM,anchor='end'))
        visible=''.join(i.svg for i in self.items if y+i.bottom>start and y+i.top<end)
        return (f'<g transform="translate({x} {y})" class="restore" style="--delay:{self.delay}s">'
                +frame+(chrome if start<y+30 else '')+visible+'</g>')


def watermark(x,y,kind):
    rows = (['       .','      /|','   .-/:\\-.','< ::: + ::: >',"   '-\\:/-'","      \\|",'       ˙']
            if kind=='star' else ['   .----.','  / .--. \\',' / / /\\ \\ \\',' \\ \\ \\/ / /','  \\ \'--\' /',"   '----'"])
    return '<g opacity=".05">'+''.join(t(x,y+i*11,r,15,MINT,attrs='xml:space="preserve"') for i,r in enumerate(rows))+'</g>'


def date_of(value):
    return datetime.fromisoformat(value.replace('Z','+00:00'))


def identity(w,animated):
    p=Pane(w,'identity',1,focus=True)
    pad=17
    p.add(46,62,command(pad,58,'whoami | figlet',14,True,animated))
    logo_w=min(w-44,462)
    p.add(74,74+logo_w/65*8,wordmark(pad+2,74,logo_w))
    y=round(77+logo_w/65*8)+24
    p.add(y-15,y+2,command(pad,y,'cat ~/.plan'))
    p.add(y+9,y+27,t(pad,y+25,'给 Minecraft 写模组，给 FGO 算伤害。',15,INK))
    y+=58
    p.add(y-15,y+2,command(pad,y,'fastfetch --logo none'))
    p.add(y+7,y+34,t(pad,y+25,'Stack',12,DIM)+t(pad+62,y+25,'TypeScript / JavaScript / C#',13))
    agents=t(pad,y+48,'Agents',12,DIM)
    cx=pad+65
    for sym,caption in [('gemini','Gemini'),('openai','OpenAI'),('claude','Claude (RIP)')]:
        agents+=icon(sym,cx,y+43,5.2)+t(cx+10,y+48,caption,12,MINT if sym!='claude' else DIM)
        cx+=len(caption)*7.2+25
    p.add(y+34,y+51,agents)
    p.add(y+56,y+75,t(pad,y+71,'Fuel',12,DIM)+t(pad+62,y+71,'40% Coffee / 60% Tokens',13))
    y+=99
    p.add(y-10,y+2,path(f'M{pad} {y-8}H{w-pad}'))
    heading=t(pad+32,y+24,'Thinking... (1.4s)',14,MINT,bold=True)
    p.add(y+6,y+27,spinner(pad+17,y+24,'thoughts',animated)
          +'<g class="fold-hide">'+link('#thoughts-folded',t(pad,y+24,'▾',14,MINT)+heading,'Fold thinking log')+'</g>'
          +'<g class="fold-show">'+link('#thoughts-open',t(pad,y+24,'▸',14,MINT)+heading,'Expand thinking log')+'</g>')
    y+=47
    first=y
    for i,note in enumerate(NOTES):
        lines=wrap(note,int((w-pad*2-13)/(11.5*.62)))
        text=''.join(t(pad+13,y+j*16,line,11.5,DIM,cls='note',attrs=f'style="--delay:{1.12+i*.19}s"') for j,line in enumerate(lines))
        p.add(y-13,y+len(lines)*16,'<g class="thoughts">'+text+'</g>')
        y+=16*len(lines)+4
    p.add(first-12,y-9,'<g class="thoughts">'+path(f'M{pad+2} {first-11}V{y-10}',BORDER,2)+'</g>')
    p.h=y+10
    p.items.insert(0,Item(144,235,watermark(w-151,164,'star')))
    return p


def process_pane(w,data,animated):
    p=Pane(w,'processes',2,delay=.14); x=16
    end=date_of(data['end']).date()
    recent=Counter(r['repo'] for r in data['commits'] if 0<=(end-date_of(r['time']).date()).days<30)
    projects=list(PROJECTS)
    if 'repositories' in data:
        available={r['name']:r for r in data['repositories']}
        projects=[name for name in PROJECTS if name in available]
        extras=sorted((name for name,r in available.items() if not r['fork'] and name not in projects and name!='1nsaneeee'),
                      key=lambda name:(-recent[name],name.lower()))
        projects=(projects+extras)[:len(PROJECTS)]
    peak=max([recent[name] for name in projects]+[1])
    p.add(42,62,command(x,58,'ps -u $USER'))
    state_x,bar_x=w-146,w-89
    p.add(68,83,t(x,79,'PROCESS',10,DIM)+t(state_x,79,'STAT',10,DIM)+t(bar_x,79,'ACT / 30d',10,DIM))
    y=88
    for i,name in enumerate(projects):
        n=recent[name]; on=bool(n); count=max(1,round(7*n/peak)) if on else 0
        label=shorten(name,int((state_x-x-12)/(13*.62)))
        row=t(x,y+25,label,13,INK,cls='ref')+t(state_x,y+25,'RUN' if on else 'IDLE',11.5,MINT if on else DIM)
        row+=''.join(rect(bar_x+k*7,y+17,5,8,MID if k<count else BORDER) for k in range(7))
        row+=t(w-x,y+25,str(n),10.5,DIM,anchor='end')
        row+=path(f'M{x} {y+40}H{w-x}',BAR)
        # The link is on both SVG text and the native Markdown strip.
        url=PROFILE+'/'+name
        p.add(y,y+46,link(url,row,name))
        p.target(f'repo-{i}',y,y+46,url,f"{name} · {'RUN' if on else 'IDLE'} · {n} commits / 30d")
        y+=46
    y+=26
    p.add(y-18,y+2,command(x,y,'systemctl --user list-units "*ai*"',12.5))
    for i,(key,name,status) in enumerate([('gemini','Gemini','active (thinking)'),('openai','OpenAI','active (coding)'),('claude','Claude','failed (banned)')]):
        yy=y+26+i*23; col=RED if key=='claude' else MINT
        row=t(x,yy,'×' if key=='claude' else '●',12,col)+icon(key,x+26,yy-4,5.5,col)
        row+=t(x+39,yy,name,13,INK if key!='claude' else RED)+t(x+114,yy,status,12,col)
        if key=='gemini': row+=spinner(x+245,yy,'gemini',animated)
        p.add(yy-14,yy+3,row)
    y+=103
    p.add(y-15,y+2,command(x,y,'cat .env.local'))
    for i,(name,value,status) in enumerate(ENV):
        yy=y+24+i*20
        key=f'{name}_KEY="{value}"'
        usable=w-2*x-90
        size=min(11,usable/(len(key)*.61))
        body=t(x,yy,key,max(10,size),DIM,attrs=f'textLength="{min(usable,len(key)*size*.60):.2f}" lengthAdjust="spacingAndGlyphs"')
        body+=t(w-x,yy,status,10.5,RED if name=='CLAUDE' else MINT,anchor='end',bold=True)
        p.add(yy-13,yy+3,body)
    p.h=y+89
    p.items.insert(0,Item(195,288,watermark(w-115,206,'hex')))
    return p




def calendar_pane(w,data,calendar):
    p=Pane(w,'activity / 365d',3,delay=.24); x=16
    rows=data['commits']; counts=Counter(r['time'][:10] for r in rows)
    first=date.fromisoformat(data['start']); last=date_of(data['end']).date()
    p.add(42,62,command(x,58,'cat activity/365d.ansi'))
    fields=[(len(rows),'commits'),(len(counts),'active days'),(len({r['repo'] for r in rows}),'repos')]
    for i,(n,label) in enumerate(fields):
        xx=x+i*(w-2*x)/3
        p.add(76,127,t(xx,101,str(n),29,MINT if i==0 else INK,bold=True)+t(xx,121,label,11,DIM))
    p.add(133,153,t(x,148,f'{first} .. {last}',11,DIM))
    stock=ET.fromstring(calendar(first,last,counts,True))
    _,_,cw,ch=map(int,stock.get('viewBox').split())
    s=(w-2*x)/cw
    top=163
    # Split by calendar row so a README slice embeds only cells it actually displays.
    bands={}
    for item in stock.iter():
        tag=item.tag.rsplit('}',1)[-1]
        if tag=='text':
            xx,yy=float(item.get('x')),float(item.get('y'))
            bounds=(yy-11,yy+2); content=t(xx,yy,item.text or '',10,DIM)
        elif tag=='rect' and 'data-date' in item.attrib:
            xx,yy,ww,hh=[float(item.get(attr)) for attr in ('x','y','width','height')]
            day=item.get('data-date'); count=item.get('data-count')
            bounds=(yy,yy+hh);content=(f'<rect x="{xx:g}" y="{yy:g}" width="{ww:g}" height="{hh:g}" rx="1.5" '
                        f'fill="{item.get("fill")}" data-date="{day}" data-count="{count}"><title>{day} · {count}</title></rect>')
        else:
            continue
        bands.setdefault(bounds,[]).append(content)
    for (a,b),parts in bands.items():
        p.add(top+a*s,top+b*s,f'<g transform="translate({x} {top}) scale({s:.5f})">'+''.join(parts)+'</g>')
    foot=round(top+ch*s)+17
    p.add(foot-14,foot+4,t(x,foot,'0',10,DIM)+''.join(rect(x+12+k*12,foot-9,9,9,c) for k,c in enumerate(
          ('#24362e','#395c4b','#4a836c','#70af93','#a1dbc0')))+t(x+78,foot,'10+',10,DIM))
    p.h=foot+56
    return p


def age(value,end):
    secs=max(0,int((end-date_of(value)).total_seconds()))
    for scale,suffix in [(86400,'d'),(3600,'h'),(60,'m')]:
        if secs>=scale: return f'{secs//scale}{suffix} ago'
    return 'now'


def diff_bar(stats):
    if not stats or 'additions' not in stats or 'deletions' not in stats:
        return ''
    plus,minus=stats['additions'],stats['deletions']
    if not plus+minus: return '·····'
    positives=round(5*plus/(plus+minus))
    if plus and minus: positives=max(1,min(4,positives))
    return '+'*positives+'−'*(5-positives)


def cat(x,y,animated):
    head=t(0,0,r'/\_/\ ',11,MID)
    eyes=t(-1,11,'( o.o )',11,MINT,cls='open-eye')
    if animated:
        eyes+=t(-1,11,'( -.- )',11,MINT,cls='closed-eye',attrs='opacity="0"')
    paw=t(4,22,'>o',11,MID,cls='paw-short')
    if animated:
        paw+=t(4,22,'>---o',11,MID,cls='paw-long',attrs='opacity="0"')
    paw+=rect(40,14,4,9,MINT,'class="prey"')
    return f'<g transform="translate({x} {y})">{head}{eyes}{paw}</g>'


def journal(w,data,animated):
    p=Pane(w,'commits.log',4,delay=.33); x=16; left=x+19
    p.add(43,61,command(x,58,'git log -5 --graph'))
    rows=data['commits'][:5]; y=98; end=date_of(data['end'])
    for i,row in enumerate(rows):
        sha=row['sha']; meta_y=y+16
        title=wrap(row['title'],int((w-left-x)/(13.5*.62)))
        if len(title)>2:
            title=[title[0],shorten(' '.join(title[1:]),int((w-left-x)/(13.5*.62)))]
        height=41+18*len(title)
        node=x+3
        lines=''
        if i and rows[i-1]['repo']==row['repo'] and sha in rows[i-1].get('parents',[]):
            lines+=path(f'M{node} {y}V{meta_y-4}',MID,1.5)
        if i+1<len(rows) and rows[i+1]['repo']==row['repo'] and rows[i+1]['sha'] in row.get('parents',[]):
            lines+=path(f'M{node} {meta_y-4}V{y+height}',MID,1.5)
        lines+=f'<circle cx="{node}" cy="{meta_y-4}" r="3.8" fill="{MINT if i==0 else PANEL}" stroke="{MID}" stroke-width="1.5"/>'
        lines+=t(left,meta_y,sha[:7],13,MINT,bold=True)
        xx=left+66; max_ref=max(8,int((w-xx-100)/6.4))
        capsule='['+shorten(row['repo'],min(21,max_ref-2))+']'
        capw=cells(capsule)*6.6+9
        lines+=rect(xx,meta_y-12,capw,16,BAR,f'rx="2" stroke="{BORDER}"')+t(xx+4,meta_y,capsule,11,DIM)
        lines+=t(w-x,meta_y,age(row['time'],end),11,DIM,anchor='end')
        for j,line in enumerate(title):
            lines+=t(left,y+38+18*j,line,13.5,INK,cls='ref')
        stats=row.get('stats'); bars=diff_bar(stats)
        if bars:
            sy=y+height-4
            lines+=('<g><title>'+escape(f"+{stats['additions']} / -{stats['deletions']}")+'</title>'
                    +t(w-x-46,sy,f"+{stats['additions']} −{stats['deletions']}",10.5,DIM,anchor='end')
                    +t(w-x,sy,bars,12,MID,anchor='end')+'</g>')
        lines+=path(f'M{left} {y+height-.5}H{w-x}',BAR)
        if row.get('ai'):
            lines+=icon(row['ai'],left+3,y+height-7,3,LOW)
        desc=f"{sha[:7]} · {row['repo']}/{row['branch']} · {row['title']} · {row['time'][:10]}"
        p.add(y,y+height,link(row['url'],lines,desc))
        p.target(f'commit-{i}',y,y+height,row['url'],desc)
        y+=height
    if not rows:
        p.add(y,y+30,t(x,y+17,'(no public commits)',13,DIM));y+=30
    p.h=y+53
    return p


def status_bar(w,data,mobile):
    x=15; y=20
    body=rect(.5,.5,w-1,35 if not mobile else 61,BAR,f'stroke="{BORDER}"')
    body+=t(x,y,'[0] 0:zsh*  1:nvim-',12,MINT,bold=True)
    start=14 if mobile else 231
    yy=47 if mobile else 21
    for label in ('TS','C#','Minecraft','FGO'):
        ww=18+len(label)*7
        body+=f'<path d="M{start} {yy-13}h{ww-6}l6 8-6 8H{start}Z" fill="#294236"/>'
        body+=t(start+6,yy-1,label,11.5,MINT,bold=True);start+=ww+4
    created=data.get('created_at')
    uptime=f"{max(0,(date_of(data['end'])-date_of(created)).days)}d" if created else '—'
    body+=t(w-x,y,'uptime '+uptime,11,DIM,anchor='end')
    body+=t(198,20,'|',12,MINT,cls='blink')
    comment='# crawler.note: Insaneeee / 10x dev, powered by coffee.'
    body+=t(1,79 if mobile else 53,comment,8.5,LOW)
    return body,85 if mobile else 60


class Desktop:
    def __init__(self,data,calendar,mobile,animated):
        self.w=420 if mobile else 1080
        self.animated=animated
        gap=10; inside=self.w-2*gap
        left=inside if mobile else 567
        right=inside if mobile else inside-gap-left
        ident=identity(left,animated); proc=process_pane(right,data,animated)
        heat=calendar_pane(left,data,calendar); log=journal(right,data,animated)
        y=38
        if mobile:
            self.panes=[]
            for p in (ident,proc,heat,log):
                self.panes.append((gap,y,p));y+=p.h+gap
        else:
            ident.h=proc.h=max(ident.h,proc.h)
            heat.h=log.h=max(heat.h,log.h)
            next_y=y+ident.h+gap
            self.panes=[(gap,y,ident),(gap+left+gap,y,proc),(gap,next_y,heat),(gap+left+gap,next_y,log)]
            y=next_y+heat.h+gap
        self.status_y=y
        self.status,self.status_h=status_bar(inside,data,mobile)
        self.h=y+self.status_h+4
        # Move both decorative footers to the real pane bottom after the two-column height is known.
        heat.add(heat.h-27,heat.h-5,t(16,heat.h-13,'xxd: '+'Hello from Insaneeee'.encode().hex(),9.5,LOW))
        log.add(log.h-40,log.h-5,cat(log.w-75,log.h-32,animated))
        self.targets={}
        for _,py,p in self.panes:
            for key,start,end,url,alt in p.targets:
                self.targets[key]=(py+start,py+end,url,alt)
        # The stats hit lives in the activity title bar and precedes the first commit in both layouts.
        py=next(py for _,py,p in self.panes if p is heat)
        commits=data['commits']
        stats=f"{len(commits)} commits · {len({r['time'][:10] for r in commits})} active days · {len({r['repo'] for r in commits})} repos"
        self.targets['stats']=(py,py+46,'./assets/terminal/stat.svg',stats+' · 按日提交明细')
        heat.add(5,25,link('https://github.com/1nsaneeee/1nsaneeee/blob/main/assets/terminal/stat.svg',
                           rect(1,1,heat.w-2,27,'transparent')+t(heat.w-15,19,'--stat ↗',11,MINT,anchor='end'),'Daily commit counts'))
        self.description=f"Insaneeee · AI agent desktop · {len(data['commits'])} commits · {data['end'][:10]}"
        self.bar=(t(10,23,'◆',15,MINT)+t(32,23,'hypr / 01',12,MINT,bold=True)
                  +t(121,23,'~/workspace',12,DIM)+t(self.w-10,23,'1nsaneeee@github',12,DIM,anchor='end'))

    def svg(self,start=0,end=None):
        end=self.h if end is None else end
        h=end-start
        out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{h}" viewBox="0 {start} {self.w} {h}" '
             'role="group" aria-labelledby="screen-title">',f'<title id="screen-title">{escape(self.description)}</title>',
             stylesheet(self.animated),
             f'<defs><pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="{MINT}"/></pattern></defs>',
             '<g id="thoughts-folded"/><g id="thoughts-open"/>',rect(0,start,self.w,h,BG),
             rect(0,start,self.w,h,'url(#dots)','opacity=".025"')]
        if start<36:out.append(self.bar)
        for x,y,p in self.panes:
            out.append(p.render(x,y,start,end))
        if end>self.status_y:
            out.append(f'<g transform="translate(10 {self.status_y})">{self.status}</g>')
        return ''.join(out)+'</svg>\n'


def render_terminal(data,assets,calendar,write):
    target=Path(assets)/'terminal'
    dest=target/'desktop'
    dest.mkdir(parents=True,exist_ok=True)
    versions={}
    for mobile in (False,True):
        for animated in (False,True):
            board=Desktop(data,calendar,mobile,animated)
            suffix=('-still' if not animated else '')+('-mobile' if mobile else '')
            versions[suffix]=board
            write(dest/('workspace'+suffix+'.svg'),board.svg())
    first=versions['']
    keys=sorted(first.targets,key=lambda k:first.targets[k][0])
    # GitHub disables nested SVG links when an SVG is used as an image. Keep each actionable
    # output row as its own native Markdown anchor; all crops use the same scene coordinates.
    names=[];last_key=None
    for idx,key in enumerate(keys+['end']):
        band='region-'+str(idx)
        for suffix,board in versions.items():
            start=board.targets[last_key][1] if last_key else 0
            end=board.h if key=='end' else board.targets[key][0]
            if end>start:
                write(dest/(band+suffix+'.svg'),board.svg(start,end))
            else:
                assert end==start
        if any((b.h if key=='end' else b.targets[key][0])>(b.targets[last_key][1] if last_key else 0) for b in versions.values()):
            caption=(first.description+' · 给 Minecraft 写模组，给 FGO 算伤害。TypeScript / JavaScript / C#。'
                     if not idx else 'Gemini thinking · OpenAI coding · Claude failed (banned) · 模拟服务与环境变量'
                     if key=='stats' else '365 天提交热力图 · git log --graph' if key.startswith('commit-')
                     else 'ASCII 小猫 · tmux 会话 · 技术徽章与账号 uptime')
            names.append((band,None,caption))
        if key!='end':
            for suffix,board in versions.items():
                start,end,_,_=board.targets[key]
                write(dest/(key+suffix+'.svg'),board.svg(start,end))
            _,_,url,alt=first.targets[key]
            names.append((key,url,alt))
        last_key=key
    parts=[]
    for stem,url,alt in names:
        base='./assets/terminal/desktop/'+stem
        pic=(f'<picture><source media="(max-width: 900px) and (prefers-reduced-motion: reduce)" srcset="{base}-still-mobile.svg">'
             f'<source media="(prefers-reduced-motion: reduce)" srcset="{base}-still.svg">'
             f'<source media="(max-width: 900px)" srcset="{base}-mobile.svg">'
             f'<img src="{base}.svg" alt="{escape(alt,quote=True)}" width="100%" align="top"></picture>')
        parts.append(f'<a href="{escape(url,quote=True)}">{pic}</a>' if url else pic)
    start=data['start'];last=data['end'][:10]
    days=Counter(r['time'][:10] for r in data['commits'])
    lines=[f'{start} .. {last} / UTC+8','public · non-fork · default branches',*[f'{d}    {n:>4}' for d,n in sorted(days.items(),reverse=True)]]
    stat=''.join(t(18,32+21*i,line,13,MINT if i==0 else INK) for i,line in enumerate(lines))
    sh=48+21*len(lines)
    write(target/'stat.svg',f'<svg xmlns="http://www.w3.org/2000/svg" width="550" height="{sh}" viewBox="0 0 550 {sh}">'+stylesheet(False)+rect(0,0,550,sh,BG)+stat+'</svg>\n')
    return '<p>'+''.join(parts)+'</p>\n'
