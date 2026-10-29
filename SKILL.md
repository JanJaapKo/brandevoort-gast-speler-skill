---
name: brandevoort-guest-players
description: Overview of which SV Brandevoort youth teams (O19, O17, O16, O15) play on a match day, home or away, at what time and where, to find guest players ("invallers", "spelers lenen") for JO17-3 when there aren't enough available players. Use when the user asks which teams can supply players, who plays this weekend/Saturday, or for the program of eligible teams at svbrandevoort.nl.
---

# SV Brandevoort guest-player overview

The user coaches **JO17-3 (O17-3) of SV Brandevoort**. When too few players are available, players from teams **O19, O17, O16 and O15** may play as guests. This skill shows, for a match day, which of those teams play, whether at home or away, their kick-off time and venue, and whether that clashes with JO17-3's match.

## How to run

Run `scripts/overview.py` from this skill's folder (the folder containing this `SKILL.md`) with Python 3.9+ (`python` on Windows, `python3` on macOS/Linux):

```
python <skill-folder>/scripts/overview.py [--date YYYY-MM-DD] [--weeks N] [--gap MINUTES] [--team O17-3] [--groups 19,17,16,15]
```

- No `--date`: the next Saturday (today if it's Saturday).
- `--weeks N`: show N consecutive Saturdays.
- Turn relative dates such as "next week" or "14 Nov" into `--date YYYY-MM-DD`.
- Python standard library only. The script finds team pages in the site menu, so new teams each season are picked up automatically.

## Output

Markdown per match day: first JO17-3's own match (or "no match scheduled"), then **three tables**:
1. **No match (free)**: eligible teams without a match that day, the best candidates.
2. **Match, but fits the timeframe**: kick-offs are at least 2.5 h apart (`--gap` minutes, default 150), so playing both is possible. If JO17-3 has no match, every playing team goes here, marked "O17-3 has no match".
3. **Match, does not fit the timeframe**: kick-offs are less than 2.5 h apart.

Always show all three tables to the user (an empty table shows "None"). The "no match" list comes only from the team-page programme on the website; don't look for other matches elsewhere. Then briefly list the most likely sources of players (table 1 first, then table 2; prefer home matches at Sportpark Brandevoort).

## Notes

- Source: the "Programma" table on each team page at https://www.svbrandevoort.nl (Sportlink data). It only lists the next few weeks.
- The site blocks requests without a browser User-Agent; the script sends one. If a page fails, the team is listed under "Could not read" below the tables.
- If JO17-3 has no match that day, say so; the teams are still listed.
