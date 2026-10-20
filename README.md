# AeroLens 3 — Aerospace & Aviation Decision Intelligence

**Aviation market intelligence · network analytics · operations research · engineering assurance · Power BI**

AeroLens is an interactive decision-intelligence system for analysing aviation markets, exploring operational scenarios, and connecting quantitative evidence to engineering and commercial decisions. It combines a browser-based analytical workbench with reproducible Python workflows, SQL analysis, and an editable Power BI project.

![AeroLens fleet allocation workspace](media/v3_fleet_portfolio.png)

## Capabilities

| Module | Analytical capability |
|---|---|
| **Market intelligence** | Compare annual passenger demand, growth and airport-pair trends across 28 selected London Heathrow–US markets. |
| **Network connectivity** | Search dated flight graphs, resolve time zones, enforce connection windows and rank alternative itineraries. |
| **Commercial analysis** | Explore capacity-constrained demand, break-even load factors, cost assumptions and Monte Carlo sensitivities. |
| **Carrier data workbench** | Validate authorised BTS T-100 imports and calculate carrier/route capacity and load factors. |
| **Fleet portfolio optimisation** | Allocate constrained weekly flying hours using an exact integer optimisation model. |
| **Sustainability** | Compare route geometry, fuel-use assumptions, modelled emissions and passenger intensity. |
| **Engineering assurance** | Track document revisions, approvals, evidence completeness and corrective actions. |
| **Forecasting** | Import monthly demand observations, backtest seasonal baselines and generate scenario forecasts. |
| **Data integrity** | Inspect data lineage, checksums, validations and export-ready analytical datasets. |

## Getting started

### Interactive web application

Open [`index.html`](index.html) in Chrome or Edge. The interactive application runs locally without a backend service or API credentials.

For a portable release, the separate standalone HTML distribution packages the application into a single file.

### Python analytics

**Requirements:** Python 3.11+.

```bash
python scripts/build_data.py
python scripts/build_advanced.py
python scripts/build_enterprise.py
python scripts/build_powerbi.py
python scripts/validate_powerbi.py
python -m unittest discover -s tests -v
```

The core Python workflows use the standard library. Generated datasets and semantic-model artefacts are built through reproducible scripts.

### Editable Power BI project

Open [`AeroLensIntelligence.pbip`](powerbi/AeroLensIntelligence/AeroLensIntelligence.pbip) in Power BI Desktop on Windows.

The source-controlled Power BI implementation includes:

- **6 semantic-model tables**
- **26 DAX measures**
- **6 report pages**
- **24 native visual definitions**
- Power Query M, TMDL semantic-model definitions and PBIR report definitions

The PBIP is an editable source project. Automated checks cover its structure, model references and visual bindings; open it in Power BI Desktop to refresh and verify the rendered report. See the [Power BI Desktop checklist](docs/POWERBI_DESKTOP_CHECKLIST.md).

## Architecture

```text
Public aviation data / authorised external datasets
                    │
                    ▼
       Python ingestion + validation
                    │
           Structured data outputs
                    │
         ┌──────────┴───────────┐
         ▼                      ▼
  Browser analytics       Power BI project
  & scenario engines      Power Query + DAX
         │                      │
         └──────────┬───────────┘
                    ▼
      Reports, exports and decision analysis
```

The implementation separates source-data processing from network algorithms, optimisation, forecasting, finance scenarios and the presentation layer.

Key implementation areas:

- **Temporal network modelling:** date-aware flight schedules, UTC chronology and transfer constraints.
- **Operations research:** integer fleet allocation under weekly resource and emissions constraints.
- **Scenario analytics:** capacity limits, break-even calculations and reproducible Monte Carlo stress testing.
- **Evidence workflows:** revision status, approvals, document completeness and action tracking.
- **Time series:** consecutive-month checks and rolling forecast evaluation.
- **Reporting:** offline browser UI and a version-controlled Power BI semantic model.

## Data and analytical provenance

AeroLens keeps observed datasets and model-generated scenarios separate.

| Dataset / subsystem | Data basis |
|---|---|
| 28 selected Heathrow–US airport markets | UK Civil Aviation Authority published 2024/2025 annual passenger totals across **all carriers** |
| Network itineraries | Dated **synthetic flight schedules**; externally sourced schedules can be imported |
| Fares, costs, market share and route contribution | **Scenario assumptions**, not airline financial disclosures |
| Fleet utilisation and fuel/CO₂ metrics | **Illustrative operational inputs** |
| Engineering document register | **Synthetic technical records** |
| Monthly forecasting | User-provided monthly history, or a separately labelled synthetic demonstration |
| Carrier seat capacity | User-provided authentic BTS T-100 extract, when available |

**Primary public source:** [UK Civil Aviation Authority — Annual airport statistics 2025, Table 12.1](https://www.caa.co.uk/data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-2025/annual-2025/).

The CAA passenger figures describe airport-pair market activity; they are not carrier-specific revenue, profitability or passenger counts. Every scenario engine works with explicitly parameterised assumptions.

### Optional operational data imports

**BTS T-100 segment records**

```bash
python scripts/ingest_bts.py ./local_source/T100_international.csv --source-note "Original source URL and extraction date"
```

**Dated flight schedules**

```bash
python scripts/import_operations.py ./local_source/schedule.csv --source-note "Authorised schedule source and extraction date"
```

Schedule CSV columns: `flight_id,carrier,origin,destination,departure_local,arrival_local`, with numerical UTC offsets in the local timestamps.

The importers validate schema, types, chronology and specified consistency rules. Only supply datasets that are authorised for use and redistribution.

## Quality engineering

- **45 Python unit tests** covering ingestion, schedule logic, operations research, scenario calculations, evidence rules and forecasting.
- Cross-checked selected browser calculations against Python outputs.
- Browser interactions exercised on desktop and mobile layouts.
- GitHub Actions automates dataset generation, unit tests and Power BI structural validation.

Run the full test suite with:

```bash
python -m unittest discover -s tests -v
```

## Documentation

- [System architecture](docs/ARCHITECTURE_V3.md)
- [Source register](docs/SOURCE_REGISTER.md)
- [Power BI Desktop checklist](docs/POWERBI_DESKTOP_CHECKLIST.md)
- [Validation methodology](docs/VALIDATION_AND_LIMITS.md)

## Licence

Application code is distributed under the included MIT licence. Third-party datasets retain their original licences, attribution requirements and usage conditions. Organisational names identify public data sources and do not imply endorsement.
