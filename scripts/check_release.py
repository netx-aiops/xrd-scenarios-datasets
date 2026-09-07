#!/usr/bin/env python3
"""Release validation: published counts must match released manifests on disk.

Reviewer-mandated release check (2026-07-14, rides the v1.2.0 release): the
v1.0.0 CITATION shipped claiming "70 scenarios" while the tree held 66 — the
count drifted because nothing compared prose to disk. This script is that
comparison. Run it before tagging any release:

    python3 scripts/check_release.py

Checks (stdlib-only, exit 1 on any mismatch):
  * every */*/meta.json parses as JSON and names its own profile/scenario dirs;
  * released scenario/profile counts == the counts in CITATION.cff and README;
  * pending-live-verification candidates have no asserted logging gold;
  * CITATION version is semver-shaped and date-released is a valid ISO date.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(errors: list[str]) -> None:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)


def main() -> None:
    errors: list[str] = []

    manifests = sorted(ROOT.glob("*/*/meta.json"))
    released: list[Path] = []
    pending: list[Path] = []
    for m in manifests:
        try:
            data = json.loads(m.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{m.relative_to(ROOT)}: invalid JSON ({e})")
            continue
        if data.get("profile") != m.parents[1].name:
            errors.append(
                f"{m.relative_to(ROOT)}: profile field "
                f"{data.get('profile')!r} != directory {m.parents[1].name!r}"
            )
        if data.get("scenario") != m.parents[0].name:
            errors.append(
                f"{m.relative_to(ROOT)}: scenario field "
                f"{data.get('scenario')!r} != directory {m.parents[0].name!r}"
            )
        status = data.get("release_status", "released")
        if status == "released":
            released.append(m)
        elif status == "pending-live-verification":
            pending.append(m)
            if data.get("expected_symptoms") != []:
                errors.append(
                    f"{m.relative_to(ROOT)}: pending candidate must not assert "
                    "expected_symptoms"
                )
            if data.get("is_silent") is not False:
                errors.append(
                    f"{m.relative_to(ROOT)}: pending candidate cannot assert a silent outcome"
                )
        else:
            errors.append(
                f"{m.relative_to(ROOT)}: unsupported release_status {status!r}"
            )

    released_profiles = sorted({m.parents[1].name for m in released})

    citation = (ROOT / "CITATION.cff").read_text()
    m_count = re.search(
        r"(\d+)\s+Cisco IOS-XR/IOS-XE network fault scenarios", citation
    )
    m_prof = re.search(r"across\s+(\d+)\s+topology profiles", citation)
    m_ver = re.search(r"^version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", citation, re.M)
    m_date = re.search(
        r'^date-released:\s*"([0-9]{4}-[0-9]{2}-[0-9]{2})"\s*$', citation, re.M
    )
    if not m_count or int(m_count.group(1)) != len(released):
        errors.append(
            f"CITATION.cff scenario count "
            f"{m_count.group(1) if m_count else '<missing>'} "
            f"!= {len(released)} released manifests on disk"
        )
    if not m_prof or int(m_prof.group(1)) != len(released_profiles):
        errors.append(
            f"CITATION.cff profile count "
            f"{m_prof.group(1) if m_prof else '<missing>'} "
            f"!= {len(released_profiles)} released profile dirs on disk"
        )
    if not m_ver:
        errors.append("CITATION.cff version missing or not semver")
    if not m_date:
        errors.append("CITATION.cff date-released missing or not ISO YYYY-MM-DD")
    else:
        try:
            datetime.date.fromisoformat(m_date.group(1))
        except ValueError:
            errors.append(f"CITATION.cff date-released invalid: {m_date.group(1)}")

    readme = (ROOT / "README.md").read_text()
    m_readme = re.search(r"(\d+)\s+released network fault scenarios", readme)
    if not m_readme or int(m_readme.group(1)) != len(released):
        errors.append(
            f"README.md scenario count "
            f"{m_readme.group(1) if m_readme else '<missing>'} "
            f"!= {len(released)} released manifests on disk"
        )

    if errors:
        fail(errors)
    print(
        f"OK: {len(released)} released scenarios / "
        f"{len(released_profiles)} released profiles; {len(pending)} pending; "
        f"CITATION v{m_ver.group(1)} ({m_date.group(1)}) "
        "and README agree with released disk state."
    )


if __name__ == "__main__":
    main()
