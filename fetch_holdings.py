import os
import pandas as pd
from yahooquery import Ticker


def _clear_proxy_environment() -> None:
    """Disable inherited proxy settings before querying Yahoo Finance."""
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    ):
        os.environ.pop(key, None)


def check_fund_portfolio(yahoo_ticker: str):
    """
    Connects to Yahoo Finance via yahooquery, extracts the raw nested JSON 
    portfolio holdings data, and prints it out as a structured table.
    """
    print(f"📡 Querying Yahoo database for ticker: {yahoo_ticker}...")
    _clear_proxy_environment()
    
    # 1. Initialize the network object for the mutual fund
    fund = Ticker(yahoo_ticker)
    
    # 2. Call the dedicated property that holds mutual fund allocation statistics
    holding_info = fund.fund_holding_info
    
    # Safety Check A: Verify if Yahoo returned an error or empty dictionary
    if not holding_info or yahoo_ticker not in holding_info:
        print(f"❌ Error: No holding database entry found for {yahoo_ticker}.")
        return None
        
    # Safety Check B: Verify if the institutional holdings array actually exists
    holdings_list = holding_info[yahoo_ticker].get('holdings', [])
    if not holdings_list:
        print(f"⚠️ Warning: Ticker exists, but its holdings recipe is hidden or empty.")
        return None

    # 3. Convert the list of raw dictionaries into a structured DataFrame
    df = pd.DataFrame(holdings_list)
    
    # 4. Clean up formatting anomalies (e.g. drop cash lines with no stock ticker)
    df = df[df['symbol'].notna() & (df['symbol'] != '')].copy()
    
    return df

# --- STANDALONE TEST RUN ---
if __name__ == "__main__":
    # Test using HDFC Mid-Cap Opportunities Fund Direct Growth ticker
    target_ticker = "0P0000XW8F.BO" 
    
    portfolio_df = check_fund_portfolio(target_ticker)
    
    if portfolio_df is not None:
        print("\n📊 SUCCESS! EXTRACTED PORTFOLIO RECIPE MATRIX:")
        print("=" * 70)
        # Display the full table cleanly in the terminal console
        print(portfolio_df.to_string(index=False))
        print("=" * 70)