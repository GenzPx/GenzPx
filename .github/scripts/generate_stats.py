#!/usr/bin/env python3
"""Generate a terminal-style stats SVG for the GitHub profile README.

Fetches live data from the GitHub API (no third-party service, no external
rendering dependency) and writes a self-contained SVG to `terminal_stats.svg`.
Run by the "Generate terminal stats" workflow on a schedule.
"""
import json
import os
import urllib.request

USER = "GenzPx"
OUT = "terminal_stats.svg"
TOKEN = os.environ.get("GITHUB_TOKEN")

# --- theme ----------------------------------------------------------------
BG = "#0D1117"
BORDER = "#30363d"
GREEN = "#00FF41"
DIM = "#8b949e"
RED, YEL, GRN = "#ff5f56", "#ffbd2e", "#27c93f"
FONT = "DejaVu Sans Mono, monospace"


def api(url):
    headers = {"User-Agent": "GenzPx-stats", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def fetch():
    user = api(f"https://api.github.com/users/{USER}")
    repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)

    # Accurate per-language byte counts via each repo's languages_url
    # (excludes binary blobs like the .brain artifacts in CasperVerse).
    lang_bytes = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            langs = api(r["languages_url"])
        except Exception:
            continue
        for lang, n in langs.items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n

    total = sum(lang_bytes.values()) or 1
    langs = sorted(lang_bytes.items(), key=lambda kv: -kv[1])[:5]
    langs = [(name, round(100.0 * n / total, 1)) for name, n in langs]

    return {
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "public_repos": user.get("public_repos", 0),
        "stars": total_stars,
        "forks": total_forks,
        "created": (user.get("created_at") or "")[:10],
        "langs": langs,
    }


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(d):
    W = 600
    pad = 20
    lh = 22
    title_h = 40
    label_w = 130
    bar_max = W - pad * 2 - label_w - 60

    y = title_h + 18
    prims = []

    def text(x, yy, t, color, size, anchor="start"):
        return (f'<text x="{x}" y="{yy}" fill="{color}" font-size="{size}" '
                f'text-anchor="{anchor}">{esc(t)}</text>')

    def add(t, color=GREEN, size=14, x=pad):
        nonlocal y
        prims.append(text(x, y + 4, t, color, size))
        y += lh

    def bar(label, pct):
        nonlocal y
        prims.append(text(pad, y + 4, label, DIM, 13))
        tx = pad + label_w
        bw = int(bar_max * pct / 100.0)
        prims.append(f'<rect x="{tx}" y="{y - 9}" width="{bar_max}" height="11" rx="3" fill="#161b22"/>')
        prims.append(f'<rect x="{tx}" y="{y - 9}" width="{bw}" height="11" rx="3" fill="{GREEN}"/>')
        prims.append(text(tx + bar_max + 10, y + 4, f"{pct}%", GREEN, 13))
        y += lh

    add("$ whoami")
    add("  GenzPX  (./XternalZ)", DIM)
    add("  Indonesian solo builder", DIM)
    y += 4

    add("$ stats")
    add(f"  followers     {d['followers']}")
    add(f"  following     {d['following']}")
    add(f"  public repos  {d['public_repos']}")
    add(f"  total stars   {d['stars']}")
    add(f"  total forks   {d['forks']}")
    y += 4

    add("$ languages")
    for name, pct in d["langs"]:
        bar(name, pct)
    y += 4

    add("$ exit")
    add("  bye.", DIM)

    H = y + 12

    svg = [f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="20" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="25" fill="{DIM}" font-size="13" '
               f'text-anchor="middle">~ genzpx</text>')
    svg.append(f'<line x1="0" y1="{title_h}" x2="{W}" y2="{title_h}" stroke="{BORDER}"/>')
    svg.extend(prims)
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    d = fetch()
    svg = render(d)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes)")
    print(json.dumps(d, indent=2))


if __name__ == "__main__":
    main()
