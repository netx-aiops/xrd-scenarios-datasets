# Security Policy

## Scope

This repository contains a **static evaluation dataset** — JSON scenario
manifests and Markdown documentation. It ships **no executable code, no runtime,
no dependencies, and no CI that runs untrusted input**, so the classic software
vulnerability surface is minimal.

The security-relevant concerns for a dataset like this are instead:

- accidental inclusion of secrets, credentials, or tokens;
- accidental inclusion of production, customer, or personally identifiable data
  (this benchmark is synthetic / lab-generated and must stay that way);
- tampering with gold labels that would silently corrupt evaluation results.

## Reporting a vulnerability

Please report suspected security issues **privately** — not in a public issue or
pull request:

- **Preferred:** GitHub Private vulnerability reporting
  (repository → **Security** → *Report a vulnerability*).
- **Alternative:** contact the maintainer, [@tikoehle](https://github.com/tikoehle),
  directly.

Include the affected file(s), a description, and — if applicable — how to
reproduce. We aim to acknowledge reports within a reasonable time and will
coordinate a fix and disclosure. Please do **not** publicly disclose the details
of a sensitive finding before it has been addressed.

## Supported versions

The latest tagged release is supported; fixes ship as new releases under the
repository's semantic-versioning policy (see the [dataset card](README.md)).

| Version | Supported |
| --- | --- |
| 1.0.x | :white_check_mark: |
