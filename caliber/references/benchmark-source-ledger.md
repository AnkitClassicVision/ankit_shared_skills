# CALIBER v0.3 — Benchmark and Evidence Ledger

Use evidence to set per-surface model levels. Do not flatten all evidence into a
single leaderboard.

## Evidence weights

1. **Internal task evals / production fixtures** — highest weight when they match
   the target workflow.
2. **Independent benchmarks** — useful when mapped to the correct surface.
3. **Model-maker reports** — useful but self-interested; store separately.
4. **Social/practitioner reviews** — useful for ergonomics, hidden failure modes,
   latency, taste, refusal behavior, and agent loop behavior; not a score alone.
5. **Demos/anecdotes** — store as examples unless reproducible.

## Benchmark families by surface

| Surface cluster | Benchmark families | Warning |
|---|---|---|
| reasoning/science | GPQA Diamond, HLE, ARC-AGI, LiveBench | MMLU is saturated at frontier. |
| math | AIME, MATH, FrontierMath | GSM8K/AIME may be saturated; prefer fresh/harder tests. |
| coding | SWE-bench Verified/Pro, Aider, Terminal-Bench | HumanEval is saturated. |
| agents/tool use | BFCL, tau-bench, OSWorld, WebArena, METR time horizons | Harness quality strongly affects results. |
| long context | RULER, MRCR, LongBench, Needle variants | Context size is not effective recall. |
| vision/docs | MMMU, MathVista, OCRBench, DocVQA, ChartQA | Compliance can override model accuracy. |
| video | Video-MME, MVBench, VBench | Generation and understanding are separate surfaces. |
| human preference | Chatbot Arena, WebDev Arena, creative Arena, field reviews | Good for taste; weak for factual safety. |
| robotics | robotics sim/real success suites | Hardware and safety case dominate. |

## Evidence record shape

```yaml
- evidence_id: swebench_verified_2026_07
  source_type: independent_benchmark
  source_url: https://...
  surface: software_engineering
  model_id: provider/model
  metric: pass_rate
  value: null
  date_observed: null
  confidence: low | medium | high
  notes: "Do not use until source and version are verified."
```
