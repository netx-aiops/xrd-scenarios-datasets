---
license: cc-by-4.0
language:
- en
pretty_name: "XRd Scenario Datasets — Autonomous Network RCA Evaluation Golds"
tags:
- root-cause-analysis
- network-diagnostics
- agent-evaluation
- benchmark
- ios-xr
- bgp
- ospf
- isis
- srv6
- segment-routing
task_categories:
- text-generation
- question-answering
size_categories:
- n<1K
annotations_creators:
- expert-generated
source_datasets:
- original
---

# Dataset Card for XRd Scenario Datasets

Gold-standard benchmark for evaluating **autonomous network root-cause-analysis
(RCA) agents** against a **live IOS-XR (XRd) network**. Each scenario injects a
single, real fault — a configuration change applied to a running multi-router lab
— and asks an agent to identify the root cause from live telemetry alone. The
agent is **ground-truth-blind**: it sees only the network and a generic question,
never the answer. Its RCA is then scored against an engineer-written gold.

- **Curated by:** Timo Koehler (netx-aiops)
- **Language:** English, with IOS-XR CLI / network configuration
- **License:** CC-BY-4.0 (data & documentation); Apache-2.0 (any bundled code)
- **Repository:** <https://github.com/netx-aiops/xrd-scenarios-datasets>
- **Version:** 1.0.0
- **Point of contact:** the repository issue tracker

## Dataset Summary

60 curated network fault scenarios across 6 IOS-XR network profiles (topologies),
10 each. Each scenario is a self-contained manifest describing one injected fault,
the ground-truth-blind question posed to the agent, the engineer-written gold RCA,
and the exact CLI to inject and revert the fault on the live lab.

| Profile | Focus |
| --- | --- |
| `simple-bgp` | OSPF underlay + iBGP PE–PE |
| `ospf-multi-area-bgp` | multi-area OSPF + eBGP/iBGP + route reflection |
| `ospf-bgp-rr` | dual route-reflector iBGP |
| `isis-ipfrr` | IS-IS + TI-LFA fast-reroute |
| `segment-routing` | IS-IS Segment Routing (SR-MPLS) |
| `srv6-l3vpn` | SRv6 L3VPN (VPNv4-over-IPv6) |

Fault classes span IGP adjacency (area / MTU / authentication / hello-timer /
circuit-type), BGP session and policy (AS mismatch, update-source,
route-reflector-client, route-policy, TCP-MD5), and SR / SRv6 (prefix-SID
conflict, SRGB shift, locator prefix). Several scenarios inject a **deliberately
inert** change — no operational impact — to test an agent's resistance to false
positives.

## Supported Tasks and Intended Use

The primary task is **agentic network root-cause-analysis evaluation**. This
dataset is intended for:

1. evaluating an RCA agent's final root-cause answer against a gold;
2. measuring semantic fact coverage (recall) and claim support (precision);
3. regression-testing RCA pipelines across releases;
4. comparing prompt, planner, memory, retrieval, and tool-use strategies;
5. probing false-positive resistance via the inert-change scenarios.

It is an **evaluation** dataset, **not** intended for model pretraining or
fine-tuning.

## Out-of-Scope Use

- training production models without explicit permission;
- claiming vendor coverage beyond IOS-XR / the documented profiles;
- evaluating general networking knowledge outside the included scenarios;
- security, exploit, or offensive network-automation benchmarking;
- evaluation of real customer environments without additional validation.

## Dataset Structure

```
<profile>/<scenario>/meta.json
```

Each `meta.json` is a self-contained scenario manifest:

| Field | Meaning |
| --- | --- |
| `profile`, `scenario` | identity |
| `question` | the ground-truth-blind prompt shown to the agent |
| `expected_rca` | **the gold** — engineer-written root cause / mechanism / fix; the label the metric scores against |
| `target_routers` | the device(s) carrying the injected fault |
| `description` | human notes on the fault and its mechanism |
| `expected_symptoms`, `expected_symptoms_summary` | the syslog signature the fault produces |
| `expected_state_diffs` | expected operational state changes (where captured) |
| `apply`, `revert` | the exact IOS-XR CLI to inject / undo the fault on the live lab |
| `mode`, `is_silent` | delivery mode (`live`); whether the fault is log-silent |

The **input** an agent is given is `(profile, question)` only; every other field
is held out as ground truth. `expected_rca` is the single field the scoring metric
grades against.

Example (`ospf-multi-area-bgp/r4-ebgp-r5-multihop-removed`):

```json
{
  "profile": "ospf-multi-area-bgp",
  "scenario": "r4-ebgp-r5-multihop-removed",
  "question": "Identify the root cause of the network fault: which device, what changed, and why it breaks.",
  "target_routers": ["R4"],
  "expected_rca": "Root cause: on 100.64.0.104 (R4), `ebgp-multihop` was removed from the R5 eBGP neighbor (192.0.2.5).\nBecause R4 peers with R5 over its loopback, without multihop the BGP packets are sent with TTL=1 and are dropped before reaching R5 when the loopback path is more than one IP hop, so the eBGP session cannot be established and no routes are exchanged.\nFix: restore `ebgp-multihop` on R4's R5 neighbor.",
  "apply":  [{ "device": "R4", "commands": "router bgp 65000\n neighbor 192.0.2.5\n  no ebgp-multihop\n" }],
  "revert": [{ "device": "R4", "commands": "router bgp 65000\n neighbor 192.0.2.5\n  ebgp-multihop 255\n" }]
}
```

## Scoring Protocol

The scoring **contract** is what makes this a benchmark rather than a file dump.
An agent's answer is graded against `expected_rca` by a **decompositional
semantic fact-coverage** metric:

1. the gold `expected_rca` is decomposed into distinct root-cause **facts**;
2. **recall** = fraction of gold facts the answer covers;
3. **precision** = fraction of the answer's claims supported by the gold;
4. the headline score is the **F1** of mean precision and mean recall, averaged
   over `K` independent judge samples (reference default `K=3`, temperature `0`).

The judge is conditioned on a ground-truth-blind restatement of the question, so
it never sees the fault label directly. Unsupported causal claims cost precision;
missing required root-cause facts cost recall.

The reference implementation is the `rca_eval` semantic-F1 metric used by the
netx-aiops RCA harness; any decompositional semantic recall/precision judge over
`expected_rca` reproduces the contract. Benchmark reports **must** disclose the
judge model, version, and `K`.

### Answer conventions (identifier matching)

Golds are written in the identifiers an agent actually observes on-box:

- devices are IOS-XR routers `R0`–`R7`, each with management IP `100.64.0.10N`
  (e.g. `R4` → `100.64.0.104`). The **root-cause device** is named by its
  management IP with the hostname annotated, e.g. `100.64.0.104 (R4)`;
- **neighbors / peers** are named by their peering address (loopback or link IP),
  as an agent reads them from configuration and protocol state.

## Splits and Leakage Policy

This is an **evaluation-only** benchmark: there is no `train` split, and the
scenarios are intended to be treated as a sealed test set for reporting.

If the dataset is used for prompt optimization, retrieval tuning, symbolic-rule tuning, 
or judge calibration, the scenarios used for tuning **must be reported as a development split**, 
not as sealed held-out performance.
**Do not tune on a scenario and then report its score as zero-shot.**

## Dataset Creation

### Source Data and Provenance

Scenarios are **synthetic / lab-generated** on a live IOS-XR (XRd) testbed run
under containerlab. No production or customer data is included. For each scenario
the `apply` / `revert` blocks are the exact CLI that injects and undoes the fault
on the running lab, so every gold is reproducible against the live network.

### Annotations

Gold answers are **engineer-written** root cause / mechanism / fix statements,
grounded in the injected change and standard protocol behaviour. Golds are
symptom-free (the syslog signature is captured separately in
`expected_symptoms`). Gold `expected_rca` text has been **recalibrated to
agent-observable identifiers** (management-IP device naming; premise clauses
folded into mechanism) so that the fact-coverage metric measures diagnostic
correctness rather than identifier style — see `git log` for the exact,
auditable recalibration diff.

## Known Limitations

- **Single vendor:** IOS-XR only; no cross-vendor coverage.
- **Bounded topology space:** 6 profiles, 8-router labs; limited multi-fault and
  ambiguous cases.
- **Prose-first gold:** the gold is a human-readable `expected_rca` (plus a
  symptom signature). It does **not yet** ship the fuller "gold in three layers"
  (atomic gold-fact table + expected-diagnostic-action table) recommended for
  agentic benchmarks — see Roadmap.
- **Judge dependence:** the semantic-F1 metric depends on a judge model; absolute
  scores are only comparable within a fixed judge / `K` configuration.

## Roadmap

Planned, to strengthen the scoring contract (per gold-eval best practice):

1. an **atomic gold-fact table** per scenario (required / optional / forbidden
   facts with weights and evidence), enabling fact-level F1 and hallucination
   penalties independent of a judge;
2. an **expected-diagnostic-action table** (required / acceptable / forbidden
   tool actions), enabling required-action recall and unsafe-action penalties.

## Versioning

The dataset follows semantic versioning:

- **patch** — typo / metadata fixes, non-semantic cleanup;
- **minor** — added scenarios or backward-compatible fields;
- **major** — changed gold labels, changed scoring semantics, or removed scenarios.

Current release: **v1.0.0**.

## Citation

```bibtex
@dataset{xrd_scenarios_datasets_2026,
  title     = {XRd Scenario Datasets: Autonomous Network RCA Evaluation Golds},
  author    = {Koehler, Timo},
  year      = {2026},
  version   = {1.0.0},
  license   = {CC-BY-4.0},
  url       = {https://github.com/netx-aiops/xrd-scenarios-datasets}
}
```

See also [`CITATION.cff`](CITATION.cff).

## License

- **Data, gold labels, and documentation** are licensed under
  **Creative Commons Attribution 4.0 International (CC-BY-4.0)** —
  `SPDX-License-Identifier: CC-BY-4.0`.
- **Any bundled code / scripts** are licensed under **Apache-2.0** —
  `SPDX-License-Identifier: Apache-2.0`.

You are free to share and adapt the data, including commercially, provided you
give appropriate credit, link the license, and indicate changes. See
[`LICENSE`](LICENSE) for the full notice.

Suggested attribution:

> XRd Scenario Datasets v1.0.0, created by Timo Koehler (netx-aiops), licensed
> under CC-BY-4.0.
