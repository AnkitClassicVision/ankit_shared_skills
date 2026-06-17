# Deep Module Philosophy

Source: the companion "Your codebase is NOT ready for AI" and "Brownfield Rescue" videos.

## Core Definition

**Deep module** = simple interface + complex implementation
**Shallow module** = complex interface + little implementation

The goal of codebase deepening is to move modules from shallow to deep.

## Signs of Shallow Modules

- Many public methods with trivial bodies
- Information leakage across boundaries
- Files that match 1:1 to classes (filesystem is too granular)
- Circular dependencies between adjacent files
- Difficult to describe what a module DOES in one sentence

## Deep Module Design Principles

1. **Information hiding** — the public API should not expose internal state
2. **Simple interfaces over simple implementations** — prefer an easy API even if the internals are complex
3. **Filesystem matches mental model** — code organization should reflect the conceptual model, not the chronology of implementation
4. **Progressive disclosure** — users of a module should not need to understand internals to use the public surface
5. **Seams define boundaries** — where two modules meet, the interface should be small and well-defined

## Brownfield Application

When refactoring legacy code:
- Start with a glossary + shared vocabulary (what do terms mean in this codebase?)
- Add test harness BEFORE refactoring (critical for safety)
- Move incrementally — one boundary at a time
- Preserve backward compatibility through adapter patterns when needed
- The "improve codebase architecture" skill begins with taxonomy, not rewrites

## Anti-Patterns to Watch For

| Anti-Pattern | Detection | Fix |
|-------------|-----------|-----|
| God file | >500 lines in a single file | Extract cohesive behaviors into modules |
| Stringly-typed interfaces | Literal strings passed between modules | Introduce enums or types |
| Premature abstraction | Interface for trivial behavior | Wait until there are 3+ consumers |
| Leaky boundaries | Internal data structures exposed in public API | Introduce mapping/transformation layer |
| Copy-paste coupling | Same code in 5+ places | Extract shared module with configuration |

## Metrics for Deepness

- **Interface surface area**: number of public symbols (lower = deeper)
- **Information hiding index**: percentage of implementation details not in public API
- **Comprehension time**: how long for a new engineer to understand the module's contract
- **Change blast radius**: how many files break when internals change
