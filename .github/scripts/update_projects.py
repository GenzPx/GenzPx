#!/usr/bin/env python3
"""Auto-update the "What I build" section of the profile README.

Reads .github/projects.json (category -> [{repo, icon, desc}]) and rewrites the
section between <!-- PROJECTS:START --> and <!-- PROJECTS:END --> in README.md.

Each project renders as a clickable card badge (assets/cards/<repo>.svg),
grouped under a category heading.
"""
import json
import os
import sys

USER = "GenzPx"
CONFIG = ".github/projects.json"
README = "README.md"
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"


def build_section(cfg):
    parts = []
    for category, items in cfg.items():
        parts.append(f"### {category}\n")
        parts.append('<p align="left">')
        for it in items:
            repo = it["repo"]
            link = f'<a href="https://github.com/{USER}/{repo}">'
            link += f'<img src="assets/cards/{repo}.svg" alt="{repo}" /></a>'
            parts.append(link)
        parts.append("</p>\n")
    return "\n".join(parts)


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

    section = build_section(cfg)
    new_readme = f"{head}{START}\n\n{section}\n{END}{tail}"

    if new_readme != readme:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README updated.")
    else:
        print("README already up to date.")


if __name__ == "__main__":
    main()
