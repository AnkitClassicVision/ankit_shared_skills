#!/usr/bin/env python3
"""
discover-rank.py
Reads a raw Gemini deep-scan output and produces a ranked candidate list
for the Grill gate. Uses the companion "deep module" heuristics + testability.

Usage:
    python discover-rank.py <gemini-analysis.json> [--top-k 5]

Input: JSON with fields from Gemini scan:
    [
      {
        "module_path": "string",
        "public_symbols": int,
        "lines_of_code": int,
        "complexity_score": float,  # cyclomatic or similar
        "fan_in": int,             # how many modules import this
        "fan_out": int,            # how many modules this imports
        "test_coverage_pct": float or null,
        "description": "string"
      }
    ]

Output: JSON array sorted by composite_score descending:
    [
      {
        "module_path": "...",
        "composite_score": float,
        "leverage": float,
        "risk": float,
        "reasoning": "..."
      }
    ]
"""

import argparse
import json
import math
import sys


def compute_leverage(item: dict) -> float:
    """
    Leverage = how much value we get from deepening this module.
    Higher fan_in (many consumers) = high leverage.
    Higher fan_out (depends on many things) = lower leverage (harder to isolate).
    """
    fan_in = item.get("fan_in", 0)
    fan_out = max(item.get("fan_out", 1), 1)
    # Normalize: log scale to dampen outliers
    return math.log1p(fan_in) / math.log1p(fan_out)


def compute_risk(item: dict) -> float:
    """
    Risk = how dangerous it is to refactor this module.
    Lower test coverage = higher risk.
    Higher complexity = higher risk.
    More lines of code = higher risk.
    """
    coverage = item.get("test_coverage_pct") or 0.0
    complexity = item.get("complexity_score", 1.0)
    loc = item.get("lines_of_code", 1)

    # Coverage factor: 0% -> 2.0, 100% -> 0.2
    coverage_risk = max(2.0 - (coverage / 100.0) * 1.8, 0.2)

    # Complexity factor: log scale
    complexity_risk = math.log1p(complexity) / 3.0

    # Size factor: diminishing returns
    size_risk = math.log1p(loc) / 6.0

    return coverage_risk * 0.5 + complexity_risk * 0.3 + size_risk * 0.2


def compute_composite(leverage: float, risk: float) -> float:
    """
    Composite score rewards high leverage and penalizes high risk.
    We want high leverage, low risk.
    """
    # Normalize leverage and risk to roughly 0-1 range
    norm_leverage = min(leverage / 2.0, 1.0)
    norm_risk = min(risk / 2.0, 1.0)
    return norm_leverage * 0.6 + (1.0 - norm_risk) * 0.4


def rank_candidates(input_path: str, top_k: int = 5):
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    candidates = raw if isinstance(raw, list) else [raw]

    results = []
    for item in candidates:
        leverage = compute_leverage(item)
        risk = compute_risk(item)
        composite = compute_composite(leverage, risk)

        reasoning_parts = []
        if leverage > 0.7:
            reasoning_parts.append(f"high leverage (fan_in={item.get('fan_in', 0)})")
        elif leverage < 0.3:
            reasoning_parts.append(f"low leverage (fan_in={item.get('fan_in', 0)})")

        coverage = item.get("test_coverage_pct")
        if coverage is not None and coverage < 50:
            reasoning_parts.append(f"low test coverage ({coverage:.0f}%)")
        elif coverage is not None and coverage > 80:
            reasoning_parts.append(f"good test coverage ({coverage:.0f}%)")

        if item.get("complexity_score", 0) > 20:
            reasoning_parts.append("high complexity")

        results.append({
            "module_path": item.get("module_path", "unknown"),
            "composite_score": round(composite, 3),
            "leverage": round(leverage, 3),
            "risk": round(risk, 3),
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "moderate candidate",
            "raw": item,
        })

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results[:top_k]


def main():
    parser = argparse.ArgumentParser(description="Rank codebase deepening candidates")
    parser.add_argument("input_json", help="Path to Gemini analysis JSON")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top candidates to return")
    args = parser.parse_args()

    ranked = rank_candidates(args.input_json, top_k=args.top_k)
    print(json.dumps(ranked, indent=2))


if __name__ == "__main__":
    main()
