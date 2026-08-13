#!/usr/bin/env python3
"""Generate self-hosted SVG assets for the GenzPx profile README.

Outputs:
  assets/neofetch.svg    - neofetch-style "about" card
  terminal_stats.svg     - terminal-window stats card
  streak.svg             - terminal-window streak card

Dynamic cards (stats, streak) pull live data from the GitHub API. Everything is
committed to the repo so nothing depends on flaky third-party renderers.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

USER = "GenzPx"
TOKEN = os.environ.get("GITHUB_TOKEN")

# --- theme ----------------------------------------------------------------
BG = "#0D1117"
BORDER = "#30363d"
GREEN = "#00FF41"
DIM = "#8b949e"
RED, YEL, GRN = "#ff5f56", "#ffbd2e", "#27c93f"
FONT = "DejaVu Sans Mono, monospace"


def api(url):
    headers = {"User-Agent": "GenzPx-assets", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ===========================================================================
# NEOFETCH CARD
# ===========================================================================
def gen_neofetch():
    W = 640
    pad = 26
    title_h = 42
    logo_w = 130
    logo_x = pad
    logo_y = title_h + 26
    logo_size = 110
    info_x = logo_x + logo_w + 20
    info_y0 = title_h + 46
    lh = 26

    rows = [
        ("genzpx@github", GREEN, 16),
        ("", DIM, 8),
        ("Name     ", GREEN, 14),
        ("  GenzPX", "#E6EDF3", 14),
        ("Alias    ", GREEN, 14),
        ("  ./XternalZ", "#E6EDF3", 14),
        ("Role     ", GREEN, 14),
        ("  Indonesian solo builder", "#E6EDF3", 14),
        ("Stack    ", GREEN, 14),
        ("  Android · Python · Web", "#E6EDF3", 14),
        ("Status   ", GREEN, 14),
        ("  sleep | eat | have money", "#E6EDF3", 14),
        ("", DIM, 8),
        ('"Tools are meant to be understood,', DIM, 14),
        (' not just used."', DIM, 14),
    ]

    prims = []
    y = info_y0
    for text, color, size in rows:
        if text == "":
            y += 8
            continue
        prims.append(f'<text x="{info_x}" y="{y}" fill="{color}" font-size="{size}" '
                     f'font-family="{FONT}">{esc(text)}</text>')
        y += lh

    H = max(y + 20, title_h + 26 + logo_size + 20)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="21" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="26" fill="{DIM}" font-size="13" '
               f'text-anchor="middle" font-family="{FONT}">~ genzpx</text>')
    svg.append(f'<line x1="0" y1="{title_h}" x2="{W}" y2="{title_h}" stroke="{BORDER}"/>')
    svg.append(f'<rect x="{logo_x}" y="{logo_y}" width="{logo_size}" height="{logo_size}" '
               f'rx="22" fill="#161B22" stroke="{BORDER}"/>')
    svg.append(f'<text x="{logo_x + logo_size/2}" y="{logo_y + logo_size/2 + 16}" '
               f'fill="{GREEN}" font-size="40" text-anchor="middle" font-family="{FONT}">&gt;_</text>')
    svg.extend(prims)
    svg.append("</svg>")
    with open("assets/neofetch.svg", "w") as f:
        f.write("\n".join(svg))


# ===========================================================================
# TERMINAL STATS CARD
# ===========================================================================
def fetch_stats():
    user = api(f"https://api.github.com/users/{USER}")
    repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)

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
    langs = [(n, round(100.0 * b / total, 1)) for n, b in langs]

    return {
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "public_repos": user.get("public_repos", 0),
        "stars": total_stars,
        "forks": total_forks,
        "langs": langs,
    }


def gen_terminal_stats(d):
    W = 600
    pad = 20
    lh = 22
    title_h = 40
    label_w = 130
    bar_max = W - pad * 2 - label_w - 60

    y = title_h + 18
    prims = []

    def text(x, yy, t, color, size, anchor="start", font=FONT):
        return (f'<text x="{x}" y="{yy}" fill="{color}" font-size="{size}" '
                f'font-family="{font}" text-anchor="{anchor}">{esc(t)}</text>')

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
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="20" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="25" fill="{DIM}" font-size="13" text-anchor="middle">~ genzpx</text>')
    svg.append(f'<line x1="0" y1="{title_h}" x2="{W}" y2="{title_h}" stroke="{BORDER}"/>')
    svg.extend(prims)
    svg.append("</svg>")
    with open("terminal_stats.svg", "w") as f:
        f.write("\n".join(svg))


# ===========================================================================
# STREAK CARD
# ===========================================================================
CONTRIB = {"PushEvent", "PullRequestEvent", "IssuesEvent", "IssueCommentEvent",
           "CreateEvent", "PullRequestReviewEvent", "PullRequestReviewCommentEvent",
           "CommitCommentEvent", "ReleaseEvent"}


def fetch_events():
    out = []
    for page in range(1, 4):
        try:
            ev = api(f"https://api.github.com/users/{USER}/events/public?per_page=100&page={page}")
        except Exception:
            break
        if not ev:
            break
        out.extend(ev)
        if len(ev) < 100:
            break
    return out


def compute_streak(events):
    today = datetime.now(timezone.utc).date()
    days = set()
    commits = 0
    for e in events:
        if e.get("type") not in CONTRIB:
            continue
        created = e.get("created_at", "")
        d = created[:10]
        days.add(d)
        if e["type"] == "PushEvent":
            commits += e.get("payload", {}).get("size", 0)
        else:
            commits += 1

    cur = 0
    d = today
    if str(d) not in days:
        d = today - timedelta(days=1)
    while str(d) in days:
        cur += 1
        d -= timedelta(days=1)

    sorted_days = sorted(days)
    longest = 0
    run = 0
    prev = None
    for ds in sorted_days:
        dt = datetime.strptime(ds, "%Y-%m-%d").date()
        if prev is not None and (dt - prev).days == 1:
            run += 1
        else:
            run = 1
        prev = dt
        longest = max(longest, run)

    spark = []
    for i in range(29, -1, -1):
        dd = today - timedelta(days=i)
        spark.append(1 if str(dd) in days else 0)

    return {"current": cur, "longest": longest, "commits": commits, "spark": spark}


def gen_streak(s):
    W = 600
    pad = 20
    title_h = 40
    y = title_h + 20
    lh = 26
    prims = []

    def text(x, yy, t, color, size):
        return (f'<text x="{x}" y="{yy}" fill="{color}" font-size="{size}" '
                f'font-family="{FONT}">{esc(t)}</text>')

    prims.append(text(pad, y + 4, "$ streak --live", GREEN, 14)); y += lh
    prims.append(text(pad, y + 4, f"  current streak   {s['current']} days", "#E6EDF3", 14)); y += lh
    prims.append(text(pad, y + 4, f"  longest streak   {s['longest']} days", "#E6EDF3", 14)); y += lh
    prims.append(text(pad, y + 4, f"  contributions    ~{s['commits']} (last 90d)", "#E6EDF3", 14)); y += lh + 10
    prims.append(text(pad, y + 4, "$ sparkline", GREEN, 14)); y += lh

    bw = 8
    gap = 5
    base_y = y + 6
    max_h = 30
    x = pad
    for v in s["spark"]:
        h = max_h if v else 3
        prims.append(f'<rect x="{x}" y="{base_y - h}" width="{bw}" height="{h}" rx="2" '
                     f'fill="{GREEN if v else "#21262d"}"/>')
        x += bw + gap
    y = base_y + 12

    H = y + 12
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="20" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="25" fill="{DIM}" font-size="13" text-anchor="middle">~ genzpx</text>')
    svg.append(f'<line x1="0" y1="{title_h}" x2="{W}" y2="{title_h}" stroke="{BORDER}"/>')
    svg.extend(prims)
    svg.append("</svg>")
    with open("streak.svg", "w") as f:
        f.write("\n".join(svg))


def main():
    gen_neofetch()
    print("neofetch ok")
    d = fetch_stats()
    gen_terminal_stats(d)
    print("terminal_stats ok")
    s = compute_streak(fetch_events())
    gen_streak(s)
    print("streak ok:", json.dumps({k: v for k, v in s.items() if k != "spark"}))


if __name__ == "__main__":
    main()
