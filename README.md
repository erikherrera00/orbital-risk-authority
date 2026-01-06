# Orbital Risk Authority (ORA)

> **Current prototype:** ORA v0.3 – includes band-level Population Pressure Index (PPI),
> archetypal Operator Fleet Pressure Index (OFPI), and LEO sub-band congestion.

**Orbital Risk Authority (ORA)** is an independent initiative focused on measuring orbital risk, debris accountability, and space safety for governments, insurers, and satellite operators.

The core metric is the **Orbital Risk Index (ORI)** – a structured scoring framework for:

- Global / orbit-band risk (e.g., LEO, MEO, GEO)
- Operator-level behavior and responsibility
- Satellite-level risk and disposal readiness

This repository currently contains:

- `backend/` – FastAPI-based prototype ORA API
  - `/health` – service health check
  - `/ori/global-summary` – mocked global ORI summary (LEO, MEO, GEO)
- `docs/`
  - `ori-methodology-v0.1.md` – ORI scoring framework (prototype)
  - `global-orbital-risk-snapshot-2026-v0.1.md` – illustrative global snapshot
- `index.html` – public-facing prototype site (served via GitHub Pages)

> **Status:** Early prototype (v0.1). All scores are illustrative only and not for policy or operational decision-making.

## Live resources

- Public site: `https://erikherrera00.github.io/orbital-risk-authority/`
- Prototype API: `<your Render URL here>`

## Roadmap (high level)

- Integrate real catalog-based orbital object and debris data
- Add operator-level and satellite-level ORI endpoints
- Publish a more detailed annual global orbital risk report
- Provide machine-readable outputs and dashboards for regulators, insurers, and operators

What ORA is

- A public prototype that publishes framework-driven orbital risk indicators.

- Uses snapshot-derived population counts (CelesTrak active catalog) to compute pressure indices.

- Designed for comparability across orbit regimes and operators.

What ORA is not

- Not a conjunction prediction service.

- Not a guarantee of safety, collision likelihood, or regulatory compliance.

- Not an authoritative government registry.

- Not a tool for enforcement; it’s a measurement & reporting layer.

Data & methodology notes

- Snapshot-based; may lag real-time conditions.

- Definitions (e.g., LEO/MEO/GEO) use standard thresholds; see /docs and methodology files.
