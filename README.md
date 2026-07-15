# Lotto Pattern Lab

GitHub Pages site:

`https://codekimmy.github.io/lotto-pattern-lab/`

Google Sheets source:

`https://docs.google.com/spreadsheets/d/1w1AZshic7KGnbb0lqjfg_aUx5F9RzGBtJykFJuaP-lM/edit?gid=0#gid=0`

## Data pipeline

```text
Google Sheets
  → GitHub Actions
  → validation and normalized CSV
  → data/lotto_history.csv + data/meta.json
  → GitHub commit
  → GitHub Pages deployment
```

## Repository structure

```text
.
├─ index.html
├─ .nojekyll
├─ data/
│  ├─ lotto_history.csv
│  └─ meta.json
├─ scripts/
│  └─ sync_sheet.py
└─ .github/
   └─ workflows/
      └─ sync-and-deploy.yml
```

## Automatic schedule

The workflow runs in `Asia/Seoul` every Sunday at:

- 08:17
- 14:17

It can also be run manually from:

`Actions → Sync Lotto Data and Deploy Pages → Run workflow`

## Validation

The workflow rejects the update instead of overwriting the working data when:

- the header is not `draw,date,n1,n2,n3,n4,n5,n6,bonus`
- a draw is duplicated or missing
- a main number is duplicated or outside 1–45
- a bonus number is outside 1–45 or duplicates a main number
- the date format is invalid
- the downloaded latest draw goes backward

## Important GitHub Pages setting

Open:

`Settings → Pages → Build and deployment → Source`

Select:

`GitHub Actions`

Do not keep `Deploy from a branch`, because data commits made with `GITHUB_TOKEN`
do not trigger a separate Pages branch build.
