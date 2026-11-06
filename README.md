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

# XRd scenario datasets

Evaluation manifests for controlled XRd fault tests. Each profile/scenario's
`meta.json` contains its question, expected answer/observations and apply/revert
recipe. Keep all golds, targets and recipes on the evaluator side, outside RCA
inputs. This is evaluation data, not model-training material.

Curated by Timo Koehler (netx-aiops). Data/documentation are CC-BY-4.0; bundled
code is Apache-2.0. Preserve attribution, source captures and license files.

## Use and qualify

Clone beside xrd-vlab and use its [evaluation workflow](../xrd-vlab/gui/README.md).
Fault execution requires authorized lab ownership, the matching active profile,
verified baseline and guarded restoration. A score does not establish causal
correctness, protocol completeness or successful network restoration.

Honor release and `deployment_status` separately. The current lab uses R0–R7;
retired R8/R9 cases remain historical and must not execute. Retained labels do not
imply fresh qualification after a topology change. Silent scenarios may have no
syslog trigger; missing logs do not prove no fault.

Keep profile/trajectory families together when assigning evaluation splits.
The CDP profile duplicates the LLDP twin's faults/golds and is not an independent
fault population. Record prior artifact contact; do not tune on held-out golds or
relabel development results as independent evaluation.

## Maintain

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Review
source captures, exact scope, timing and restoration before promoting a scenario.
Changes to gold labels require maintainer sign-off and versioned provenance;
do not revise frozen expectations merely because an agent disagrees.

Use the shared [RCA scorer](../rca-ax/eval/README.md) with recorded model/scorer
versions for comparisons. Keep capture notes and artifacts as qualification
provenance; deployment retirement does not rewrite their original observations.
