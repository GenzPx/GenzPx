#!/usr/bin/env python3
"""Generate self-hosted SVG assets for the GenzPx profile README.

Outputs:
  assets/neofetch.svg    - identity card (name/alias, role, stack, counts)
  terminal_stats.svg     - terminal stats card (incl. live `$ status`)
  streak.svg             - terminal streak card

Dynamic cards pull live data from the GitHub API (plus the komarev view
counter). Everything is committed to the repo — no flaky third-party renderers.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone

USER = "GenzPx"
TOKEN = os.environ.get("GITHUB_TOKEN")

# --- theme (calm, readable greens) ----------------------------------------
BG = "#0D1117"
BORDER = "#30363D"
ACCENT = "#3FB950"        # readable green for labels / prompts / bars
WHITE = "#E6EDF3"         # primary text
MUTED = "#8B949E"         # secondary text
RED, YEL, GRN = "#FF5F56", "#FFBD2E", "#27C93F"   # traffic lights
FONT = "DejaVu Sans Mono, monospace"

WIB = timezone(timedelta(hours=7))


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
# DATA
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


def fetch_views():
    """Pull the profile view count from the komarev counter badge."""
    try:
        req = urllib.request.Request(
            f"https://komarev.com/ghpvc/?username={USER}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        svg = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace")
        m = re.search(r">([\d][\d,]*)</text>", svg)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "—"


# --- time-aware status (normal schedule, WIB) -----------------------------
SCHEDULE = [
    ("sleeping", 0, 9),
    ("coding", 9, 12),
    ("eating", 12, 13),
    ("coding", 13, 18),
    ("eating", 18, 19),
    ("coding", 19, 23),
    ("winding down", 23, 24),
]


def fmt_since(mins):
    h, m = divmod(mins, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


def compute_now():
    t = datetime.now(WIB)
    hh = t.hour + t.minute / 60.0
    for i, (name, start, end) in enumerate(SCHEDULE):
        if start <= hh < end:
            start_dt = t.replace(hour=start, minute=0, second=0, microsecond=0)
            since = int((t - start_dt).total_seconds() // 60)
            n_name, n_start, _ = SCHEDULE[(i + 1) % len(SCHEDULE)]
            return {
                "state": name,
                "since": fmt_since(since),
                "next": f"{n_name} @ {n_start:02d}:00 WIB",
            }
    return {"state": "offline", "since": "0m", "next": "sleeping @ 00:00 WIB"}


# ===========================================================================
# NEOFETCH CARD
# ===========================================================================
def gen_neofetch(d, views):
    W = 640
    pad = 26
    title_h = 42
    logo_w = 130
    logo_x = pad
    logo_y = title_h + 26
    logo_size = 104
    info_x = logo_x + logo_w + 20
    info_y0 = title_h + 40
    lh = 26
    label_w = 96

    rows = [
        ("Name", "GenzPX · ./XternalZ"),
        ("Role", "Indonesian solo builder"),
        ("Stack", "Android · Python · Web"),
        ("Followers", str(d["followers"])),
        ("Stars", str(d["stars"])),
        ("Views", views),
    ]

    prims = []
    # title
    prims.append(f'<text x="{info_x}" y="{info_y0}" fill="{ACCENT}" font-size="16" '
                 f'font-family="{FONT}" font-weight="bold">genzpx@github</text>')
    y = info_y0 + lh + 2
    for label, value in rows:
        prims.append(f'<text x="{info_x}" y="{y}" fill="{ACCENT}" font-size="14" '
                     f'font-family="{FONT}">{esc(label)}</text>')
        prims.append(f'<text x="{info_x + label_w}" y="{y}" fill="{WHITE}" font-size="14" '
                     f'font-family="{FONT}">{esc(value)}</text>')
        y += lh

    # quote
    y += 8
    prims.append(f'<text x="{info_x}" y="{y}" fill="{MUTED}" font-size="14" '
                 f'font-family="{FONT}">"Tools are meant to be understood,</text>')
    y += lh
    prims.append(f'<text x="{info_x}" y="{y}" fill="{MUTED}" font-size="14" '
                 f'font-family="{FONT}"> not just used."</text>')
    y += lh

    H = max(y + 20, title_h + 26 + logo_size + 20)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="21" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="26" fill="{MUTED}" font-size="13" '
               f'text-anchor="middle" font-family="{FONT}">~ genzpx</text>')
    svg.append(f'<line x1="0" y1="{title_h}" x2="{W}" y2="{title_h}" stroke="{BORDER}"/>')
    # logo tile
    svg.append(f'<rect x="{logo_x}" y="{logo_y}" width="{logo_size}" height="{logo_size}" '
               f'rx="22" fill="#161B22" stroke="{BORDER}"/>')
    svg.append(f'<text x="{logo_x + logo_size/2}" y="{logo_y + logo_size/2 + 16}" '
               f'fill="{ACCENT}" font-size="40" text-anchor="middle" font-family="{FONT}">&gt;_</text>')
    svg.extend(prims)
    svg.append("</svg>")
    with open("assets/neofetch.svg", "w") as f:
        f.write("\n".join(svg))


# ===========================================================================
# TERMINAL STATS CARD
# ===========================================================================
def gen_terminal_stats(d, now):
    W = 600
    pad = 20
    lh = 22
    title_h = 40
    label_w = 130
    bar_max = W - pad * 2 - label_w - 60

    y = title_h + 18
    prims = []

    def text(x, yy, t, color, size):
        return (f'<text x="{x}" y="{yy}" fill="{color}" font-size="{size}" '
                f'font-family="{FONT}">{esc(t)}</text>')

    def prompt(t):
        nonlocal y
        prims.append(text(pad, y + 4, "$ " + t, ACCENT, 14))
        y += lh

    def row(label, value):
        nonlocal y
        prims.append(text(pad, y + 4, "  " + label.ljust(10), MUTED, 14))
        prims.append(text(pad + 12 + 10 * 8.4, y + 4, value, WHITE, 14))
        y += lh

    def bar(label, pct):
        nonlocal y
        prims.append(text(pad, y + 4, "  " + label.ljust(10), MUTED, 13))
        tx = pad + label_w
        bw = int(bar_max * pct / 100.0)
        prims.append(f'<rect x="{tx}" y="{y - 9}" width="{bar_max}" height="11" rx="3" fill="#161B22"/>')
        prims.append(f'<rect x="{tx}" y="{y - 9}" width="{bw}" height="11" rx="3" fill="{ACCENT}"/>')
        prims.append(text(tx + bar_max + 10, y + 4, f"{pct}%", WHITE, 13))
        y += lh

    prompt("whoami")
    row("name", "GenzPX")
    row("alias", "./XternalZ")
    y += 4

    prompt("stats")
    row("followers", str(d["followers"]))
    row("following", str(d["following"]))
    row("repos", str(d["public_repos"]))
    row("stars", str(d["stars"]))
    row("forks", str(d["forks"]))
    y += 4

    prompt("languages")
    for name, pct in d["langs"]:
        bar(name, pct)
    y += 4

    prompt("status")
    row("state", now["state"])
    row("since", now["since"])
    row("next", now["next"])
    y += 4

    prompt("exit")
    row("", "bye.")

    H = y + 12
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="20" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="25" fill="{MUTED}" font-size="13" text-anchor="middle">~ genzpx</text>')
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

    prims.append(text(pad, y + 4, "$ streak --live", ACCENT, 14)); y += lh
    prims.append(text(pad, y + 4, f"  current streak   {s['current']} days", WHITE, 14)); y += lh
    prims.append(text(pad, y + 4, f"  longest streak   {s['longest']} days", WHITE, 14)); y += lh
    prims.append(text(pad, y + 4, f"  contributions    ~{s['commits']} (last 90d)", WHITE, 14)); y += lh + 10
    prims.append(text(pad, y + 4, "$ sparkline", ACCENT, 14)); y += lh

    bw = 8
    gap = 5
    base_y = y + 6
    max_h = 30
    x = pad
    for v in s["spark"]:
        h = max_h if v else 3
        prims.append(f'<rect x="{x}" y="{base_y - h}" width="{bw}" height="{h}" rx="2" '
                     f'fill="{ACCENT if v else "#21262D"}"/>')
        x += bw + gap
    y = base_y + 12

    H = y + 12
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="{FONT}">']
    svg.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>')
    for cx, c in ((24, RED), (44, YEL), (64, GRN)):
        svg.append(f'<circle cx="{cx}" cy="20" r="6" fill="{c}"/>')
    svg.append(f'<text x="{W/2}" y="25" fill="{MUTED}" font-size="13" text-anchor="middle">~ genzpx</text>')
    svg.append(f'<line x1="0" y1="{title_h}" x2="{W}" y2="{title_h}" stroke="{BORDER}"/>')
    svg.extend(prims)
    svg.append("</svg>")
    with open("streak.svg", "w") as f:
        f.write("\n".join(svg))


def main():
    d = fetch_stats()
    views = fetch_views()
    now = compute_now()
    gen_neofetch(d, views)
    print("neofetch ok — views:", views)
    gen_terminal_stats(d, now)
    print("terminal_stats ok — status:", json.dumps(now))
    s = compute_streak(fetch_events())
    gen_streak(s)
    print("streak ok:", json.dumps({k: v for k, v in s.items() if k != "spark"}))


if __name__ == "__main__":
    main()
