---
name: handoff
display_name: Handoff
viewer_summary: Compact project state into a redacted continuation packet for another agent or session.
description: Compact the current conversation into a handoff document for another agent to pick up.
bundle: run-project
phase: transfer
category: transfer
artifact_type: handoff-packet
primary_command: /handoff
triggers:
  - handoff this
  - summarize for next agent
  - continue in another session
  - resume packet
inputs:
  - Current conversation or project state
  - Next-session purpose
  - Sensitive data constraints
outputs:
  - Redacted handoff document
  - Resume instructions
  - Open questions
  - Known decisions
dependencies:
  before:
    - run-project
    - writing-plans
    - skillify
  after: []
risk_level: low
side_effects: draft-only
requires_repo: false
requires_network: false
argument-hint: What will the next session be used for?
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
