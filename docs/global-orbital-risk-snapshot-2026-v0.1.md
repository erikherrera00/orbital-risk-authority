# Global Orbital Risk Snapshot – 2026 (v0.1)

> **Orbital Risk Authority (ORA)**  
> **Status:** Prototype snapshot, not for policy use  
> **Date:** [fill in]

---

## 1. Executive Summary

- Overall orbital risk level: **Elevated**
- LEO: High congestion and debris growth pressures.
- MEO: Moderate risk, driven by navigation constellations.
- GEO: Moderate risk with slot crowding in key longitudes.

This snapshot is based on the prototype **Orbital Risk Index (ORI)** framework (v0.1) and uses simplified, illustrative data for concept validation.

---

## 2. ORI Framework (Brief)

Reference: `docs/ori-methodology-v0.1.md`

- ORI scores: 0–100, higher = higher risk.
- Levels: Orbit band, operator, satellite.
- Inputs: object density, collision indicators, behavior, disposal, transparency.

This snapshot focuses on **orbit band scores** only.

---

## 3. Orbit Band Scores (Illustrative v0.1)

| Orbit Band | ORI Score (0–100) | Qualitative Level | Key Drivers |
|-----------:|-------------------|-------------------|-------------|
| LEO        | 72.5              | High              | High object density, debris, mega-constellations. |
| MEO        | 45.2              | Moderate          | Navigation fleets, moderate debris environment.   |
| GEO        | 38.7              | Moderate          | Slot crowding, relatively lower debris density.   |

These scores mirror the prototype API response from `/ori/global-summary`.

In this prototype, each orbit band is also assigned an illustrative **object_count** and **Population Pressure Index (PPI)**. The PPI is a 0–100 scale intended to reflect how crowded a given region is relative to a notional reference level. Future versions will ground these values in actual cataloged object populations and their growth trends.

---

## 4. Qualitative Observations

### 4.1 Low Earth Orbit (LEO)

- Rapid growth in active satellites and constellations.
- Increasing conjunction counts and maneuver demands.
- Long-term sustainability heavily dependent on responsible deployment and deorbit practices.

### 4.2 Medium Earth Orbit (MEO)

- Dominated by navigation constellations (e.g., GNSS).
- Fewer objects than LEO, but orbits are mission-critical and long-lived.
- Disposal and redundancy strategies are central to risk containment.

### 4.3 Geostationary Orbit (GEO)

- Crowding in commercially valuable slots.
- Lower debris count than LEO but high economic value per asset.
- Graveyard orbit disposal and station-keeping behavior strongly influence long-term stability.

---

## 5. Limitations of This Snapshot

- Uses mocked, simplified scores aligned with ORI v0.1 API prototypes.
- Based on conceptual density and trend assumptions rather than full catalog analysis.
- Intended as a structural demonstration only.

---

## 6. Roadmap

Future snapshots will aim to:

1. Integrate actual catalog-based density metrics and conjunction statistics.
2. Add regional GEO slot analysis and sub-bands within LEO.
3. Introduce operator-level and satellite-level score examples.
4. Provide machine-readable outputs via a public ORA API.

---

## 7. Disclaimer

This document is part of an early-stage prototype. It is not intended as a regulatory tool or as the sole basis for insurance, licensing, or operational decision-making. All scores and classifications are subject to change as methodology and data sources are refined.

