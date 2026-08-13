#!/usr/bin/env python3
"""Auto-update the "What I build" section of the profile README.

Reads .github/projects.json (category -> [{icon, repo}]) and rewrites the
tables between <!-- PROJECTS:START --> and <!-- PROJECTS:END --> in README.md.

Repo descriptions are pulled live from the GitHub API, so keeping a repo's
description up to date keeps the profile table in sync automatically.
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

TOKEN = os.environ.get("GITHUB_TOKEN")


def api(url):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def repo_desc(repo):
    try:
        data = api(f"https://api.github.com/repos/{USER}/{repo}")
        desc = (data.get("description") or "").strip()
        return desc if desc else "—"
    except Exception as e:
        print(f"warn: could not fetch {repo}: {e}", file=sys.stderr)
        return "—"


def build_tables(cfg):
    parts = []
    for category, items in cfg.items():
        parts.append(f"### {category}\n")
        parts.append("| | Project | What it actually does |")
        parts.append("| :--- | :--- | :--- |")
        for it in items:
            icon = it.get("icon", "")
            repo = it["repo"]
            desc = repo_desc(repo)
            link = f"[**{repo}**](https://github.com/{USER}/{repo})"
            img = f'<img src="assets/icons/{icon}" width="20" />'
            parts.append(f"| {img} | {link} | {desc} |")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main():
    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    with open(README, "r", encoding="utf-8") as f:
        readme = f.read()

    if START not in readme or END not in readme:
        print(f"error: markers {START}/{END} not found in {README}", file=sys.stderr)
        sys.exit(1)

    head, rest = readme.split(START, 1)
    _, tail = rest.split(END, 1)

    tables = build_tables(cfg)
    new_readme = f"{head}{START}\n\n{tables}\n{END}{tail}"

    if new_readme != readme:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README updated.")
    else:
        print("README already up to date.")


if __name__ == "__main__":
    main()
