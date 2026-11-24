"""Fetch public GitHub activity and regenerate Oh My Zsh terminal cards + README.md."""
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import json
import os
import sys

from terminal_art import render_terminal

OWNER = "1nsaneeee"
BASE = "https://api.github.com"


def api(path, **params):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "zsh-public-profile"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    url = BASE + path + ("?" + urlencode(params) if params else "")
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        return json.load(response)


def pages(path, **params):
    for page in range(1, 1000):
        body = api(path, **params, per_page=100, page=page)
        if not isinstance(body, list):
            raise ValueError("Expected a list from " + path)
        yield from body
        if len(body) < 100:
            break


def snapshot():
    zone = timezone(timedelta(hours=8))
    when = datetime.now(zone)
    start = when.date() - timedelta(days=364)
    repos = list(pages("/users/" + OWNER + "/repos", type="owner"))
    all_rows = {}
    total = 0
    language_bytes = Counter()

    for repo in sorted(repos, key=lambda item: item["name"].lower()):
        if repo["fork"] or repo["private"] or repo.get("size", 0) == 0:
            continue
        total += 1
        slug = repo["name"]
        route = "/repos/" + OWNER + "/" + quote(slug) + "/commits"
        language_bytes.update(api("/repos/" + OWNER + "/" + quote(slug) + "/languages"))
        try:
            rows = list(pages(route, sha=repo["default_branch"]))
        except Exception as exc:
            print(f"Skipping commits for {slug}: {exc}", file=sys.stderr)
            continue
        for row in rows:
            author = row.get("author")
            if not author or author["login"].lower() != OWNER.lower():
                continue
            time = datetime.fromisoformat(row["commit"]["author"]["date"].replace("Z", "+00:00")).astimezone(zone)
            if time > when or time.date() < start:
                continue
            sha = row["sha"]
            title = row["commit"]["message"].splitlines()[0]
            if title.strip().lower() == "refresh profile activity":
                continue
            parents = [parent["sha"] for parent in row.get("parents", ())]
            all_rows.setdefault(
                sha,
                dict(
                    sha=sha,
                    repo=slug,
                    branch=repo["default_branch"],
                    parents=parents,
                    time=time.isoformat(),
                    title=title,
                    url=row["html_url"],
                ),
            )

    commits = sorted(all_rows.values(), key=lambda row: (row["time"], row["sha"]), reverse=True)
    repositories = [{"name": r["name"], "fork": r["fork"]} for r in repos if not r["private"]]
    return {
        "end": when.isoformat(),
        "start": start.isoformat(),
        "owned": len(repos),
        "scanned": total,
        "repositories": repositories,
        "created_at": api("/users/" + OWNER)["created_at"],
        "commits": commits,
        "language_bytes": dict(language_bytes),
    }


def local_write(path, content):
    import tempfile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temp.write(content.encode("utf-8"))
    os.replace(temp.name, path)


def publish_terminal(data, root):
    readme = render_terminal(data, root / "assets", local_write)
    local_write(root / "README.md", readme)


def refresh(from_json=None):
    if from_json:
        data = json.loads(Path(from_json).read_text(encoding="utf-8"))
    else:
        data = snapshot()
    publish_terminal(data, Path(__file__).resolve().parent)
    print(f"Updated {len(data['commits'])} commits through {data['end'][:10]}.")


if __name__ == "__main__":
    src = sys.argv[2] if len(sys.argv) >= 3 and sys.argv[1] == "--from-json" else None
    refresh(from_json=src)
