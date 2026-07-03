# Contributing to XRd Scenario Datasets

Thank you for your interest. This repository is a **curated gold-standard
evaluation benchmark**, not a general-purpose codebase, so contributions are
handled with correctness and stability of the gold labels as the priority.

## How changes are accepted

- **All changes land via pull request.** Direct pushes to `main` are disabled.
- **Every pull request is reviewed.** No PR — internal or external — is merged
  without review and approval from a maintainer, enforced by
  [`CODEOWNERS`](.github/CODEOWNERS) plus branch protection.
- **Opening a pull request or issue grants no write access.** A maintainer must
  explicitly approve and merge; nothing lands automatically.

## Changes to gold labels require maintainer sign-off

The `expected_rca` gold answers — and the `apply` / `revert` /
`expected_symptoms` that define each scenario — are the scored ground truth of
the benchmark. Changes to them:

- **require explicit maintainer approval** and a clear rationale in the PR;
- must preserve the scoring contract and answer conventions in the
  [dataset card](README.md) (e.g. the root-cause device is named by its
  management IP);
- are treated as a **major** version bump under the repository's semantic
  versioning, because they change what "correct" means for every consumer.

If you believe a gold is wrong, please **open an issue first** — describe the
scenario, the current gold, the proposed gold, and the evidence — before opening
a pull request.

## Good contributions

- typo / formatting fixes in documentation (patch);
- new scenarios that follow the existing `meta.json` schema (minor);
- clarifications to the dataset card.

## Ground rules

- Never include production, customer, or personally identifiable data — this is a
  synthetic / lab-generated benchmark and must stay that way.
- Keep each `meta.json` self-contained and valid against the documented fields.
- Prefer one scenario or one focused change per pull request.

By contributing, you agree that your contributions are licensed under the
repository's licenses: **CC-BY-4.0** for data and documentation, and
**Apache-2.0** for any code (see [`LICENSE`](LICENSE)).
