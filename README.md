# Orbital Risk Authority (ORA)

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

