"""Overview of SV Brandevoort teams eligible to lend players to a given team.

Scrapes the team pages on svbrandevoort.nl and reports, for a match day, whether
each eligible team plays, home/away, kick-off time and venue.

Usage:
    python overview.py [--date YYYY-MM-DD] [--weeks N] [--gap MINUTES]
                       [--team O17-3] [--groups 19,17,16,15]
"""
import argparse
import datetime as dt
import html
import re
import sys
import urllib.request

BASE = "https://www.svbrandevoort.nl"
CLUB = "SV Brandevoort"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130 Safari/537.36"}
MONTHS = {"jan": 1, "feb": 2, "mrt": 3, "mar": 3, "apr": 4, "mei": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
CLASH_WINDOW = dt.timedelta(hours=2, minutes=30)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def discover_teams(groups):
    """Return {team: url} for teams like O17-3 found in the site menu."""
    page = fetch(BASE)
    teams = {}
    pat = r"<a[^>]*href='([^']+)'[^>]*>\s*<div[^>]*>\s*(O(\d{2})-\d+)\s*</div>"
    for url, name, age in re.findall(pat, page):
        if age in groups and name not in teams:
            teams[name] = url
    return teams


def parse_date(text, today):
    m = re.match(r"(\d{1,2})\s+([a-z]{3})\.?\s+(\d{1,2}):(\d{2})", text.strip().lower())
    if not m:
        return None
    day, mon, hh, mm = int(m[1]), MONTHS.get(m[2]), int(m[3]), int(m[4])
    if not mon:
        return None
    # No year on the site: choose the year closest to today.
    cands = [dt.datetime(today.year + d, mon, day, hh, mm) for d in (-1, 0, 1)]
    return min(cands, key=lambda c: abs((c.date() - today).days))


def team_matches(team, url, today):
    page = fetch(url)
    m = re.search(r">Programma</h4>(.*?)</table>", page, re.S)
    if not m:
        return []
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 5:
            continue
        when = parse_date(strip(cells[0]), today)
        game = strip(cells[2])
        venue = strip(cells[4])
        me = f"{CLUB} {team}"
        if not when or me not in game:
            continue
        home, _, away = game.partition(" - ")
        is_home = home.strip() == me
        out.append({"team": team, "when": when, "home": is_home,
                    "opponent": (away if is_home else home).strip(),
                    "venue": venue, "match": game})
    return out


def next_saturday(today):
    return today + dt.timedelta(days=(5 - today.weekday()) % 7)


def team_sort_key(name):
    age, num = re.match(r"O(\d+)-(\d+)", name).groups()
    return (-int(age), int(num))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="Match day YYYY-MM-DD (default: next Saturday)")
    ap.add_argument("--team", default="O17-3", help="Own team (default O17-3)")
    ap.add_argument("--groups", default="19,17,16,15", help="Eligible age groups")
    ap.add_argument("--weeks", type=int, default=1, help="Number of consecutive weeks")
    ap.add_argument("--gap", type=int, default=int(CLASH_WINDOW.total_seconds() // 60),
                    help="Minimum minutes between kick-offs for a team to fit (default 150)")
    args = ap.parse_args()
    gap_window = dt.timedelta(minutes=args.gap)

    today = dt.date.today()
    start = dt.date.fromisoformat(args.date) if args.date else next_saturday(today)
    groups = {g.strip() for g in args.groups.split(",")}
    own = args.team.upper().replace("JO", "O")

    teams = discover_teams(groups | {own[1:3]})
    if own not in teams:
        sys.exit(f"Team {own} not found on {BASE}")

    matches = {}
    for name, url in teams.items():
        try:
            matches[name] = team_matches(name, url, today)
        except Exception as e:  # keep going if one page fails
            print(f"Warning: could not read {name}: {e}", file=sys.stderr)
            matches[name] = None

    for w in range(args.weeks):
        day = start + dt.timedelta(weeks=w)
        print(f"\n## Match day {day:%a %d %b %Y}\n")
        own_games = [g for g in matches[own] or [] if g["when"].date() == day]
        if own_games:
            for g in own_games:
                print(f"**Own team {own}:** {g['match']} — {g['when']:%H:%M}, "
                      f"{'home' if g['home'] else 'away'} @ {g['venue']}\n")
        else:
            print(f"**Own team {own}:** no match scheduled\n")

        free, fits, clashes, errors = [], [], [], []
        for name in sorted(teams, key=team_sort_key):
            if name == own:
                continue
            if matches[name] is None:
                errors.append(name)
                continue
            games = [g for g in matches[name] if g["when"].date() == day]
            if not games:
                free.append(name)
                continue
            for g in games:
                if not own_games:
                    fits.append((g, f"{own} has no match"))
                    continue
                diff = g["when"] - own_games[0]["when"]
                gap = f"{abs(diff).seconds // 3600}h{abs(diff).seconds % 3600 // 60:02d}"
                if abs(diff) < gap_window:
                    clashes.append((g, f"{gap} {'before' if diff < dt.timedelta(0) else 'after'} us"))
                else:
                    fits.append((g, f"plays {gap} {'before' if diff < dt.timedelta(0) else 'after'} us"))

        def match_table(rows):
            if not rows:
                print("_None._\n")
                return
            print("| Team | Home/Away | Kick-off | Opponent | Venue | vs our kick-off |")
            print("|---|---|---|---|---|---|")
            for g, note in rows:
                print(f"| {g['team']} | {'Home' if g['home'] else 'Away'} | {g['when']:%H:%M} | "
                      f"{g['opponent']} | {g['venue']} | {note} |")
            print()

        mins = int(gap_window.total_seconds() // 60)
        print("### 1. No match (free)\n")
        if free:
            print("| Team |\n|---|")
            for name in free:
                print(f"| {name} |")
            print()
        else:
            print("_None._\n")
        print(f"### 2. Match, but fits the timeframe (kick-offs ≥ {mins // 60}h{mins % 60:02d} apart)\n")
        match_table(fits)
        print(f"### 3. Match, does not fit the timeframe (kick-offs < {mins // 60}h{mins % 60:02d} apart)\n")
        match_table(clashes)
        if errors:
            print(f"_Could not read: {', '.join(errors)}._\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
