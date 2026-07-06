# CALIBER v0.3 — Defender Registry

A defender is the proof mechanism that checks whether the constructor succeeded.
High-risk work is not done until the defender passes or a human accepts the risk.

| Surface/task type | Defender |
|---|---|
| `software_engineering` | unit tests, typecheck, lint, integration tests, code review |
| `agentic_coding` | plan review, test suite, diff review, behavior smoke test, rollback note |
| `tool_calling` | schema validation, dry-run, idempotency key, audit log |
| `workflow_automation` | replay harness, canary, queue dashboard, exception path, kill switch |
| `world_knowledge_current` | citation audit, source freshness check, source diversity check |
| `rag_grounding` | quote verifier, retrieval trace, contradiction check |
| `long_context_synthesis` | source ledger, sampled quote recall, contradiction preservation |
| `math_formal` | deterministic calculator/Python/SymPy or independent proof check |
| `data_analysis` | executable notebook/script, row counts, reconciliation totals |
| `document_ocr_extraction` | schema validation, OCR confidence, spot-check against source image/PDF |
| `regulated_data_compliance` | approved compliant deployment proof, privacy scrub/check, minimum-necessary fields, audit log |
| `voice_agent` | call simulator, transcript QA, fallback/transfer rule, cost/duration cap |
| `image_generation` | artifact review, prompt-adherence checklist, brand/safety check |
| `video_generation` | artifact review, temporal consistency check, rights/safety check |
| `audio_asr` | transcript sample QA, domain-term recall, speaker/consent policy |
| `robotics_embodied` | simulator, hardware safety case, emergency stop, human supervision |
| `real_world_safety` | formal safety case, canary, kill switch, human gate |
| `external_send_or_write` | approval receipt, dry-run, audit log, rollback/undo plan |

## Defender output

```text
Defender:
- verifier:
- pass threshold:
- evidence artifact:
- escalation if failed:
- human gate:
```
