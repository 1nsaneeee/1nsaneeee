from datetime import date, datetime, timezone, timedelta
from urllib.parse import urlencode,quote
from urllib.request import Request,urlopen
from pathlib import Path
import json, os, subprocess
from terminal_art import render_terminal
owner='1nsaneeee'
base='https://api.github.com'
def pages(path,**params):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'zsh-public-profile'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    for page in range(1,1000):
        url=base+path+'?'+urlencode(dict(params,per_page=100,page=page))
        req=Request(url,headers=headers)
        with urlopen(req,timeout=25) as response:
            body=json.load(response)
        if not isinstance(body,list): raise ValueError('Expected a list from '+path)
        yield from body
        if len(body)<100:break
def snapshot():
    zone=timezone(timedelta(hours=8))
    when=datetime.now(zone); start=when.date()-timedelta(days=364)
    repos=list(pages('/users/'+owner+'/repos',type='owner'))
    all_rows={}; total=0
    for repo in sorted(repos,key=lambda item:item['name'].lower()):
        if repo['fork'] or repo['private']: continue
        total+=1
        slug=repo['name']; route='/repos/'+owner+'/'+quote(slug)+'/commits'
        refs=subprocess.run(['git','ls-remote',repo['clone_url'],'refs/heads/'+repo['default_branch']],check=True,capture_output=True,text=True,timeout=30).stdout.split()
        if not refs:continue
        # The API's author search can omit linked commits visible in the branch history.
        rows=pages(route,sha=refs[0])
        for row in rows:
            if not row.get('author') or row['author']['login'].lower()!=owner.lower():continue
            time=datetime.fromisoformat(row['commit']['author']['date'].replace('Z','+00:00')).astimezone(zone)
            if time>when or time.date()<start:continue
            sha=row['sha']
            all_rows.setdefault(sha,dict(sha=sha,repo=slug,branch=repo['default_branch'],time=time.isoformat(),title=row['commit']['message'].splitlines()[0],url=row['html_url']))
    return {'end':when.isoformat(),'start':start.isoformat(),'owned':len(repos),'scanned':total,'commits':sorted(all_rows.values(),key=lambda row:(row['time'],row['sha']),reverse=True)}
palette=['#24362e','#3e7958','#5eac71','#97d588','#d7ed9f']

def heatmap(first,last,counts,small):
    monday=first-timedelta(days=first.weekday())
    weeks=(last-monday).days//7+1
    ranges=[(0,weeks)] if not small else [(0,weeks//2),(weeks//2,weeks)]
    pitch=14 if not small else 12
    margin=36 if not small else 28
    width=margin+max(b-a for a,b in ranges)*pitch+6
    band=7*pitch+30
    height=band*len(ranges)+2
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
         '<title id="title">每日提交热力图；精确数量见按日明细</title>',
         f'<rect width="{width}" height="{height}" fill="#101816"/>',
         '<g fill="#b0beb2" font-family="ui-monospace,monospace" font-size="10">']
    for band_index,(a,b) in enumerate(ranges):
        top=band*band_index
        labels=[]
        for week in range(a,b):
            day=monday+timedelta(weeks=week)
            visible_day=max(first,day)
            if week==a or any((day+timedelta(days=n)).day==1 for n in range(7)):
                month=max(visible_day,min(day+timedelta(days=6),last))
                if labels and week-labels[-1][0]<3:
                    labels.pop()
                labels.append((week,month))
        for week,month in labels:
            label=f'{month.month}月'
            out.append(f'<text x="{margin+(week-a)*pitch}" y="{top+12}">{label}</text>')
        for row,label in [(0,'一'),(2,'三'),(4,'五'),(6,'日')]:
            out.append(f'<text x="3" y="{top+29+row*pitch}">{label}</text>')
        for week in range(a,b):
            for row in range(7):
                day=monday+timedelta(weeks=week,days=row)
                if not first<=day<=last:continue
                n=counts[day.isoformat()]
                color=palette[0 if not n else 1 if n==1 else 2 if n<5 else 3 if n<10 else 4]
                out.append(f'<rect x="{margin+(week-a)*pitch}" y="{top+19+row*pitch}" width="{pitch-2}" height="{pitch-2}" rx="2" fill="{color}" data-count="{n}" data-date="{day}"><title>{day} · {n} 次提交</title></rect>')
    return ''.join(out)+'</g></svg>'

def local_write(path,content):
    import tempfile
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as temp:
        temp.write(content.encode('utf-8'))
    os.replace(temp.name,path)

def publish_terminal(data, root):
    readme = render_terminal(data, root / 'assets', heatmap, local_write)
    local_write(root / 'README.md', readme)


def refresh():
    data = snapshot()
    publish_terminal(data, Path(__file__).resolve().parent)
    print(f"Updated {len(data['commits'])} commits through {data['end'][:10]}.")


if __name__ == '__main__':
    refresh()
