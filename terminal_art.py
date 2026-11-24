"""Render the profile as contiguous terminal strips with real HTML links around the rows."""
from datetime import datetime
from html import escape
from pathlib import Path
import re
import unicodedata

BG = '#101816'
TEXT = '#d4dfd6'
MUTED = '#a5b6aa'
MINT = '#91cbb7'
GREEN = '#bfeca8'
SHA = '#d5e799'
PROJECTS = ('ftb-quests-preview', 'url-to-markdown', 'fgo-np-calculator', 'Programming-Carrier')
PROFILE = 'https://github.com/1nsaneeee'


def svg(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="{BG}"/>'
            f'<g font-family="Consolas, Menlo, Liberation Mono, Microsoft YaHei, monospace">{body}</g></svg>\n')


def text(x, y, value, size=15, color=TEXT, bold=False, end=False):
    weight = ' font-weight="bold"' if bold else ''
    align = ' text-anchor="end"' if end else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"{weight}{align}>{escape(value)}</text>'


def prompt(x, y, path, cmd, size):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="bold">'
            f'<tspan fill="{MINT}">{escape(path)} ❯ </tspan>'
            f'<tspan fill="{TEXT}">{escape(cmd)}</tspan></text>')


def picture(stem, description, link=None, banner=False, still=None):
    path = './assets/' if banner else './assets/terminal/'
    ext = 'gif' if banner else 'svg'
    static = ''
    if still:
        name, extension = still
        static = (f'<source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="{path}{name}-mobile.{extension}">'
                  f'<source media="(prefers-reduced-motion: reduce)" srcset="{path}{name}.{extension}">')
    tag = (f'<picture>{static}<source media="(max-width: 600px)" srcset="{path}{stem}-mobile.{ext}">'
           f'<img width="100%" align="top" alt="{escape(description, quote=True)}" src="{path}{stem}.{ext}"></picture>')
    return f'<a href="{escape(link, quote=True)}">{tag}</a>' if link else tag


def ascii_cat(mobile, animated):
    # Eyes, foreleg and cursor column for anticipation, reach, catch and release.
    poses = [
        (0,  'o.o', '>',         17),
        (18, 'o.o', '>',         None),
        (27, 'o.O', '>o',        17),
        (38, 'o.O', '>--o',      16),
        (44, 'O.O', '>------o',  15),
        (53, '^.^', '>---o',     12),
        (62, '^.^', '>o',         9),
        (78, 'o.o', '>o',        13),
        (85, 'o.o', '>',         17),
    ]
    keyframes, sprites = [], []
    for index, (percent, eyes, paw, cursor) in enumerate(poses if animated else poses[:1]):
        keyframes.append(f'{percent}%{{transform:translateY(-{index*64}px)}}')
        lines = [(r'    /\_/\ ', MINT), (f'   ( {eyes} )', TEXT),
                 ('   /   '+paw, GREEN), ('~ (_____)', MINT)]
        sprite = ''.join(f'<text x="{run.start()*9.6:.1f}" y="{line*14}" font-size="16" fill="{color}" '
                         f'textLength="{len(run[0])*9.6:.1f}" lengthAdjust="spacingAndGlyphs">{escape(run[0])}</text>'
                         for line, (chars, color) in enumerate(lines, 1) for run in re.finditer(r'\S+', chars))
        if cursor is not None:
            sprite += f'<rect x="{cursor*9.6}" y="30" width="7" height="13" fill="{SHA}"/>'
        sprites.append(f'<g transform="translate(0 {index*64})">{sprite}</g>')
    style = ('<style>@keyframes catch{' + ''.join(keyframes) + '100%{transform:translateY(0)}}'
             '@media (prefers-reduced-motion:no-preference){.cat{animation:catch 3.6s step-end infinite}}</style>') if animated else ''
    cat_x, cat_y, w, h = (228, 30, 120, 44) if mobile else (656, 29, 173, 59)
    cat = (f'<svg x="{cat_x}" y="{cat_y}" width="{w}" height="{h}" viewBox="0 0 180 64" overflow="hidden">'
           f'{style}<g class="cat" xml:space="preserve" font-family="Consolas,monospace">'
           + ''.join(sprites) + '</g></svg>')
    return cat


def wrapped(value, limit):
    """Approximate monospace display cells, keeping word boundaries when possible."""
    lines, line, cells = [], '', 0
    for word in re.findall(r'\S+\s*', value):
        word_cells = sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in word)
        if line and cells + word_cells > limit:
            lines.append(line.rstrip())
            line, cells = '', 0
        for char in word:
            size = 2 if unicodedata.east_asian_width(char) in 'WF' else 1
            if cells + size > limit:
                lines.append(line.rstrip())
                line, cells = '', 0
            line += char
            cells += size
    if line.strip(): lines.append(line.rstrip())
    return lines or ['']


EDGE = '#425749'
AMBER = '#e9bc78'
BAR = '#1b2922'
BADGES = [('TS', 'TypeScript', '#80b9ed'), ('JS', 'JavaScript', '#e5c968'),
          ('#', 'C#', '#b7a9d1'), ('>_', 'zsh', MINT)]
COMMANDS = [('identity', '~', 'whoami | figlet'), ('profile', '~', 'cat ~/.plan'),
            ('activity', '~/src', 'cat activity/365d.ansi'), ('commits', '~/src', 'git log -5 --graph'),
            ('repos', '~/src', 'tree -d -L 1')]


def frame(width, height, bottom=False):
    path = f'M.5 0V{height} M{width-.5} 0V{height}'
    if bottom:
        path += f' M0 {height-.5}H{width}'
    return f'<path d="{path}" fill="none" stroke="{EDGE}"/>'


def typed_header(index, width, mobile, animated):
    label, cwd, command = COMMANDS[index]
    x, font = (15, 14) if mobile else (28, 17)
    tab = (f'<rect width="{width}" height="28" fill="{BAR}"/>'
           f'<path d="M0 .5H{width} M0 27.5H{width}" stroke="{EDGE}"/>'
           f'<rect x="{x}" y="5" width="21" height="18" rx="2" fill="{MINT if index==0 else "#344d3e"}"/>'
           + text(x+6,18,str(index),12,BG if index==0 else GREEN,True)
           + text(x+30,19,label,14,TEXT,True)
           + text(width-x,18,'tmux / zsh' if not index else cwd,12,MUTED,end=True))
    cell = round(font*.60,2)
    prefix = '❯' if mobile and index==3 else cwd+' ❯'
    left = x+(len(prefix)+1)*cell
    length = round(len(command)*cell,2)
    baseline = 61 if mobile else 67
    start = [1.5, 3.3, 6, 8.5, 11][index]
    finish = start + len(command)*.62
    steps = f'steps({len(command)},end)'
    css = ''
    if animated:
        def keys(prop, first, last):
            return (f'0%,{start}%{{{prop}:{first};animation-timing-function:{steps}}}'
                    f'{finish}%,100%{{{prop}:{last}}}')
        css = ('<style>@keyframes type{' + keys('transform','scaleX(0)','scaleX(1)') + '}'
               '@keyframes travel{' + keys('transform','translateX(0)',f'translateX({length}px)') + '}'
               '@media (prefers-reduced-motion:no-preference){'
               '.reveal{animation:type 9.6s linear infinite}.carriage{animation:travel 9.6s linear infinite}}'
               '</style>')
    tokens = []
    for token in re.finditer(r'\S+',command):
        word = token[0]
        color = GREEN if token.start()==0 else AMBER if word.startswith('-') else MINT if word=='|' else TEXT
        tokens.append(f'<text x="{token.start()*cell:.2f}" y="0" font-size="{font}" fill="{color}" '
                      f'textLength="{len(word)*cell:.2f}" lengthAdjust="spacingAndGlyphs">{escape(word)}</text>')
    clip = (f'<defs><clipPath id="typed"><rect class="reveal" y="{-font}" width="{length+1}" '
            f'height="{font+6}"/></clipPath></defs>')
    typed = (text(x,baseline,prefix,font,MINT,True)
             + f'<g transform="translate({left} {baseline})">{clip}<g clip-path="url(#typed)">'
             + ''.join(tokens) + '</g>'
             + f'<g class="carriage" style="transform:translateX({length}px)"><rect x="1" y="{-font+3}" '
               f'width="{max(3,round(cell*.64))}" height="{font}" fill="{MINT}"/></g></g>')
    return css+tab+typed+(ascii_cat(mobile,animated) if index==3 else '')


def output(body, index):
    # Each linked SVG is a separate document on GitHub. Give sibling rows the same entrance.
    wait = (1.5,3.3,6,8.5,11)[index]*.096 + len(COMMANDS[index][2])*.05952
    initial = '.72' if index>=3 else '.28'
    return (f'<style>@keyframes printout{{from{{opacity:{initial}}}to{{opacity:1}}}}'
            f'@media (prefers-reduced-motion:no-preference){{.out{{animation:printout .16s ease-out {wait:.2f}s backwards}}}}</style>'
            f'<g class="out">{body}</g>')


def badge_row(x, mobile):
    result = ''
    left, y = x, 46
    for i,(mark,label,color) in enumerate(BADGES):
        if mobile and i==2:
            left, y = x, y+31
        length = 43 + len(label)*7
        result += (f'<rect x="{left}" y="{y-17}" width="{length}" height="24" rx="3" fill="{BAR}" stroke="{EDGE}"/>'
                   f'<rect x="{left}" y="{y-17}" width="27" height="24" rx="2" fill="{color}"/>'
                   + text(left+5,y,mark,13,BG,True) + text(left+35,y,label,13,TEXT))
        left += length+8
    return result


def commit_row(rows, i, width, x, font, mobile):
    row = rows[i]
    node = x+5
    left = node + (17 if mobile else 24)
    line_height = 20 if mobile else 22
    title_lines = wrapped(row['title'],int((width-left-x)/(font*.63)))
    ref = row['repo']+'/'+row['branch']
    ref_font = 12 if mobile else 13
    ref_limit = int((width-left-x-18)/(ref_font*.63))
    ref_lines = wrapped(ref,ref_limit) if mobile or len(ref)>45 else [ref]
    inline_ref = not mobile and len(ref)<=45
    last_y = 23+line_height*len(title_lines)
    ref_y = last_y+21
    height = last_y+16 if inline_ref else ref_y+16+(len(ref_lines)-1)*17
    older = i+1<len(rows) and rows[i+1]['sha'] in row.get('parents',()) and rows[i+1]['repo']==row['repo']
    newer = i>0 and row['sha'] in rows[i-1].get('parents',()) and rows[i-1]['repo']==row['repo']
    body = ''
    if newer:
        body += f'<path d="M{node} 0V17" stroke="{MINT}" stroke-width="2"/>'
    if older:
        body += f'<path d="M{node} 17V{height}" stroke="{MINT}" stroke-width="2"/>'
    body += (f'<circle cx="{node}" cy="17" r="4.5" fill="{GREEN if i==0 else BG}" stroke="{MINT}" stroke-width="2"/>'
             + text(left,22,row['sha'][:7],font,AMBER,True)
             + text(width-x,21,datetime.fromisoformat(row['time']).strftime('%m-%d %H:%M'),12,MUTED,end=True))
    for k,line in enumerate(title_lines):
        body += text(left,23+(k+1)*line_height,line,font,TEXT)
    ref_x = left+font*5.4 if inline_ref else left
    for k,line in enumerate(ref_lines):
        y = 21 if inline_ref else ref_y+k*17
        if k==0:
            body += f'<path d="M{ref_x} {y-9}l5 5-5 5" fill="none" stroke="{MINT}" stroke-width="1.5"/>'
        body += text(ref_x+11,y,line,ref_font,MINT)
    if i+1<len(rows):
        body += f'<path d="M{left} {height-.5}H{width-x}" stroke="#26392e"/>'
    return height,body


def render_terminal(data, assets, calendar, write):
    from collections import Counter
    from datetime import date
    end = datetime.fromisoformat(data['end']).date()
    first = date.fromisoformat(data['start'])
    rows = data['commits']
    recent = rows[:5]
    counts = Counter(r['time'][:10] for r in rows)
    stats = f"{len(rows)} commits · {len(counts)} active days · {len({r['repo'] for r in rows})} repos"
    period = f'{first}..{end}'
    path = Path(assets) / 'terminal'
    path.mkdir(exist_ok=True)
    daily = [f'{day}   {count:>3}' for day,count in sorted(counts.items(), reverse=True)]
    stat_lines = [period+'  UTC+8', '本人公开非 Fork 仓库的默认分支，按关联作者和作者日期统计。', 'commits/day   0 / 1 / 2–4 / 5–9 / 10+', *daily]
    stat_body = prompt(26,34,'~/src','cat activity/stat',17)
    for i,line in enumerate(stat_lines):
        stat_body += text(26,70+i*24,line,15,TEXT if i<3 else MINT)
    write(path/'stat.svg',svg(670,93+24*len(stat_lines),stat_body))

    for mobile in (False, True):
        width, x, font = (360,15,14) if mobile else (864,28,16)
        suffix = '-mobile' if mobile else ''
        def put(stem,height,body,bottom=False):
            write(path/(stem+suffix+'.svg'),svg(width,height,body+frame(width,height,bottom)))
        def put_result(stem,height,body,index,bottom=False):
            put(stem,height,body,bottom)
            put(stem+'-print',height,output(body,index),bottom)
        for idx,(name,_,_) in enumerate(COMMANDS):
            for animated in (False,True):
                header_height = (80 if mobile else 91) if idx==3 else (72 if mobile else 80)
                put('pane-'+name+('' if animated else '-still'),header_height,typed_header(idx,width,mobile,animated))

        bio = text(x,17,'给 Minecraft 写模组，给 FGO 算伤害。',font,TEXT)+badge_row(x,mobile)
        put_result('bio',99 if mobile else 70,bio,1,True)

        head = text(x,19,stats,font,GREEN,True)
        head += text(x if mobile else width-x,39 if mobile else 18,period,12,MUTED,end=not mobile)
        chart_y = 49 if mobile else 31
        chart = calendar(first,end,counts,mobile)
        w,h = map(int,re.search(r'viewBox="0 0 (\d+) (\d+)"',chart).groups())
        chart_h = round((width-2*x)*h/w)
        head += chart.replace('<svg ',f'<svg x="{x}" y="{chart_y}" width="{width-2*x}" height="{chart_h}" ',1)
        base_y=chart_y+chart_h+21
        head += text(x,base_y,'↳ --stat',13,MINT)
        head += text(width-x-83,base_y,'−',12,MUTED)
        for k,color in enumerate(('#24362e','#3e7958','#5eac71','#97d588','#d7ed9f')):
            head += f'<rect x="{width-x-69+12*k}" y="{base_y-9}" width="9" height="9" fill="{color}"/>'
        head += text(width-x,base_y,'+',12,MUTED,end=True)
        put_result('overview',base_y+16,head,2,True)

        for i in range(len(recent)):
            height,body = commit_row(recent,i,width,x,font,mobile)
            put_result('commit-'+str(i+1),height,body,3,i==len(recent)-1)
        if not recent:
            put_result('empty-log',41,text(x,23,'(no commits)',font,MUTED),3,True)
        for i,project in enumerate(PROJECTS):
            branch = '└──' if i==len(PROJECTS)-1 else '├──'
            body = text(x,23,branch,font,MUTED)+text(x+font*2.8,23,project+'/',font,MINT,True)
            put_result('repo-'+project,39 if mobile else 36,body,4)
        put('prompt',43,prompt(x,26,'~/src','',font)+text(x+font*5,26,'▌',font,GREEN),True)

    def heading(i):
        label,_,cmd = COMMANDS[i]
        name = 'pane-'+label
        alt = cmd+(' · ASCII 小猫抓光标' if i==3 else '')
        return picture(name,alt,still=(name+'-still','svg'))
    def result(name,alt,link=None):
        return picture(name+'-print',alt,link,still=(name,'svg'))
    panes = [
        [heading(0),picture('wordmark','1nsaneeee · 写点工具，也做游戏。',banner=True,still=('wordmark','png'))],
        [heading(1),result('bio','给 Minecraft 写模组，给 FGO 算伤害。TypeScript · JavaScript · C# · zsh')],
        [heading(2),result('overview',stats+' · '+period+' · 查看按日统计','./assets/terminal/stat.svg')],
        [heading(3)], [heading(4)]
    ]
    for i,row in enumerate(recent):
        desc = f"{row['sha'][:7]} · {row['title']} · {row['repo']}/{row['branch']} · {row['time'][:10]}"
        panes[3].append(result('commit-'+str(i+1),desc,row['url']))
    if not recent:
        panes[3].append(result('empty-log','没有公开提交'))
    panes[4].extend(result('repo-'+p,p+'/',PROFILE+'/'+p) for p in PROJECTS)
    panes[4].append(picture('prompt','~/src ❯'))
    return '\n\n'.join('<p>'+''.join(group)+'</p>' for group in panes)+'\n'
