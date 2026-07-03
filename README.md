# XRd Scenario Datasets

Evaluation golds for benchmarking **autonomous network root-cause-analysis (RCA)
agents** against a **live IOS-XR (XRd) network**.

Each scenario injects a single, real fault — a configuration change applied to a
running multi-router lab — and asks an agent to identify the root cause from live
telemetry alone. The agent is **ground-truth-blind**: it sees only the network and
a generic question, never the answer. Its RCA is then scored against an
engineer-written gold.

## Contents

60 scenarios across 6 IOS-XR network profiles (topologies), 10 each:

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
inert** change (no operational impact) to test an agent's resistance to false
positives.

## Layout

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
| `apply`, `revert` | the exact IOS-XR CLI to inject / undo the fault on the live lab |
| `mode`, `is_silent` | delivery mode (`live`); whether the fault is log-silent |

## Scoring

The agent's answer is scored against `expected_rca` by a **semantic fact-coverage
metric**: the gold is decomposed into distinct root-cause facts, then

- **recall** = fraction of gold facts the answer covers,
- **precision** = fraction of the answer's claims supported by the gold.

## Conventions

- Devices are IOS-XR routers `R0`–`R7`; each has management IP `100.64.0.10N`
  (e.g. `R4` → `100.64.0.104`). Golds name the **root-cause device by its
  management IP** with the hostname annotated — e.g. `100.64.0.104 (R4)` — to
  match the identifier an agent observes on-box.
- **Neighbors / peers** are named by their peering address (loopback or link IP),
  as an agent reads them from configuration and protocol state.

---

Internal evaluation dataset. © 2024–2026 Timo Koehler. All rights reserved.
