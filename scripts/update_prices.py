"""
Daily CMP updater for the Anup Engineering financial model.

Pulls the latest closing price for Anup Engineering and its five peers from
Yahoo Finance, and writes them into the exact input cells the model already
uses (these were already hardcoded numbers in the workbook, so we are only
ever overwriting a number with a newer number -- no formulas are touched).

Excel recalculates every downstream formula (DCF upside/downside, relative
valuation, peer comps table) automatically the next time the file is opened,
so this script does not need to run any recalculation itself.
"""
import datetime
import sys

import openpyxl
import yfinance as yf

FILE_PATH = "Niranjan_Desai_Anup_Engineering_Model.xlsx"

# ticker -> list of (sheet name, cell) to write the price into
TICKER_CELLS = {
    "ANUP.NS": [("DCF Model", "C59"), ("Peer Data", "D14")],
    "ISGEC.NS": [("Peer Data", "D9")],
    "PRAJIND.NS": [("Peer Data", "D10")],
    "GMMPFAUDLR.NS": [("Peer Data", "D11")],
    "THERMAX.NS": [("Peer Data", "D12")],
    "PATELSAI.BO": [("Peer Data", "D13")],  # Patels Airtemp trades thin on NSE;
                                             # Yahoo only carries a reliable feed on BSE.
}

# "as of <date>" labels that sit next to the CMP inputs, kept in sync
DATE_LABEL_CELLS = [
    ("DCF Model", "B59", "CMP a/o {date}"),
    ("Peer Data", "D8", "a/o {date}"),
    ("Peer Data", "E8", "a/o {date}"),
]


def fetch_price(ticker: str) -> float:
    """Latest available close for `ticker`. Falls back through a couple of
    yfinance APIs since field names have shifted across versions."""
    t = yf.Ticker(ticker)

    try:
        price = t.fast_info["last_price"]
        if price:
            return round(float(price), 2)
    except Exception:
        pass

    hist = t.history(period="5d")
    if hist.empty:
        raise RuntimeError(f"No price history returned for {ticker}")
    return round(float(hist["Close"].dropna().iloc[-1]), 2)


def main() -> int:
    wb = openpyxl.load_workbook(FILE_PATH)
    today_str = datetime.date.today().strftime("%-d %B, %Y")

    failures = []
    updated = {}

    for ticker, targets in TICKER_CELLS.items():
        try:
            price = fetch_price(ticker)
        except Exception as exc:
            failures.append((ticker, str(exc)))
            print(f"FAILED  {ticker}: {exc}", file=sys.stderr)
            continue

        for sheet, cell in targets:
            wb[sheet][cell] = price
        updated[ticker] = price
        print(f"OK      {ticker}: {price}")

    # Only touch the "as of" date labels if at least one price actually updated,
    # so a fully-failed run doesn't leave a stale/misleading date on old prices.
    if updated:
        for sheet, cell, template in DATE_LABEL_CELLS:
            wb[sheet][cell] = template.format(date=today_str)

    wb.save(FILE_PATH)

    if failures:
        print(f"\n{len(failures)} of {len(TICKER_CELLS)} tickers failed:", file=sys.stderr)
        for ticker, err in failures:
            print(f"  - {ticker}: {err}", file=sys.stderr)

    if not updated:
        print("No prices updated at all -- failing the run.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
