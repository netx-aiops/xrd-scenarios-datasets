# r3-r2-passive-interface — raw lab capture (2026-07-13, pre-gold)

Real-apply evidence for the D4 passive-interface scenario (V2B expansion 9).
Captured per the reviewer-authorized sequence BEFORE any gold was written
(baseline → fault → revert-test → restore). Lab: xrd-vlab
`ospf-multi-area-bgp` profile, XRd 26.1.1, all timestamps UTC (XR clocks).

## Timeline

- 15:20:49 baseline captured (R2 + R3; adjacency FULL, R3=DR R2=BDR).
- 15:21:47 fault applied on R3 via net-api cli_rw (user AI_AGENT_RW):
  `router ospf 100 / area 0 / interface GigabitEthernet0/0/0/0 /
  passive enable` — accepted verbatim, one commit.
- 15:21:47.188 **R3 (the passive end) logs IMMEDIATELY**:
  `%ROUTING-OSPF-5-ADJCHG … Nbr 192.0.2.2 … from FULL to DOWN,
  Neighbor Down: interface down or detached` — the "silent passive end"
  prediction is REFUTED; the passive end logs FIRST, at config time.
- 15:22:20.043 R2 logs `… Nbr 192.0.2.3 … from FULL to DOWN,
  Neighbor Down: dead timer expired` (~33 s later).
- NO `%ROUTING-OSPF-4-ERRRCV` lines on either end (the discriminator vs
  the ospf-area-mismatch scenario). NO BGP flap (OSPF rerouted via R3
  Gi0/0/0/1; loopback reachability held).
- 15:23:43 revert spelling test: `passive disable` ACCEPTED — leaves an
  EXPLICIT `passive disable` line in config (an explicit-false config
  token, not a clean restore); adjacency reformed FULL within ~14 s
  (R2 took DR on re-election — expected after adjacency reset).
- 15:24 clean removal: `no passive` ACCEPTED — running config restored
  BYTE-IDENTICAL to baseline (diff-verified); adjacency FULL.

## Evidence-source findings (the command-selection gate)

`show ospf interface` (device-wide detail form) satisfies ALL SIX
reviewer conditions in one output:

1. process explicit per interface (`Process ID 100`);
2. routing context inherited unambiguously (unscoped = default VRF;
   VRF-scoped variants are a distinct `show ospf vrf …` command);
3. enumerates every OSPF-enabled interface;
4. area explicit per interface (`… Area 0 …`);
5. effective passive state EXPLICIT IN BOTH POLARITIES —
   passive: `No Hellos (Passive interface)`;
   non-passive: `Hello due in <t>`;
6. explicit false is licensed from the POSITIVE `Hello due` marker,
   never from syntax absence.

Loopback0 renders `Network Type LOOPBACK … treated as a stub Host`
with NEITHER hello marker — loopbacks carry no passive polarity in the
operational output, coherent with their structural out-of-scope status.

`show running-config router ospf` is the secondary source: complete
hierarchical stanza; explicit `passive enable` AND (post-disable-test)
explicit `passive disable` tokens exist; false-from-absence would
require complete-stanza + inheritance reasoning. `show ospf interface
brief` does NOT expose passive at all (Gi0/0/0/0 still showed `DR 0/0`
while passive) — brief is insufficient for this family.

## Scenario-facing conclusions (gold NOT yet written)

- apply: `configure terminal / router ospf 100 / area 0 /
  interface GigabitEthernet0/0/0/0 / passive enable`
- revert: `… / no passive` (byte-identical restore; `passive disable`
  is valid CLI but leaves an explicit override residue).
- expected symptoms: BILATERAL ADJCHG with DISTINCT reasons and ~30-40 s
  stagger (passive end first, `interface down or detached`; far end
  later, `dead timer expired`); no ERRRCV; no BGP flap.

## Files

- baseline_R2.txt / baseline_R3.txt — healthy state + both candidate
  command outputs + Loopback0 baseline passive config.
- fault_R2.txt / fault_R3.txt — fault state: logs, neighbor state,
  candidate outputs on R3 showing `No Hellos (Passive interface)` +
  the `passive enable` config line.
- restored_R3.txt — post-`no passive`: config diff-identical to
  baseline, adjacency FULL, device-wide `show ospf interface` output
  (incl. the Loopback0 rendering).
