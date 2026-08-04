# AMFI Mutual Fund NAV & Portfolio Estimator

This project fetches mutual fund NAV data from AMFI, resolves AMFI scheme codes to Yahoo Finance tickers, extracts portfolio holdings, and estimates a fund-level expected change from the portfolio’s stock price movements.

It is designed for research and workflow automation around mutual fund data, with the main entry point returning a structured nested payload that can be reused by other modules.

Data source: https://www.amfiindia.com/spages/NAVAll.txt

---

## What the project does

- Fetches the latest NAV data from AMFI
- Parses the NAV dataset and filters by selected fund IDs
- Resolves AMFI scheme codes to Yahoo tickers using the local mapping file
- Queries Yahoo Finance for mutual fund portfolio holdings
- Estimates expected fund-level change from portfolio weights and stock price moves
- Prints a compact summary for terminal use
- Processes multiple funds concurrently for faster execution

---

## Current features

- Fetch NAV data directly from AMFI
- Parse AMFI NAV records and filter by scheme code
- Resolve AMFI codes to Yahoo tickers through ticker_map.json
- Extract portfolio holding data with yahooquery
- Estimate expected daily change using yfinance market metrics
- Return structured results for downstream automation
- Run fund processing in parallel with ThreadPoolExecutor

---

## Project structure

```text
project/
├── main.py
├── amfi_nav_fetcher.py
├── fetch_holdings.py
├── portfolio_valuator.py
├── fund_change_estimator.py
├── stock_finance_fetcher.py
├── ticker_map.json
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd Mutual-fund-iNAV-estimation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Required packages include:

- requests
- pandas
- yahooquery
- yfinance

---

## Usage

Run the main workflow:

```bash
python main.py
```

The script will:

1. Fetch NAV data from AMFI
2. Filter the configured fund IDs
3. Resolve Yahoo tickers
4. Extract portfolio data
5. Estimate expected fund change from holdings
6. Print a summary and return a nested payload

The default fund list is defined in main.py and currently includes a small sample set of AMFI scheme codes.

---

## Example output

The terminal output includes:

- AMFI NAV table details
- per-fund ticker information
- portfolio row counts
- expected-change summary for each fund
- debug messages for each processing step

The script returns a nested payload in the following shape:

```python
{
    "fund_ids": [...],
    "nav_results": [...],
    "fund_details": [
        {
            "fund_id": "118955",
            "fund_name": "HDFC Flexi Cap Fund",
            "nav_date": "17-Jul-2026",
            "nav_value": "2248.741",
            "ticker": {
                "value": "0P0000XW77.BO",
                "status": "success"
            },
            "portfolio": {
                "available": True,
                "rows": [...],
                "dataframe": ...
            },
            "expected_change": {
                "status": "success",
                "estimated_pct_change": 0.0123,
                "holdings": [...]
            },
            "debug_message": "Ticker lookup success for fund 118955 | Portfolio extracted (10 rows)"
        }
    ]
}
```

---

## How the workflow works

1. AMFI NAV data is fetched from the official source.
2. The data is parsed and filtered by the requested fund IDs.
3. Each fund is processed to find its Yahoo ticker.
4. Portfolio holdings are retrieved from Yahoo Finance.
5. Stock-level price metrics are fetched and used to estimate the fund’s expected change.
6. The results are aggregated into a nested structure for further automation.
7. Processing is done concurrently for multiple funds to reduce runtime.

---

## Notes

- The ticker mapping is currently stored in ticker_map.json.
- If a fund does not have a ticker mapping, the script marks it as missing and skips portfolio lookup.
- Portfolio extraction depends on Yahoo Finance data availability and may vary by ticker.
- The expected-change estimate is based on available holding data and stock price movement metrics, so it may be incomplete when some holdings are missing or unavailable.

---

## License

MIT License
