"""
stock_finance_fetcher.py

Utility module to fetch real-time market prices, previous closing prices,
and fractional intraday price movements using yfinance.
"""

import json
import logging
import os
import warnings
from typing import Dict, List, Any, Optional
import math

import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("yahooquery").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.WARNING)


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


def is_invalid(val: Any) -> bool:
    """Check if a numeric value is missing or NaN safely."""
    if val is None or not isinstance(val, (int, float)):
        return True
    return math.isnan(val)


def _safe_float(value: Any) -> Optional[float]:
    """Convert a value to float when possible."""
    try:
        val = float(value)
        return None if math.isnan(val) else val
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

    # Clear proxy settings before executing web request
    _clear_proxy_environment()

    # Deduplicate ticker list, normalize to UPPERCASE, and strip whitespace
    unique_tickers = list(dict.fromkeys([t.strip().upper() for t in tickers if isinstance(t, str) and t.strip()]))
    results = {}

    try:
        # Single-batch query via yfinance Tickers wrapper
        ticker_group = yf.Tickers(" ".join(unique_tickers))

        for symbol in unique_tickers:
            try:
                ticker_obj = ticker_group.tickers.get(symbol)
                if not ticker_obj:
                    continue

                fast_info = getattr(ticker_obj, "fast_info", {})
                if fast_info is None or not hasattr(fast_info, "get"):
                    fast_info = {}

                # Cross-version compatibility check (camelCase OR snake_case)
                live_price = _safe_float(fast_info.get("lastPrice") or fast_info.get("last_price"))
                prev_close = _safe_float(fast_info.get("previousClose") or fast_info.get("previous_close"))

                # Fallback to historical daily prices if fast_info missing or invalid
                if is_invalid(live_price) or is_invalid(prev_close) or prev_close <= 0:
                    try:
                        hist = ticker_obj.history(period="2d")
                    except Exception as history_error:
                        logging.debug(f"History fallback failed for {symbol}: {history_error}")
                        hist = None

                    if hist is not None and not hist.empty:
                        clean_closes = hist["Close"].dropna()
                        if len(clean_closes) >= 2:
                            prev_close = _safe_float(clean_closes.iloc[-2])
                            live_price = _safe_float(clean_closes.iloc[-1])
                        elif len(hist) == 1:
                            # Use Open price as baseline for intraday shift if only 1 day is available
                            open_price = _safe_float(hist["Open"].iloc[0])
                            close_price = _safe_float(hist["Close"].iloc[0])
                            prev_close = open_price if (open_price and open_price > 0) else close_price
                            live_price = close_price

                # Final validation check
                if is_invalid(live_price) or is_invalid(prev_close) or prev_close <= 0:
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

    # Sample batch testing lowercase normalization & mixed asset types
    sample_tickers = ["reliance.ns", "HDFCBANK.NS", "goog", "USDINR=X"]

    print(f"Fetching live metrics for sample input: {sample_tickers}\n")
    finance_data = get_stock_finance_metrics(sample_tickers)

    print("📊 Returned Financial Metrics Dictionary:")
    print(json.dumps(finance_data, indent=4))
