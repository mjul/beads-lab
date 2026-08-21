---
name: test-first
description: Write tests before implementation using outside-in TDD. Prefer high-level module or acceptance tests that encode requirements and stay decoupled from internals; add low-level unit tests only when they pay for themselves. Use when adding features, fixing bugs, designing APIs, or when the user asks for TDD, test-first, or behavior-driven coverage.
---

# Test-First (Outside-In)

Write the failing test that expresses the requirement, then implement just enough to make it pass. Prefer tests that would still make sense after a refactor.

## When to apply

- New behavior, bug fixes, or API design
- User asks for TDD, test-first, or requirement-level coverage
- Expanding or replacing existing code where behavior should stay stable

Skip only when the change is pure docs/config with no behavioral surface, or the user explicitly asks for implementation-only work.

## Workflow

1. **Name the requirement** in one sentence: who/what, under what conditions, what observable outcome.
2. **Write a high-level test first** at the module, package, or public-API boundary that asserts that outcome.
3. **Run it and watch it fail** for the right reason (missing behavior, not a setup mistake).
4. **Implement the minimum** to pass. Prefer the public surface the test already uses.
5. **Refactor** with the test green. Keep the test stable while internals move.
6. **Add lower-level tests only if needed** (see below). Do not start with them.

## Prefer high-level (module) tests

High-level tests are the default. They:

- Read like requirements or acceptance criteria
- Exercise the public API, CLI, HTTP handler, message handler, or module façade
- Assert observable results: return values, outputs, persisted state, emitted events, status codes
- Avoid private helpers, internal class structure, call order, and framework wiring details

Good shape:

```text
given <precondition / input>
when  <action on the public boundary>
then  <observable outcome>
```

Name tests after behavior (`creates_issue_when_title_is_valid`), not after methods (`test_create_issue`).

## Stay decoupled from implementation

Do:

- Depend on stable contracts (public functions, ports, fixtures that build domain inputs)
- Assert outcomes, not collaboration graphs
- Use fakes or stubs only at true external boundaries (clock, network, filesystem, DB) when the high-level test would otherwise be slow, flaky, or unsafe

Do not:

- Assert which private methods were called, in what order
- Reach into private fields or package-internal modules to set up or verify
- Mirror the production call graph with mocks “one mock per collaborator”
- Encode algorithms, data-structure choices, or class hierarchies in the test

If a refactor that preserves behavior forces a large test rewrite, the test was too coupled—fix the test toward the boundary.

## When to add low-level tests

Add focused unit tests only when a high-level test is the wrong tool:

| Add a low-level test when… | Prefer to keep it high-level when… |
| --- | --- |
| Logic is dense (parsing, pricing, state machines) and failures are hard to localize from the module test | Behavior is a straight orchestration of clear steps |
| You need many examples/edge cases and the module path is expensive | A few examples at the boundary already lock the requirement |
| A pure helper has a crisp contract worth pinning | The helper exists only to support one module path |
| You are isolating a known regression in a narrow algorithm | The bug is best described as a user-visible requirement |

Low-level tests still describe **behavior of that unit’s contract**, not its internals. They support the high-level suite; they do not replace it.

## Bug fixes

1. Write a high-level (or the narrowest sufficient) test that reproduces the bug.
2. Confirm it fails.
3. Fix the code.
4. Keep the test as regression coverage.

## Checklist before merging

- [ ] At least one high-level test states the requirement in observable terms
- [ ] Tests were written (or updated) before or with the behavior change, and failed before the fix
- [ ] No new mocks of internal collaborators without a clear boundary reason
- [ ] Low-level tests, if any, cover justified complexity—not every private function
- [ ] Test names and arrange/act/assert structure remain readable as documentation

## Project notes

This repo uses `pytest` (`uv run pytest`). Put requirement-level tests under `tests/`, targeting public entry points in `src/`. Match existing fixtures and layout when present.
