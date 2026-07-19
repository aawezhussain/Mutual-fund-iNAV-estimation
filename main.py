"""
Main script to fetch and display AMFI Mutual Fund NAV data
"""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from amfi_nav_fetcher import get_nav_data, print_results
from portfolio_valuator import get_ticker_from_json
from fetch_holdings import check_fund_portfolio


def _build_fund_detail(record):
    """Fetch ticker and portfolio data for a single fund record."""
    fund_id, fund_name, nav_date, nav_value = record

    ticker_value = get_ticker_from_json(fund_id)
    ticker_status = "success" if ticker_value else "missing"
    portfolio_df = check_fund_portfolio(ticker_value) if ticker_value else None

    portfolio_rows = []
    if portfolio_df is not None:
        portfolio_rows = portfolio_df.to_dict(orient="records")

    debug_message = (
        f"Ticker lookup {ticker_status} for fund {fund_id}"
        if ticker_value
        else f"Ticker lookup failed for fund {fund_id}"
    )

    if portfolio_df is not None:
        debug_message += f" | Portfolio extracted ({len(portfolio_rows)} rows)"
    else:
        debug_message += " | Portfolio unavailable"

    return {
        "fund_id": fund_id,
        "fund_name": fund_name,
        "nav_date": nav_date,
        "nav_value": nav_value,
        "ticker": {
            "value": ticker_value,
            "status": ticker_status,
        },
        "portfolio": {
            "available": portfolio_df is not None,
            "rows": portfolio_rows,
            "dataframe": portfolio_df,
        },
        "debug_message": debug_message,
    }


def _print_processed_summary(results_payload):
    """Print a compact summary of the processed fund details."""
    print("\n" + "=" * 80)
    print("Processed Fund Details".center(80))
    print("=" * 80)

    for fund in results_payload["fund_details"]:
        print(f"\n[{fund['fund_id']}] {fund['fund_name']}")
        print(f"  NAV Date : {fund['nav_date']}")
        print(f"  NAV Value: ₹{fund['nav_value']}")
        print(f"  Ticker   : {fund['ticker']['value'] or 'N/A'}")
        print(f"  Status   : {fund['ticker']['status']}")
        print(f"  Debug    : {fund['debug_message']}")

        if fund["portfolio"]["available"]:
            print(f"  Portfolio Rows: {len(fund['portfolio']['rows'])}")
        else:
            print("  Portfolio Rows: 0")


def main():
    """Main execution function"""

    # Clear terminal
    subprocess.run(["clear"])

    # Define the fund IDs to retrieve
    fund_ids = {118955, 118989, 122639, 147946, 119783}

    print("\n" + "=" * 80)
    print("AMFI Mutual Fund NAV Data Retrieval".center(80))
    print("=" * 80 + "\n")

    # Fetch NAV data
    nav_results = get_nav_data(fund_ids)

    if not nav_results:
        print("❌ No data found for the requested fund IDs\n")
        return {
            "fund_ids": sorted(fund_ids),
            "nav_results": [],
            "fund_details": [],
        }

    # Print results
    print_results(nav_results, "Retrieved Fund Data")
    print(f"Total funds retrieved: {len(nav_results)}\n")

    results_payload = {
        "fund_ids": sorted(fund_ids),
        "nav_results": nav_results,
        "fund_details": [],
    }

    max_workers = max(1, min(5, len(nav_results)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results_payload["fund_details"] = list(executor.map(_build_fund_detail, nav_results))

    _print_processed_summary(results_payload)

    print("\n" + "-" * 80)
    print(f"\n✅ Successfully processed {len(results_payload['fund_details'])} fund(s)")

    return results_payload


if __name__ == "__main__":
    results_payload = main()
    print("\nNested payload ready for further action:")
    #print(results_payload)
