"""
stock_finance_fetcher.py

Utility module to fetch real-time market prices, previous closing prices,
and fractional intraday price movements using yfinance.
"""

import json
import logging
from typing import Dict, List, Any
import yfinance as yf

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_stock_finance_metrics(tickers: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Fetches real-time market metrics for a list of Yahoo Finance ticker symbols.

    Args:
        tickers (List[str]): List of Yahoo Finance ticker symbols 
                             (e.g., ['RELIANCE.NS', 'GOOG', 'USDINR=X'])

    Returns:
        Dict[str, Dict[str, float]]: Nested dictionary mapping each ticker symbol to:
            - 'live_price': Current live market price (P_live)
            - 'prev_close': Previous trading session closing price (P_prev_close)
            - 'pct_change': Fractional intraday price movement ((P_live - P_prev_close) / P_prev_close)
    """
    if not tickers:
        return {}

    # Deduplicate ticker list while preserving order
    unique_tickers = list(dict.fromkeys(tickers))
    results = {}

    try:
        # Single-batch query via yfinance Tickers wrapper for maximum speed
        ticker_group = yf.Tickers(" ".join(unique_tickers))

        for symbol in unique_tickers:
            try:
                ticker_obj = ticker_group.tickers.get(symbol)
                if not ticker_obj:
                    continue

                fast_info = ticker_obj.fast_info
                live_price = fast_info.get("lastPrice")
                prev_close = fast_info.get("previousClose")

                # Fallback to historical daily prices if fast_info parameters are missing
                if live_price is None or prev_close is None:
                    hist = ticker_obj.history(period="2d")
                    if len(hist) >= 2:
                        prev_close = float(hist["Close"].iloc[-2])
                        live_price = float(hist["Close"].iloc[-1])
                    elif len(hist) == 1:
                        prev_close = float(hist["Open"].iloc[0])
                        live_price = float(hist["Close"].iloc[0])

                if live_price is not None and prev_close and prev_close > 0:
                    # Fractional change: (P_live - P_prev_close) / P_prev_close
                    pct_change = (live_price - prev_close) / prev_close

                    results[symbol] = {
                        "live_price": round(float(live_price), 4),
                        "prev_close": round(float(prev_close), 4),
                        "pct_change": round(float(pct_change), 6),
                    }
                else:
                    logging.warning(f"Unable to retrieve valid price quotes for: {symbol}")

            except Exception as e:
                logging.error(f"Error processing ticker '{symbol}': {e}")

    except Exception as e:
        logging.error(f"Batch request failed: {e}")

    return results


# 🔬 Script Guard for isolated terminal testing
if __name__ == "__main__":
    print("🚀 Executing stock_finance_fetcher.py diagnostic test...\n")

    # Sample batch: NSE Stock + US Stock + Currency Pair
    sample_tickers = ["RELIANCE.NS", "HDFCBANK.NS", "GOOG", "USDINR=X"]

    print(f"Fetching live metrics for sample input: {sample_tickers}\n")
    finance_data = get_stock_finance_metrics(sample_tickers)

    print("📊 Returned Financial Metrics Dictionary:")
    print(json.dumps(finance_data, indent=4))
