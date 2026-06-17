#!/usr/bin/env python3
"""
grill-presentation.py
Formats ranked candidate list for human review at the Grill gate.
Produces an HTML page with candidate cards, leverage/risk scores,
and decision buttons.

Usage:
    python grill-presentation.py <ranked-candidates.json> [--output grill.html]
"""

import argparse
import json
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Grill Gate — Deepen Candidates</title>
<style>
body { font-family: system-ui, sans-serif; background: #0f1115; color: #e6e8ec; padding: 20px; }
h1 { margin-top: 0; }
.candidate { background: #1a1d23; border: 1px solid #2a2e38; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.candidate h3 { margin: 0 0 8px 0; color: #f2c94c; }
.metrics { display: flex; gap: 20px; font-size: 0.9rem; color: #8b919e; margin-bottom: 8px; }
.score { color: #56ccf2; font-weight: 600; }
.reasoning { font-size: 0.85rem; color: #8b919e; line-height: 1.5; }
.actions { margin-top: 12px; display: flex; gap: 10px; }
button { padding: 6px 14px; border-radius: 4px; border: none; cursor: pointer; font-weight: 600; }
.btn-deepen { background: #6fcf97; color: #0f1115; }
.btn-defer { background: #f2994a; color: #0f1115; }
.btn-reject { background: #eb5757; color: #fff; }
</style>
</head>
<body>
<h1>Grill Gate: Deepen Candidates</h1>
<p>Select which modules to deepen, defer, or reject.</p>
{{CARDS}}
</body>
</html>"""


def build_card(candidate: dict, idx: int) -> str:
    return f"""
<div class="candidate" data-index="{idx}">
  <h3>#{idx + 1} {candidate['module_path']}</h3>
  <div class="metrics">
    <span>Composite: <span class="score">{candidate['composite_score']}</span></span>
    <span>Leverage: {candidate['leverage']}</span>
    <span>Risk: {candidate['risk']}</span>
  </div>
  <div class="reasoning">{candidate['reasoning']}</div>
  <div class="actions">
    <button class="btn-deepen" onclick="alert('DEEPEN: {candidate['module_path']}')">Deepen</button>
    <button class="btn-defer" onclick="alert('DEFER: {candidate['module_path']}')">Defer</button>
    <button class="btn-reject" onclick="alert('REJECT: {candidate['module_path']}')">Reject</button>
  </div>
</div>
"""


def main():
    parser = argparse.ArgumentParser(description="Grill gate presentation")
    parser.add_argument("input_json", help="Path to ranked candidates JSON")
    parser.add_argument("--output", default="grill.html", help="Output HTML path")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    cards = "\n".join(build_card(c, i) for i, c in enumerate(candidates))
    html = HTML_TEMPLATE.replace("{{CARDS}}", cards)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Grill presentation written to {args.output}")


if __name__ == "__main__":
    main()
