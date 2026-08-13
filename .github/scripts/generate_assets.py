#!/usr/bin/env python3
"""Generate all self-hosted SVG assets for the GenzPx profile README.

Outputs:
  assets/icons/<name>.svg    - 24x24 brand-colored icons
  assets/cards/<repo>.svg    - card badges (icon + name + short description)
  assets/neofetch.svg        - neofetch-style "about" card
  terminal_stats.svg         - terminal-window stats card
  streak.svg                 - terminal-window streak card

Project metadata (name, icon, short description, category) lives in
.github/projects.json — the single source of truth shared with
update_projects.py. Dynamic cards (stats, streak) pull live GitHub data.
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
SANS = "DejaVu Sans, sans-serif"


def api(url):
    headers = {"User-Agent": "GenzPx-assets", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_projects():
    with open(".github/projects.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ===========================================================================
# ICONS (Material Design paths, Apache-2.0)
# ===========================================================================
ICONS = {
    "music": ("M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z", "#A855F7"),
    "monitoredcheck": ("M20 3H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h3l-1 1v2h12v-2l-1-1h3c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 13H4V5h16v11z", "#06B6D4"),
    "sickhack": ("M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8h16v10zm-2-1h-6v-2h6v2zM7.5 17l-1.41-1.41L8.67 13l-2.59-2.59L7.5 9l4 4-4 4z", "#22C55E"),
    "apkstore": ("M17.6 9.48l1.84-3.18c.16-.31.04-.69-.26-.85-.29-.15-.65-.06-.83.22l-1.88 3.24c-2.86-1.21-6.08-1.21-8.94 0L5.65 5.67c-.19-.29-.58-.38-.87-.2-.28.18-.37.54-.22.83L6.4 9.48C3.3 11.25 1.28 14.44 1 18h22c-.28-3.56-2.3-6.75-5.4-8.52zM7 15.25c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25zm10 0c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25z", "#6366F1"),
    "the-decoder": ("M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z", "#14B8A6"),
    "downloader-ux": ("M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z", "#3B82F6"),
    "security-toolkit": ("M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z", "#0EA5E9"),
    "information-cracker": ("M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z", "#F59E0B"),
    "casperverse": ("M15 9H9v6h6V9zm-2 4h-2v-2h2v2zm8-2V9h-2V7c0-1.1-.9-2-2-2h-2V3h-2v2h-2V3H9v2H7c-1.1 0-2 .9-2 2v2H3v2h2v2H3v2h2v2c0 1.1.9 2 2 2h2v2h2v-2h2v2h2v-2h2c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2zm-4 6H7V7h10v10z", "#EC4899"),
    "edukids": ("M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z", "#F97316"),
}


def gen_icons():
    os.makedirs("assets/icons", exist_ok=True)
    for name, (path, color) in ICONS.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
               f'width="24" height="24"><path fill="{color}" d="{path}"/></svg>')
        with open(f"assets/icons/{name}.svg", "w") as f:
            f.write(svg)


# ===========================================================================
# PROJECT CARDS (icon + name + short description)
# ===========================================================================
def card_svg(repo, icon_key, desc):
    path, color = ICONS[icon_key]
    H = 56
    icon = 28
    pad = 16
    gap = 14

    name_fs = 16
    desc_fs = 12

    name_tw = len(repo) * 8.6
    desc_tw = len(desc) * 6.6
    text_w = max(name_tw, desc_tw)

    W = pad + icon + gap + text_w + pad

    icon_x = pad
    icon_y = (H - icon) / 2
    text_x = pad + icon + gap
    name_y = 24
    desc_y = 42

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" rx="12" fill="#161B22" stroke="{BORDER}"/>'
            f'<g transform="translate({icon_x},{icon_y}) scale({icon/24})">'
            f'<path fill="{color}" d="{path}"/></g>'
            f'<text x="{text_x}" y="{name_y}" fill="#E6EDF3" font-size="{name_fs}" '
            f'font-family="{SANS}" font-weight="600">{esc(repo)}</text>'
            f'<text x="{text_x}" y="{desc_y}" fill="{DIM}" font-size="{desc_fs}" '
            f'font-family="{SANS}">{esc(desc)}</text>'
            f'</svg>')


def gen_cards():
    os.makedirs("assets/cards", exist_ok=True)
    projects = load_projects()
    seen = set()
    for items in projects.values():
        for it in items:
            repo = it["repo"]
            icon_key = it["icon"]
            desc = it.get("desc", "")
            svg = card_svg(repo, icon_key, desc)
            with open(f"assets/cards/{repo}.svg", "w") as f:
                f.write(svg)
            seen.add(repo)


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
    gen_icons()
    print("icons ok")
    gen_cards()
    print("cards ok")
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
