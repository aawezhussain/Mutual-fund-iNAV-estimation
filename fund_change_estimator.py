from pprint import pprint
from typing import Any, Dict, List

from stock_finance_fetcher import get_stock_finance_metrics


def _coerce_weight(value: Any) -> float | None:
    """Convert common weight representations to a float."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        cleaned = cleaned.rstrip("%")
        try:
            return float(cleaned)
        except ValueError:
            return None

    return None


def _normalize_weights(weights: List[float]) -> List[float]:
    """Normalize weights so they sum to 1 when possible."""
    total = sum(weights)
    if total <= 0:
        return [0.0 for _ in weights]
    return [w / total for w in weights]


def estimate_fund_expected_change(results_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate fund-level expected daily change from portfolio weights and per-stock price moves."""
    fund_details = results_payload.get("fund_details", [])
    updated_fund_details = []

    for fund in fund_details:
        portfolio_rows = fund.get("portfolio", {}).get("rows", []) or []
        holdings = []
        weights = []
        symbols = []

        for row in portfolio_rows:
            if not isinstance(row, dict):
                continue

            symbol = row.get("symbol")
            weight = None
           
            weight = _coerce_weight(row.get("holdingPercent"))
            
            if not symbol or weight is None:
                continue

            symbols.append(symbol)
            weights.append(weight)
            holdings.append(
                {
                    "symbol": symbol,
                    "weight": weight,
                }
            )

        if not holdings:
            updated_fund_details.append(
                {
                    **fund,
                    "expected_change": {
                        "status": "no_holdings",
                        "estimated_pct_change": None,
                        "holdings": [],
                    },
                }
            )
            continue

        normalized_weights = _normalize_weights(weights)
        finance_metrics = get_stock_finance_metrics(symbols)

        weighted_contributions = []
        weighted_total = 0.0
        valid_count = 0

        for holding, normalized_weight in zip(holdings, normalized_weights):
            symbol = holding["symbol"]
            metric = finance_metrics.get(symbol, {})
            pct_change = metric.get("pct_change")

            if pct_change is None:
                continue

            contribution = normalized_weight * float(pct_change)
            weighted_total += contribution
            valid_count += 1
            weighted_contributions.append(
                {
                    **holding,
                    "stock_pct_change": float(pct_change),
                    "weighted_contribution": contribution,
                }
            )

        if valid_count == 0:
            status = "no_valid_metrics"
            estimated_pct_change = None
        else:
            status = "success"
            estimated_pct_change = weighted_total

        updated_fund_details.append(
            {
                **fund,
                "expected_change": {
                    "status": status,
                    "estimated_pct_change": estimated_pct_change,
                    "holdings": weighted_contributions,
                },
            }
        )

    result_payload = {
        **results_payload,
        "fund_details": updated_fund_details,
    }

    #print("\n[estimate_fund_expected_change] Result:")
    #pprint(result_payload["fund_details"][0]["expected_change"] if result_payload.get("fund_details") else {})

    return result_payload


if __name__ == "__main__":
    sample_payload = {
        "fund_details": [
            {
                "fund_id": "demo-fund",
                "fund_name": "Demo Fund",
                "portfolio": {
                    "rows": [
                        {"symbol": "RELIANCE.NS", "holdingPercent": "10%"},
                        {"symbol": "HDFCBANK.NS", "holdingPercent": "20%"},
                    ]
                },
            }
        ]
    }

    estimate_fund_expected_change(sample_payload)
