# DDD / Clean Architecture Guardrails

This repo follows a layered DDD/Clean Architecture structure. These rules are mandatory for new code and refactors.

## Current Architecture Map

- `cli`: interface adapter (Click commands, user-facing errors and output).
- `application`: use-case orchestration (extract, mask, unmask workflows).
- `domain`: pure business rules (secret selection and masking semantics).
- `infrastructure`: IO and framework details (filesystem, dotenv, config loading, path formatting).

## Dependency Rule (Inward)

Allowed imports:

- `cli -> application`
- `application -> domain`
- `application -> infrastructure`

Disallowed imports:

- `domain -> application`
- `domain -> infrastructure`
- `domain -> click` (or other interface/framework concerns)
- `infrastructure -> application`
- `infrastructure -> cli`

## Placement Rules

Use this rule of thumb before adding code:

- Put logic in `domain` if it is a pure business rule and has no side effects.
- Put logic in `application` if it coordinates a workflow across domain rules and infrastructure operations.
- Put logic in `infrastructure` if it reads/writes files, parses external formats, or depends on framework/library IO.
- Keep `cli` thin: parse args, call application use-cases, print results/errors.

## Do Not Break

- Do not place business decisions in `cli`.
- Do not add side effects or file IO to `domain`.
- Do not bypass `application` by calling `domain` directly from CLI for use-case execution.
- Do not couple `domain` to Click, dotenv, or filesystem APIs.
- Do not reintroduce legacy compatibility modules (`core`, `settings`, `utils`).

## PR Checklist

- [ ] New code is placed in the correct layer.
- [ ] Import direction follows the allowed dependency rule.
- [ ] Domain code is pure and deterministic.
- [ ] Use-case orchestration lives in `application`.
- [ ] IO/framework code lives in `infrastructure`.
- [ ] CLI remains thin and delegates to application use-cases.
- [ ] Tests cover the changed behavior at the appropriate layer.
