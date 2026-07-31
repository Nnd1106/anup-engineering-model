# Anup Engineering Model — Daily CMP Automation

Every weekday afternoon (after NSE/BSE close), this pulls the latest closing
price for Anup Engineering and its five peers, writes them into the model,
and pushes the refreshed file straight back into this GitHub repo. No
external accounts, no credentials, no credit card — GitHub's own built-in
token does the commit.

## What updates automatically
| Cell | What it holds |
|---|---|
| `DCF Model!C59` | Anup Engineering CMP (drives % upside/downside) |
| `Peer Data!D14` | Anup Engineering CMP (mirror, feeds peer comps) |
| `Peer Data!D9` | ISGEC Heavy Engineering CMP |
| `Peer Data!D10` | Praj Industries CMP |
| `Peer Data!D11` | GMM Pfaudler CMP |
| `Peer Data!D12` | Thermax CMP |
| `Peer Data!D13` | Patels Airtemp India CMP |

Everything else in the model (DCF cash flows, WACC, the sensitivity table) is
untouched — those don't depend on today's market price.

## One-time setup (~5 minutes)

**1. Create a private GitHub repo** (Settings must allow Actions to run,
   which is on by default) and push this whole folder to it, exactly as-is.

**2. That's it.** No secrets, no app registrations, no third-party sign-in.
   `permissions: contents: write` in the workflow file is enough for GitHub
   Actions to commit the daily update back into your own repo using its
   built-in token.

**3. Test it manually** before trusting the schedule: go to the repo's
   **Actions** tab → "Daily Anup Engineering Model Update" → **Run workflow**.
   Check the logs, then confirm the commit shows up with today's date and the
   file's CMP cells changed.

## How to view the latest version each day

Since there's no OneDrive/Drive sync here, "viewing the latest file" takes
one click instead of zero. Two ways to do it, pick whichever's more
convenient:

- **Bookmark the raw file URL:**
  `https://github.com/<your-username>/<your-repo>/raw/main/Niranjan_Desai_Anup_Engineering_Model.xlsx`
  As long as you're logged into GitHub in your browser, clicking this always
  downloads whatever is currently on the `main` branch — i.e. today's
  version — and you open it in Excel from your downloads folder.
- **Or just open the repo on GitHub.com** and click the file — GitHub shows
  a basic in-browser preview, though a workbook this complex (charts, 250+
  row sheets, a Data Table) may not render perfectly there; downloading and
  opening in real Excel is the reliable option.

If you later change your mind about wanting it to land somewhere with true
zero-click viewing (Google Drive, OneDrive), the door's still open — just
say the word and we can revisit that layer without touching
`update_prices.py` at all.

## Notes
- Patels Airtemp India trades thin on NSE; Yahoo Finance only reliably feeds
  its BSE listing (`PATELSAI.BO`), so that one's price may lag NSE's by more
  than the others on low-volume days.
- If a ticker fetch fails on a given day (e.g. a Yahoo Finance hiccup), that
  one's price is simply left at its last known value and the rest still
  update — check the Action's logs if you want to know which one, if any.
- The "as of [date]" labels next to the CMP inputs update automatically too,
  but only on runs where at least one price actually refreshed — so a
  fully-failed run never leaves a misleading date next to stale prices.
