# CALIBER v0.3 — Model Registry Summary

This file is the human-readable summary. The structured database lives in
`model-capability-matrix.yaml` and should be refreshed whenever model availability,
pricing, compliance paths, or benchmark results change.

## Current routing stance

- Use **deterministic tools** for level -1 tasks.
- Use **tiny/small/local models** for level 0–1 classification, extraction,
  routing, and privacy-first drafts when they pass fixtures.
- Use **workhorse frontier/API models** for level 2 professional work.
- Use **strong specialist/frontier models** for level 3–4 hard reasoning, coding,
  architecture, long-context synthesis, and multimodal reasoning.
- Use **orchestrated routes** for level 5: decompose first, attach tools,
  defenders, and human gates.
- Reserve **level 6** for future super-frontier capability beyond the current top
  pool.

## Model families to track

| Lane | Examples/classes | Notes |
|---|---|---|
| deterministic | SQL, regex, scripts, APIs | Prefer for exact transforms. |
| tiny/local | Phi/Gemma/Qwen/Llama small classes | Privacy/cost lane; requires local fixtures. |
| workhorse API | Sonnet/GPT/Gemini-class workhorses | Default for normal text/code/spec work. |
| frontier reasoning | Opus/Fable/GPT reasoning/Gemini Pro-class | Hard reasoning, architecture, expensive-to-fail planning. |
| open-weight frontier | DeepSeek, Qwen, GLM/Z.ai, Llama, Mistral, Kimi classes | Useful for local/private/cost leverage; score per surface. |
| long-context | Gemini/Claude/GPT/Kimi/Qwen long-context lanes | Window size must be validated by retrieval/synthesis evals. |
| coding specialist | Codex, Claude Code, Qwen-Coder, DeepSeek-Coder-style lanes | Pair with repo tests and code review. |
| image generation | Midjourney, Imagen, DALL-E, FLUX classes | Media artifact lane, not general reasoning. |
| video generation | Veo, Sora, Runway, Pika classes | Artifact QA and rights/safety review required. |
| audio/voice | Whisper/ASR, ElevenLabs/TTS, Hume/prosody classes | Consent, privacy, and transcript QA matter. |
| robotics/embodied | robotics foundation/action models | Require simulator, safety case, and hardware gates. |

## Compliance rule

A model's surface score is separate from its deployment permissions. regulated/private data requires an approved private/compliant deployment even if a first-party
API version of the same model is more capable.
