# Global Orbital Risk Snapshot – 2026 (v0.3)

> **Orbital Risk Authority (ORA)**  
> **Prototype Version:** ORA v0.3  
> **Status:** Prototype snapshot, not for policy use  
> **Date:** [fill in]

---

## 1. Executive Summary

- Overall orbital risk level: **Elevated**
- LEO: High congestion and growth pressure, with uneven distribution by altitude.
- MEO: Moderate congestion, dominated by navigation fleets.
- GEO: Moderate congestion, with crowding in key commercial longitudes.

This snapshot uses the ORI prototype (ORI-0.3) and combines:

- a band-level view with Population Pressure Index (PPI),
- an operator archetype view with Fleet Pressure Index (OFPI),
- and a sub-band view for LEO congestion.

All values are illustrative but directionally aligned with known trends.

---

## 2. Band-Level ORI and Population Pressure (PPI)

Band-level scores and PPI values:

| Orbit Band | ORI Score | Level    | Objects (est.) | PPI (0–100) | Notes |
|-----------:|----------:|----------|----------------|------------:|-------|
| LEO        | 72.5      | High     | ~36,000        | 100.0       | Dense operational satellite and debris environment. |
| MEO        | 45.2      | Moderate | ~4,000         | ~11.1       | Navigation constellations dominate; fewer total objects than LEO. |
| GEO        | 38.7      | Moderate | ~3,000         | ~8.3        | Crowding in key slots, but lower total object count than LEO. |

PPI is normalized such that the most crowded band (currently LEO) receives a value of 100, with other bands scaled proportionally.

---

## 3. LEO Sub-Band Congestion (ZPI)

To avoid treating LEO as a homogeneous shell, ORA v0.3 introduces illustrative altitude zones:

| Zone  | Altitude Range | Objects (est.) | Zone Pressure Index (0–100) | Notes |
|------:|----------------|----------------|-----------------------------:|-------|
| LEO-1 | 300–500 km     | ~14,000        | ~87.5                        | Significant constellation presence and active deployments. |
| LEO-2 | 500–800 km     | ~16,000        | 100.0                        | Highest object concentration within LEO. |
| LEO-3 | 800–1200 km    | ~6,000         | ~37.5                        | Fewer objects but longer orbital persistence due to slower decay. |

These values are illustrative and intended to show how congestion can vary by altitude band.

---

## 4. Operator Fleet Pressure (OFPI – Archetypes)

ORA v0.3 uses archetypal operators to illustrate the concept of fleet-driven systemic pressure:

| Operator Archetype                  | Orbit | Fleet Size (est.) | Fleet Pressure (0–100) | Notes |
|-------------------------------------|:-----:|-------------------:|------------------------:|-------|
| LEO Broadband Constellation A       | LEO   | 5,500              | 100.0                   | Large-scale LEO broadband constellation with aggressive deployment pace. |
| LEO Imaging & IoT Constellation B   | LEO   | 900                | ~16.4                   | Mixed imaging / IoT fleet with moderate scale. |
| Global Navigation System C          | MEO   | 180                | ~3.3                    | Core navigation constellation in MEO. |
| GEO Comms Operator D                | GEO   | 80                 | ~1.5                    | GEO communications operator with long-lived assets. |

These profiles do not represent specific real-world entities but illustrate how ORA can surface relative system impact from fleet dominance.

---

## 5. Limitations

- Uses static, approximate counts and archetypes rather than live SSA data.
- Does not yet incorporate detailed collision risk models or maneuver statistics.
- Operator views are illustrative and not ratings of real organizations.

---

## 6. Roadmap Link

See `docs/ROADMAP.md` for planned evolution toward more granular bands, real data integration, and expanded responsibility indicators.

