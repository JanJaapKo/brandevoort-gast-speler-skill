# brandevoort-guest-players

An agent skill for GitHub Copilot (and other tools that support `SKILL.md` skills) that helps the coach of **SV Brandevoort JO17-3** find guest players ("invallers").

When JO17-3 doesn't have enough players, players from the **O19, O17, O16 and O15** teams may join. This skill reads the match programme of those teams from [svbrandevoort.nl](https://www.svbrandevoort.nl) and shows, for a match day, three tables:

1. **No match**: eligible teams that don't play that day.
2. **Match, but fits the timeframe**: kick-off at least 2.5 h before or after JO17-3's kick-off.
3. **Match, does not fit the timeframe**: kick-off less than 2.5 h from JO17-3's kick-off.

Each match row shows home/away, kick-off time, opponent and venue.

## Example

Ask Copilot:

> Which teams can supply players this Saturday?

or

> Show the guest-player overview for 14 November.

Output (shortened):

```markdown
## Match day Sat 07 Nov 2026

**Own team O17-3:** Mierlo Hout O17-2 - SV Brandevoort O17-3 — 11:45, away @ Sportpark De Beemd

### 1. No match (free)
| Team |
|---|
| O19-4 |
| O15-3 |

### 2. Match, but fits the timeframe (kick-offs ≥ 2h30 apart)
| Team | Home/Away | Kick-off | Opponent | Venue | vs our kick-off |
|---|---|---|---|---|---|
| O19-2 | Away | 15:00 | Deurne O19-1 | Sportpark De Kranenmortel-SV Deurne | plays 3h15 after us |
...
```

## Requirements

- Python 3.9 or later (standard library only, no packages to install)
- Internet access to `www.svbrandevoort.nl`
- An agent that supports skills, such as GitHub Copilot CLI or the GitHub Copilot app

## Installation

Clone or copy this repository into your personal skills folder, using `brandevoort-guest-players` as the folder name.

**Windows (PowerShell)**

```powershell
git clone https://github.com/janjaapko/brandevoort-guest-players.git "$env:USERPROFILE\.copilot\skills\brandevoort-guest-players"
```

**macOS / Linux**

```bash
git clone https://github.com/janjaapko/brandevoort-guest-players.git ~/.copilot/skills/brandevoort-guest-players
```

To make the skill available only in a specific repository, place it in that repository at `.github/skills/brandevoort-guest-players/` instead.

Restart your Copilot session (or the app) so the skill is picked up. To update later, run `git pull` in the skill folder.

### Check the installation

Run the script directly:

```bash
python scripts/overview.py            # Windows
python3 scripts/overview.py           # macOS / Linux
```

You should see the overview for next Saturday.

## Script options

| Option | Default | Description |
|---|---|---|
| `--date YYYY-MM-DD` | next Saturday | Match day to show |
| `--weeks N` | `1` | Number of consecutive Saturdays to show |
| `--gap MINUTES` | `150` | Minimum time between kick-offs for a team to fit |
| `--team O17-3` | `O17-3` | Your own team (`JO17-3` is also accepted) |
| `--groups 19,17,16,15` | `19,17,16,15` | Eligible age groups |

With `--team` and `--groups`, other SV Brandevoort teams can use the skill as well.

## How it works

- Team pages are found in the menu of svbrandevoort.nl, so new teams each season are picked up automatically.
- Matches come from the **Programma** table on each team page (Sportlink data). That table only covers the next few weeks, and only those matches are taken into account.
- Matches on the website have no year; the script picks the date closest to today.
- The website blocks requests without a browser User-Agent, so the script sends one.

## Files

```
brandevoort-guest-players/
├── SKILL.md            # skill instructions for the agent
├── README.md
├── .gitignore
└── scripts/
    └── overview.py     # scraper and report generator
```

## Disclaimer

This is an unofficial tool and is not affiliated with SV Brandevoort. It depends on the current layout of the club website and may break when the site changes.
