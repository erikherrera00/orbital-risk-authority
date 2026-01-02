# Orbital Risk Index (ORI) – Methodology v0.1

> **Status:** Prototype – internal use and early review only  
> **Maintained by:** Orbital Risk Authority (ORA)  
> **Purpose:** Provide a transparent, explainable framework for quantifying orbital risk at multiple levels (global, orbit band, operator, and satellite).

---

## 1. Objectives

The Orbital Risk Index (ORI) is designed to:

1. Quantify the relative level of orbital risk in different regions of Earth orbit.
2. Attribute risk to behavior and design choices by satellite operators.
3. Provide a structured basis for:
   - regulatory decision-making,
   - insurance pricing,
   - and long-term orbital sustainability assessments.

ORI is **not** a physics simulation engine. It is a **scoring framework** that integrates existing physical models, catalogs, and behavioral data into interpretable metrics.

## LEO Sub-Band Congestion (v0.3)

To avoid treating Low Earth Orbit as a single homogeneous environment, ORA v0.3
introduces a sub-band view. LEO is divided into illustrative altitude zones
(e.g., 300–500 km, 500–800 km, 800–1200 km), each assigned:

- an estimated object population
- a Zone Pressure Index (ZPI), normalized 0–100
- qualitative interpretation context

This allows ORA to highlight:

- clustering effects
- how congestion differs by altitude
- where persistence risk increases due to slower decay

Values remain illustrative in this prototype, but reflect real-world distribution
patterns where mid-LEO regions carry the highest density while higher LEO altitudes
retain objects longer.

Future versions will refine these values using structured SSA datasets.

---

## 2. Scope and Levels of the Index

ORI provides scores at three primary levels:

1. **Global / Orbit Regime Level**
   - LEO, MEO, GEO, and selected sub-bands.
   - Outputs: overall risk score per band, trend indicators, “hot zones”.

2. **Operator Level**
   - Aggregated behavior of a company/organization operating one or more satellites.
   - Outputs: Operator Risk Grade (A–F), behavior profile, contribution to debris risk.

3. **Satellite Level**
   - Individual spacecraft.
   - Outputs: Satellite Risk Score (0–100), expected contribution to collision risk and debris.

Each level uses overlapping but distinct inputs and weightings.

## Operator Fleet Pressure Index (OFPI)

In addition to orbit-band level indicators, ORA introduces an operator-level view
through the **Operator Fleet Pressure Index (OFPI)**.

OFPI is a 0–100 scale used in v0.1 to represent relative system impact based primarily
on fleet dominance — i.e., how large an operator’s active satellite presence is compared
to other major operators in similar regimes.

In this prototype, OFPI is illustrated using notional operator archetypes (e.g., a large
LEO broadband constellation, a regional imaging / IoT constellation, a MEO navigation
system, and a GEO communications operator) with approximate fleet sizes. The goal is to
demonstrate how relative fleet dominance can be surfaced, without assigning ratings to
specific real-world entities at this stage.

This allows ORA to evolve toward an accountability-aware framework without prematurely
assigning policy-driven judgment values.

---

## 3. Core Inputs (Conceptual v0.1)

In v0.1, ORI is defined around the following conceptual input categories:

1. **Physical Environment**
   - Object density in the region (satellites + tracked debris)
   - Relative velocities and crossing orbits
   - Historical collision and conjunction statistics

2. **Design and Maneuverability**
   - Propulsion availability and Δv margin
   - Attitude/orbit control capability
   - Redundancy and fault-tolerance relevant to maneuver capability

3. **Operational Behavior**
   - Responsiveness to conjunction warnings
   - Frequency and quality of collision-avoidance maneuvers
   - Adherence to published best practices and guidelines

4. **End-of-Life and Disposal**
   - Presence and credibility of a deorbit or graveyard orbit plan
   - Execution of disposal actions on schedule
   - Residual lifetime in congested orbital regions

5. **Transparency and Compliance**
   - Public availability of key mission parameters
   - Participation in data-sharing frameworks
   - Alignment with recognized standards and guidelines (e.g., 25-year rule, etc.)

In v0.1, many of these parameters are approximated or represented with coarse categories; over time they are intended to be refined with more granular and validated data sources.

---

## 4. Scoring Structure (High-Level)

Each ORI score is normalized to a 0–100 scale, where higher values represent **higher risk**.

### 4.1 Orbit Band Risk Score (Example Structure)

For a given band (e.g., LEO):

- **Debris and Object Density (DOD):** 35%
- **Collision Probability Indicators (CPI):** 30%
- **Growth & Trend (GRT):** 20%
- **Mitigation & Governance (MAG):** 15%

`ORI_band = 0.35*DOD + 0.30*CPI + 0.20*GRT + 0.15*MAG`

The exact formulas and normalization functions will be defined in later versions as data sources are fully specified.

### Population Pressure Index (PPI)

For v0.2, the Orbital Risk Index introduces a **Population Pressure Index (PPI)** as a
supporting indicator at the orbit-band level (LEO, MEO, GEO).

PPI represents how crowded an orbital regime is relative to other regimes, using a
0–100 scale. A value of 100 corresponds to the most populated band, with other bands
scaled proportionally.

For the prototype, PPI is based on approximate cataloged object populations drawn
from widely referenced space surveillance reporting:

- LEO: ~36,000 tracked objects
- MEO: ~4,000 tracked objects
- GEO: ~3,000 tracked objects

These values are intentionally approximate and are designed to communicate *relative*
risk and congestion rather than precise physics-driven collision probability. Future
versions will replace these static estimates with live or periodically refreshed data feeds.


### 4.2 Operator Risk Score (Example Structure)

For a given operator:

- **Fleet Exposure (FEX):** 30%
- **Behavior & Maneuvering (BHM):** 30%
- **End-of-Life Performance (EOL):** 25%
- **Transparency & Compliance (TRC):** 15%

Score is calculated, then mapped to a grade (A–F) for interpretability.

### 4.3 Satellite Risk Score (Example Structure)

For a given satellite:

- **Orbital Context (ORC):** 30%
- **Maneuverability (MAN):** 30%
- **Technical Health & Redundancy (THR):** 20%
- **Disposal Readiness (DSR):** 20%

Intermediate values are normalized and combined into a 0–100 score.

---

## 5. Data Sources (Prototype Phase)

In the prototype phase, ORI will rely on:

- Public satellite and debris catalogs (e.g., TLE-based)
- Publicly available datasets and literature from space agencies and research institutions
- Limited operator self-reported data where available

These inputs will initially be used to generate **illustrative** scores to validate the framework and visualization approach. No ORI v0.1 scores should be treated as definitive or used for policy decisions without explicit qualification.

## 5.5 Planned Data Inputs (v0.2+)

While v0.1 uses illustrative data, future ORI versions intend to incorporate:

- Public catalog sources (e.g., CelesTrak)
- Conjunction and space situational awareness datasets (where available)
- Launch cadence and fleet growth statistics
- Reported disposal performance vs policy expectations
- Public filings and transparency statements

Initial implementations may focus on high-level aggregate indicators rather than precise physics-based collision probabilities, with fidelity increasing over time.

---

## 6. Limitations and Roadmap

### 6.1 Known Limitations (v0.1)

- Scores are based on incomplete and sometimes noisy public data.
- Key behavioral metrics (e.g., conjunction response quality) may not be fully observable.
- End-of-life compliance may be approximated from limited reporting.

### 6.2 Roadmap Goals

Future versions are expected to:

1. Integrate higher-fidelity physical models and conjunction analysis tools.
2. Incorporate additional datasets (including commercial and governmental partnerships).
3. Provide more granular regional and operator segmentation.
4. Offer machine-readable outputs (API) for regulators, insurers, and operators.

---

## 7. Disclaimer

ORI v0.1 is an **experimental framework**. It is intended for prototyping, discussion, and technical exploration. It does not represent a finalized regulatory instrument, and ORA does not assume liability for decisions made solely on the basis of prototype scores.


