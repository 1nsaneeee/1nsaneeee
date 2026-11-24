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


def cat_heading(mobile, x, font, animated):
    if mobile:
        heading = prompt(x, 25, '~/src', 'head -5', font) + text(x+16, 46, 'activity/commits.log', font)
    else:
        heading = prompt(x, 42, '~/src', 'head -5 activity/commits.log', font)

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
    cat_x, cat_y, w, h = (200, 0, 147, 55) if mobile else (642, 2, 180, 64)
    cat = (f'<svg x="{cat_x}" y="{cat_y}" width="{w}" height="{h}" viewBox="0 0 180 64" overflow="hidden">'
           f'{style}<g class="cat" xml:space="preserve" font-family="Consolas,monospace">'
           + ''.join(sprites) + '</g></svg>')
    return heading + cat


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


def render_terminal(data, assets, calendar, write):
    from collections import Counter
    from datetime import date
    end = datetime.fromisoformat(data['end']).date()
    first = date.fromisoformat(data['start'])
    rows = data['commits']
    counts = Counter(r['time'][:10] for r in rows)
    stats = f"{len(rows)} commits · {len(counts)} active days · {len({r['repo'] for r in rows})} repos"
    period = f'{first}..{end}'
    path = Path(assets) / 'terminal'
    path.mkdir(exist_ok=True)
    stat_target = './assets/terminal/stat.svg'
    daily = [f'{day}   {count:>3}' for day,count in sorted(counts.items(), reverse=True)]
    stat_lines = [period+'  UTC+8', '本人公开非 Fork 仓库的默认分支，按关联作者和作者日期统计。', 'commits/day   0 / 1 / 2–4 / 5–9 / 10+', *daily]
    stat_body = prompt(26, 34, '~/src', 'cat activity/stat', 17)
    for i, line in enumerate(stat_lines):
        stat_body += text(26, 70 + i*24, line, 15, TEXT if i<3 else MINT)
    write(path/'stat.svg', svg(670, 93+24*len(stat_lines), stat_body))

    for mobile in (False, True):
        width, x, font = (360, 15, 13) if mobile else (864, 31, 16)
        suffix = '-mobile' if mobile else ''
        def put(stem, height, body):
            write(path/(stem+suffix+'.svg'), svg(width,height,body))
        head = prompt(x, 22, '~', 'cat ~/.plan', font)
        head += text(x, 48, '给 Minecraft 写模组，给 FGO 算伤害。', font)
        head += text(x, 69, 'TypeScript / JavaScript / C#', font-1, MUTED)
        head += prompt(x, 106, '~/src', 'cat activity/365d.ansi', font)
        head += text(x, 132, stats, font, GREEN, True)
        chart_y = 148
        if mobile:
            head += text(x, 151, period, 11, MUTED)
            chart_y = 164
        else:
            head += text(width-x, 132, period, 13, MUTED, end=True)
        chart = calendar(first,end,counts,mobile)
        w,h = map(int,re.search(r'viewBox="0 0 (\d+) (\d+)"',chart).groups())
        render_h = round((width-2*x)*h/w)
        chart = chart.replace('<svg ', f'<svg x="{x}" y="{chart_y}" width="{width-2*x}" height="{render_h}" ',1)
        head += chart
        bottom = chart_y + render_h
        head += text(x, bottom+22, '▸ --stat', font-1, MINT)
        put('overview', bottom+35, head)

        for stem, animated in [('log-cat', True), ('log', False)]:
            put(stem, 60 if mobile else 72, cat_heading(mobile, x, font, animated))
        for i, row in enumerate(rows[:5]):
            offset = x+(68 if mobile else 86)
            limit = int((width-x-offset)/(font*.64))
            lines = wrapped(row['title'],limit)
            body = text(x, 18, row['sha'][:7], font, SHA, True)
            for j,line in enumerate(lines):
                body += text(offset,18+j*21,line,font)
            label_y = 18+(len(lines)-1)*21+19
            stamp = datetime.fromisoformat(row['time'])
            body += text(offset,label_y, f"{stamp:%Y-%m-%d %H:%M} · {row['repo']}", font-2, MUTED)
            put('commit-'+str(i+1), label_y+13, body)
        put('tree',56,prompt(x,31,'~/src','tree -d -L 1',font)+text(x,51,'.',font,MUTED))
        for i,project in enumerate(PROJECTS):
            branch = '└──' if i==len(PROJECTS)-1 else '├──'
            put('repo-'+project,32,text(x,21,branch,font,MUTED)+text(x+font*2.8,21,project+'/',font,MINT,True))
        put('prompt',52,prompt(x,30,'~/src','',font)+text(x+font*5.05,30,'▌',font,GREEN))

    strips = [picture('zsh','1nsaneeee · 写点工具，也做游戏。',banner=True,still=('zsh','png')),
              picture('overview','给 Minecraft 写模组，给 FGO 算伤害。TypeScript / JavaScript / C#。'+stats+' · '+period+'；查看每日统计',stat_target),
              picture('log-cat','~/src ❯ head -5 activity/commits.log · ASCII 小猫伸爪抓光标',still=('log','svg'))]
    for i,row in enumerate(rows[:5]):
        desc = f"{row['sha'][:7]} · {row['title']} · {row['repo']} · {row['time'][:10]}"
        strips.append(picture('commit-'+str(i+1),desc,row['url']))
    strips.append(picture('tree','~/src ❯ tree -d -L 1'))
    strips.extend(picture('repo-'+p,p+'/',PROFILE+'/'+p) for p in PROJECTS)
    strips.append(picture('prompt','~/src ❯'))
    # One HTML paragraph with top-aligned 100% images. GitHub adds margins to separate paragraphs.
    return '<p>'+''.join(strips)+'</p>\n'

