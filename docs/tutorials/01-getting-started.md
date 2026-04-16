# Getting Started with NHL Scrabble

Welcome to NHL Scrabble! In this tutorial, you'll learn how to install and run your first NHL roster Scrabble score analysis.

## What you'll learn

By the end of this tutorial, you'll be able to:

- ✅ Install NHL Scrabble on your system
- ✅ Run your first analysis
- ✅ Understand Scrabble scoring for player names
- ✅ View conference and division standings
- ✅ Customize basic output settings

**Time required**: ~15 minutes

## Prerequisites

Before starting, make sure you have:

- Python 3.10 or higher installed
- Basic command-line knowledge
- Internet connection (to fetch NHL roster data)

## Step 1: Clone the repository

First, clone the NHL Scrabble repository to your local machine:

```bash
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble
```

You should now be in the `nhl-scrabble` directory.

## Step 2: Set up the development environment

NHL Scrabble uses a virtual environment to manage dependencies. Create and activate it:

```bash
make init
source .venv/bin/activate
```

**What's happening?**

- `make init` creates a Python virtual environment and installs all dependencies
- `source .venv/bin/activate` activates the environment (your prompt will change to show `(.venv)`)

**Troubleshooting**:

- If `make` is not found, install it with your package manager (`sudo apt install make` on Ubuntu/Debian)
- If Python 3.10+ is not found, install it from [python.org](https://www.python.org/downloads/)

## Step 3: Run your first analysis

Now run the NHL Scrabble analyzer:

```bash
nhl-scrabble analyze
```

**What you'll see**:

The analyzer will:

1. Fetch current NHL standings from the official API
2. Download roster data for all teams
3. Calculate Scrabble scores for every player's name
4. Generate comprehensive reports

The output starts with a progress indicator:

```
🏒 NHL Roster Scrabble Score Analyzer 🏒
================================================================================
✓ Successfully fetched 32 of 32 teams
```

## Step 4: Understanding the output

The analysis generates several reports. Let's look at each section:

### Conference Standings

```
================================================================================
CONFERENCE STANDINGS
================================================================================

Eastern Conference: 32,145 points (avg: 2,010/team)
  1. Team ABC - 2,234 points
  2. Team XYZ - 2,156 points
  ...
```

**What this means**:

- Each conference's total score is the sum of all team scores
- Teams are ranked by their total Scrabble score
- Higher scores come from players with high-value letters (Q, Z, X, J, K)

### Division Standings

```
Atlantic Division
  1. Toronto Maple Leafs - 2,234 points
  2. Tampa Bay Lightning - 2,156 points
  ...
```

**What this means**:

- Teams grouped by their NHL division
- Scores based purely on player name letter values
- Not related to actual hockey performance!

### Mock Playoff Bracket

```
Eastern Conference Playoffs:
  y - Toronto Maple Leafs (Atlantic #1)
  x - Boston Bruins (Wild Card)
  ...
```

**What this means**:

- `y` = Division leader (guaranteed playoff spot)
- `x` = Wild card team
- `z` = Conference leader
- `p` = Presidents' Trophy (best overall)
- `e` = Eliminated from playoffs

### Top Players

```
Top 20 Players by Scrabble Score:
  1. Alexander Ovechkin (WSH) - 52 points
  2. Zdeno Chara (BOS) - 48 points
  ...
```

**Understanding Scrabble values**:

- A, E, I, O, U, L, N, S, T, R = 1 point
- D, G = 2 points
- B, C, M, P = 3 points
- F, H, V, W, Y = 4 points
- K = 5 points
- J, X = 8 points
- Q, Z = 10 points

For example, "OVECHKIN":

- O(1) + V(4) + E(1) + C(3) + H(4) + K(5) + I(1) + N(1) = **20 points**

## Step 5: Save output to a file

Instead of printing to the terminal, save the report to a file:

```bash
nhl-scrabble analyze --output report.txt
```

Now you can open `report.txt` in any text editor to view the results.

## Step 6: Try JSON output

For programmatic use, export data as JSON:

```bash
nhl-scrabble analyze --format json --output report.json
```

The JSON file contains all the data in a structured format:

```json
{
  "teams": {
    "TOR": {
      "total": 2234,
      "players": [...],
      "division": "Atlantic",
      "conference": "Eastern"
    },
    ...
  },
  "divisions": {...},
  "conferences": {...},
  "playoffs": {...}
}
```

## Step 7: Customize the output

Show more top players:

```bash
nhl-scrabble analyze --top-players 50
```

Show more players per team:

```bash
nhl-scrabble analyze --top-team-players 10
```

Enable verbose logging to see API requests:

```bash
nhl-scrabble analyze --verbose
```

## What you've learned

Congratulations! You've successfully:

- ✅ Installed NHL Scrabble
- ✅ Run your first analysis
- ✅ Understood Scrabble scoring for player names
- ✅ Viewed conference and division standings
- ✅ Customized output settings
- ✅ Exported data to files and JSON

## Next steps

Now that you know the basics, you can:

1. **Dive deeper into output**: [Understanding Output Tutorial](02-understanding-output.md)
2. **Solve specific problems**: [How-to Guides](../how-to/)
3. **Look up commands**: [CLI Reference](../reference/cli.md)
4. **Understand the system**: [Architecture Explanation](../explanation/architecture.md)

## Troubleshooting

### Issue: "command not found: nhl-scrabble"

**Solution**: Make sure you activated the virtual environment:

```bash
source .venv/bin/activate
```

### Issue: "NHL API Error: Connection timeout"

**Solution**: Check your internet connection. The analyzer needs to fetch data from the NHL API at `api-web.nhle.com`.

### Issue: "Permission denied" when saving output

**Solution**: Make sure the output directory exists and is writable:

```bash
mkdir -p output
nhl-scrabble analyze --output output/report.txt
```

## Getting help

- **Questions?** See our [Support Guide](../../SUPPORT.md)
- **Found a bug?** [Open an issue](https://github.com/bdperkin/nhl-scrabble/issues)
- **Want to contribute?** Try the [First Contribution Tutorial](03-first-contribution.md)
