#!/usr/bin/env python3
"""Auto-update the "What I build" section of the profile README.

Fetches the user's public repos, sorts them by most recently pushed, takes the
top 10, and renders a single markdown table between <!-- PROJECTS:START --> and
<!-- PROJECTS:END -->. Descriptions come from .github/projects.json short_desc
map, falling back to the repo description (first 3 words).

New repos appear automatically as they're pushed to — no manual edits needed.
"""
import json
import os
import sys
import urllib.request

USER = "GenzPx"
CONFIG = ".github/projects.json"
README = "README.md"
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
EXCLUDE = {"GenzPx"}  # the profile repo itself
MAX = 10

TOKEN = os.environ.get("GITHUB_TOKEN")


def api(url):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def load_short_desc():
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f).get("short_desc", {})
    except Exception:
        return {}


def fetch_repos():
    repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
    out = []
    for r in repos:
        if r.get("fork"):
            continue
        if r["name"] in EXCLUDE:
            continue
        if r.get("archived"):
            continue
        out.append(r)
    # sort newest first (pushed_at desc)
    out.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    return out[:MAX]


def desc_for(repo, short_desc):
    name = repo["name"]
    if name in short_desc:
        return short_desc[name]
    full = (repo.get("description") or "").strip()
    if full:
        words = full.split()
        return " ".join(words[:3]).lower()
    return "—"


def build_table(repos, short_desc):
    lines = ["| Project | Description |", "| :--- | :--- |"]
    for r in repos:
        name = r["name"]
        link = f"[**{name}**](https://github.com/{USER}/{name})"
        lines.append(f"| {link} | {desc_for(r, short_desc)} |")
    return "\n".join(lines)


def main():
    short_desc = load_short_desc()
    repos = fetch_repos()
    table = build_table(repos, short_desc)

    with open(README, "r", encoding="utf-8") as f:
        readme = f.read()

    if START not in readme or END not in readme:
        print(f"error: markers {START}/{END} not found in {README}", file=sys.stderr)
        sys.exit(1)

    head, rest = readme.split(START, 1)
    _, tail = rest.split(END, 1)
    new_readme = f"{head}{START}\n\n{table}\n\n{END}{tail}"

    if new_readme != readme:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README updated.")
    else:
        print("README already up to date.")


if __name__ == "__main__":
    main()
