"""
stock_finance_fetcher.py

Utility module to fetch real-time market prices, previous closing prices,
and fractional intraday price movements using yfinance.
"""

import json
import logging
import os
import warnings
from typing import Dict, List, Any

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

import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("yahooquery").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.WARNING)


def _safe_float(value: Any) -> float | None:
    """Convert a value to float when possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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

                fast_info = getattr(ticker_obj, "fast_info", {})
                if not isinstance(fast_info, dict):
                    fast_info = {}

                live_price = _safe_float(fast_info.get("lastPrice"))
                prev_close = _safe_float(fast_info.get("previousClose"))

                if live_price is None or prev_close is None or prev_close <= 0:
                    try:
                        hist = ticker_obj.history(period="2d")
                    except Exception as history_error:
                        logging.debug(f"History fallback failed for {symbol}: {history_error}")
                        hist = None

                    if hist is not None and not hist.empty:
                        if len(hist) >= 2:
                            prev_close = _safe_float(hist["Close"].iloc[-2])
                            live_price = _safe_float(hist["Close"].iloc[-1])
                        elif len(hist) == 1:
                            prev_close = _safe_float(hist["Open"].iloc[0])
                            live_price = _safe_float(hist["Close"].iloc[0])

                if live_price is None or prev_close is None or prev_close <= 0:
                    logging.debug(f"Unable to retrieve valid price quotes for: {symbol}")
                    continue

                pct_change = (live_price - prev_close) / prev_close
                results[symbol] = {
                    "live_price": round(float(live_price), 4),
                    "prev_close": round(float(prev_close), 4),
                    "pct_change": round(float(pct_change), 6),
                }

            except Exception as e:
                logging.debug(f"Skipping ticker '{symbol}' due to error: {e}")

    except Exception as e:
        logging.debug(f"Batch request failed: {e}")

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
