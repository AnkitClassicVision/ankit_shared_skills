# CALIBER v0.3 — Surface Taxonomy

Use these surfaces to describe what a task actually requires. Assign a required
level from -1 to 6 for every material surface.

## Language and cognition

| Surface | Covers | Evidence examples |
|---|---|---|
| `text_transform` | summarize, restyle, classify, extract, rewrite | schema adherence, style evals, internal fixtures |
| `instruction_following` | exact constraints, tone, format, refusal boundaries | IFEval-style tests, internal prompt fixtures, user reviews |
| `general_reasoning` | multi-step logic, planning, tradeoffs | LiveBench, HLE, ARC-AGI, GPQA, model cards |
| `math_formal` | arithmetic, symbolic math, proofs, contest/research math | AIME, MATH, FrontierMath; GSM8K only as sanity |
| `science_expert` | biology, chemistry, physics, medical/scientific QA | GPQA Diamond, domain evals, expert review |
| `world_knowledge_current` | current facts, vendor/pricing/news, source validation | web/search freshness, citation audits, source dates |
| `creative_writing_worldbuilding` | fiction, worldbuilding, voice/taste, ideation | Chatbot Arena creative, human review, field reviews |
| `strategy_architecture` | systems design, operating models, business architecture | internal gold cases, expert review, decision residue |

## Reading, memory, and retrieval

| Surface | Covers | Evidence examples |
|---|---|---|
| `long_context_retrieval` | find facts in huge context | RULER, Needle, MRCR, LongBench |
| `long_context_synthesis` | integrate many docs and preserve contradictions | LongBench v2, MMLongBench-Doc, source-ledger evals |
| `rag_grounding` | answer from retrieved sources and cite accurately | RAGAS/ARES-style evals, citation audit, quote verifier |
| `memory_personalization` | stable user/project memory and preference carryover | longitudinal internal evals; usually harness-dependent |

## Code, tools, and agents

| Surface | Covers | Evidence examples |
|---|---|---|
| `code_generation` | snippets and single-file code | HumanEval only as low-level sanity |
| `software_engineering` | repo edits, tests, debugging, architecture | SWE-bench Verified/Pro, Aider, real repo tests |
| `agentic_coding` | long-horizon repo work with tools | Terminal-Bench, RE-Bench/HCAST/SWAA, internal build loops |
| `tool_calling` | function calling, JSON/schema, API sequencing | BFCL, tau-bench, tool-call fixtures |
| `computer_use` | browser/desktop/GUI action | OSWorld, WebArena, browser-task evals |
| `workflow_automation` | queues, retries, approvals, multi-tenant ops | process fixtures, audit logs, replay harnesses |
| `structured_output` | valid JSON, schemas, tables, CSV, config | JSON/schema validators, deterministic parsers |

## Data and documents

| Surface | Covers | Evidence examples |
|---|---|---|
| `data_analysis` | tables, spreadsheets, stats, Python reasoning | pandas/Python proof, spreadsheet evals, unit tests |
| `chart_diagram_understanding` | charts, plots, diagrams, screenshots | ChartQA, PlotQA, screenshot fixtures |
| `document_ocr_extraction` | PDFs, forms, receipts, EOBs | DocVQA, OCRBench, Textract-style comparison |
| `financial_legal_admin` | finance/legal/admin docs and decisions | expert review, source citations, human gate |

## Multimodal and media

| Surface | Covers | Evidence examples |
|---|---|---|
| `vision_static` | image understanding, OCR-adjacent tasks, screenshots | MMMU, MathVista, VQA, OCRBench |
| `image_generation` | create/edit images and design assets | human preference, prompt adherence, brand QA |
| `video_understanding` | temporal reasoning over clips | Video-MME, MVBench, clip QA |
| `video_generation` | generate/edit video and motion | VBench, artifact QA, human review |
| `audio_asr` | speech-to-text, noisy call transcription | WER, call transcript evals, domain-word recall |
| `audio_tts_voice` | generated speech, emotion, latency | MOS, call QA, human review |
| `music_audio_generation` | music/sound generation | human preference, rights/licensing review |
| `multimodal_composition` | text+image+audio+video together | task-specific evals; broad benchmarks insufficient alone |

## Physical and embodied

| Surface | Covers | Evidence examples |
|---|---|---|
| `spatial_reasoning` | maps, 3D, geometry, physical layout | spatial benchmarks, geolocation, robotics sim evals |
| `robotics_embodied` | robot action, manipulation, navigation | sim/real success rates, safety evals |
| `real_world_safety` | actions with human/physical consequences | safety case, simulator, human gate, kill switch |

## Deployment/governance

| Surface | Covers | Evidence examples |
|---|---|---|
| `local_private` | local/offline/private endpoint use | hardware tests, quantization evals, privacy review |
| `baa_phi_compliance` | regulated/private data path | vendor compliance docs, regional deployment proof |
| `latency_cost` | speed, throughput, and price fit | provider pricing, timing logs, cost reports |
| `reliability_observability` | uptime, repeatability, logs, replay | run logs, retry rates, incident records |
| `safety_refusal` | appropriate refusal and non-refusal behavior | safety evals, red-team tests, false-refusal logs |
