# Capture session — r2-pe-static-blackhole-rr-loopback (2026-08-11)

D-F8 witness capture (forwarding-specific RIB/FIB scenario on `ospf-bgp-rr`,
two candidate underlay paths, new occurrence class). Capture-first discipline:
all evidence below was collected live BEFORE any meta.json/gold was authored.

## Fault

On R2 (PE1, 100.64.0.102): `router static / address-family ipv4 unicast /
192.0.2.3/32 Null0` — a static blackhole for the primary RR's (R3) loopback.
Static AD 1 beats OSPF AD 110; CEF installs a null0 (drop) adjacency. BGP
config on every device untouched. Both OSPF underlay arms stay FULL throughout.

Apply/revert channel: net-api `/cli_rw` (XR SSH path, auto `commit;end`) — the
same channel `scenario.py` uses. NOTE: multiline config via
`docker exec … xr_cli` does NOT work (`% got wrong eof code from
parser_server: 3`, nothing committed — see `r2_apply_console.txt`).

## Timeline (UTC, 2026-08-11)

- 10:56:25  baselines captured (R2 RIB `ospf 100` metric 2 via 192.0.0.10/Gi0/0/0/0;
            CEF matched-prefix `source rib (7)` same arm; OSPF FULL to R3 + R6;
            R2 Established to both RRs; R3 Established to all 3 PEs + R7)
- 10:58:32  fault committed (MGBL DB_COMMIT on R2, commit id 1000000003)
- 10:58:45  RIB flipped: `static, distance 1, via Null0`; CEF: `attached, null0 adjacency`
- 11:00:45.499  R3: `%ROUTING-BGP-5-ADJCHANGE : neighbor 192.0.2.6 Down - BGP
                Notification sent, hold time expired`  (T+133s — the TRANSIT victim)
- 11:00:45.506  R6: `neighbor 192.0.2.3 Down - BGP Notification received, hold time expired`
- 11:00:52.737  R3: `neighbor 192.0.2.2 Down - BGP Notification sent, hold time expired` (T+140s)
- 11:00:52.739  R2: `neighbor 192.0.2.3 Down - BGP Notification received, hold time expired`
- ~11:02        faulted-state captures: R2/R3/R6 BGP summaries (R3 shows 192.0.2.2 +
                192.0.2.6 Active, 192.0.2.4 + 192.0.2.7 up); R6 RIB to 192.0.2.3
                HEALTHY (ospf metric 3 via 192.0.0.13 = transit through R2);
                pings 192.0.2.3 source Lo0 from R2 AND R6 = 0% (5/5 lost)
- 11:03:31  revert `no router static` via /cli_rw
- 11:03:32  RIB back to `ospf 100` metric 2; running-config diff vs baseline =
            timestamp/last-change header lines ONLY (config bytes identical)
- ~11:03:36 R2↔R3 and R6↔R3 re-established (R3 summary at 11:08:35 shows
            uptimes 4:59 / 4:03, all 4 sessions Established, prefixes back).
            (recovery_log.txt's "nonestablished=4" is a poller awk bug —
            CRLF line endings made `$NF` non-numeric; the summary file is
            the evidence.)

## The mechanism (why this is a forwarding witness, not an intent fault)

R2's blackhole kills TWO session pairs while only ONE device is at fault:
1. R2↔R3 — R2's own TCP to 192.0.2.3 dies at R2's Null0.
2. R6↔R3 — R6's shortest path to 192.0.2.3 (metric 3) TRANSITS R2
   (192.0.0.13 next hop), so R6's keepalives are swallowed by R2's Null0
   in transit. Neither endpoint of this pair has any fault.
R4↔R3 survives (direct R3–R4 link, never transits R2). All PE↔R7 sessions
survive. OSPF is unaffected (the static is local RIB/FIB state, not
redistributed) — so the underlay keeps offering TWO feasible realizations
toward R3 (direct arm Gi0/0/0/0; long arm via Gi0/0/0/1 → R6 → R7 → R4)
while forwarding on R2 drops the traffic: the exact
RIB/FIB-divergence-from-intent class the `bgp.transport-forwarding-resolution`
block exists to localize.

## Timing consequence for the scenario metadata

Hold-time expiry landed at T+133/140s here (last keepalives ~40–47s before
commit). Worst case = full 180 s holdtime + stagger ⇒
`symptom_capture_grace_seconds: 240`.

## Independent-apply verification (run 2, `make scenario-verify`, 11:09–11:17 UTC)

Exit 0; "MATCH: captured symptoms cover the gold exactly" (timestamp-normalized);
nothing written (non-destructive contract). Report: `scenario_verify_run1.txt`.
Run-2 symptoms: R3 192.0.2.6 Down @11:13:32.112, R3 192.0.2.2 Down @11:13:36.146,
R2 192.0.2.3 Down @11:13:36.147 (~T+215s from the engine apply — slower than
run 1's T+133/140s, consistent with keepalive phase; 240s grace was the right
call). **Variance finding: R6's "192.0.2.3 Down - Notification received" line
did NOT fire within run 2's window** — R6's logged teardown depends on R3's
NOTIFICATION landing on a still-receptive TCP socket at R6 (run 1: processed;
run 2: not, R6's session died silently later — fresh 0:40 uptime seen at
11:17). The R6↔R3 pair's failure is deterministic either way via R3's own
192.0.2.6 line; verification MATCHes either way because R2's and R6's lines
share one timestamp-normalized key. meta.json's summary field documents the
variance; expected_symptoms keeps the richer 4-line run-1 set (never-weaken).

Post-verify health re-checked 11:17 UTC: all R3 sessions Established, R2
`router static` = "No such configuration item(s)", scenario stack empty.

## File inventory

- `r2_baseline_*` — pre-fault: running-config, bgp summary, route/cef 192.0.2.3, ospf neighbors
- `r3_baseline_bgp_summary.txt`
- `r2_watermark_adjchange.txt`, `r3_watermark_adjchange.txt` — syslog watermarks
- `r2_apply_console.txt` — the FAILED xr_cli attempt (kept as evidence), then
  `r2_apply_cli_rw_response.json` — the real apply
- `r2_fault_*` — post-fault route/cef/router-static/bgp summary/ping/logging
- `r3_fault_*`, `r6_fault_*` — victim-side summaries, R6 route/cef (healthy),
  R6 ping (0%), ADJCHANGE lines
- `poller_log.txt` — symptom watch cadence; `NOTES_timing.txt` — apply/revert stamps
- `r2_revert_*` — post-revert route + running-config; `r3_recovery_bgp_summary.txt`,
  `recovery_log.txt` — session re-establishment
