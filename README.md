# AMFI Mutual Fund NAV Fetcher

This project fetches mutual fund NAV data from AMFI, maps fund IDs to Yahoo Finance tickers, and extracts portfolio holdings for further analysis.

It is designed for workflow automation and research around mutual fund data, with the main script returning a structured nested payload that can be reused by other modules.

Data source: https://www.amfiindia.com/spages/NAVAll.txt

---

## What the project does

- Fetches the latest NAV data from AMFI
- Parses the NAV dataset and filters by selected fund IDs
- Looks up Yahoo tickers using the local mapping file
- Queries Yahoo Finance for portfolio holdings information
- Builds a nested result payload containing NAV, ticker, portfolio, and debug details
- Prints a compact summary for terminal use
- Processes multiple funds concurrently for faster execution

---

## Current features

- Fetch latest NAV data directly from AMFI
- Parse AMFI NAV records
- Filter by specific scheme codes / fund IDs
- Resolve AMFI codes to Yahoo tickers via ticker_map.json
- Extract portfolio holding data using yahooquery
- Return structured results for downstream processing
- Run ticker/portfolio requests in parallel with ThreadPoolExecutor

---

## Project structure

```text
project/
├── main.py
├── amfi_nav_fetcher.py
├── fetch_holdings.py
├── portfolio_valuator.py
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
pip install -r requirements.txt
```

Required packages include:

- requests
- pandas
- yahooquery

---

## Usage

Run the main workflow:

```bash
python main.py
```

The script will:

1. Fetch NAV data from AMFI
2. Filter the selected fund IDs
3. Resolve Yahoo tickers
4. Extract portfolio data
5. Print a summary and return a nested payload

---

## Example output

The terminal output includes:

- the AMFI NAV table
- per-fund ticker info
- portfolio row counts
- debug messages for each fund

The script also returns a nested payload in the following shape:

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
5. The results are aggregated into a nested structure for further automation.
6. Processing is done concurrently for multiple funds to reduce runtime.

---

## Notes

- The ticker mapping is currently stored in ticker_map.json.
- If a fund does not have a ticker mapping, the script marks it as missing and skips portfolio lookup.
- Portfolio extraction depends on Yahoo Finance data availability and may vary by ticker.

---

## License

MIT License
