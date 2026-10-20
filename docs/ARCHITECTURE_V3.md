# AeroLens 3 — System architecture

## Evidence-class boundary

AeroLens has three disjoint data classes: `OBSERVED_CAA`, `USER_SUPPLIED_SOURCE_UNVERIFIED`, and `SYNTHETIC_SCENARIO`. Every chart displays or describes its input class. There is no join that turns CAA aggregate passenger counts into actual airline demand/yield or a fact about a given operator.

- `scripts/build_data.py` reads manually curated CAA 2024/2025 airport pairs and emits observed JS + calculated long table.
- `scripts/build_advanced.py` emits 154 fictional dated flight legs after IANA time-zone normalisation; no protected connections are inferred.
- `scripts/build_enterprise.py` creates 9 illustrative route planning scenarios, 40 fictional technical records, a synthetic monthly time series, and Power BI import datasets.
- `scripts/build_powerbi.py` compiles a native editable **PBIP source project** with TMDL semantic tables and PBIR visuals. Power BI Desktop execution is a separate validation task.

## Exact fleet portfolio allocation

`aerolens/portfolio.py` solves a discrete multiple-choice knapsack. Each route has a bounded integer weekly frequency `n`. It consumes `block_hours_i × n` from a fleet-hours budget and `emissions_t_i × n` from a modelled emissions budget. Gross weekly carried passengers are `min(weekly_demand_i, seats_i × n)`. Contribution under assumptions is:

```
contribution_i(n) = carried_i(n) × (fare_i − variable_cost_i) − n × departure_cost_i
```

Dynamic programming keeps the strongest score per exact `(used_hours,used_emissions_t)` state. It is exact **for discrete resource units and these separable assumptions**, not globally optimum for a real airline. There are no aircraft rotation, crew, contract or actual slot constraints. Cross-checks include a brute-force oracle on small configurations, capacity guards, deterministic scenarios and infeasible minimum frequency conditions.

## Network and reliability

The original date-less flight graph was replaced in v2 by a dated IANA-aware graph. AeroLens 3 anonymises its sample carrier codes and adds `aerolens/operations.py` for externally supplied flight schedules. The importer rejects bad offsets, impossible durations, duplicate flight IDs and missing provenance. All genuine schedules remain **user-provided and source-unverified** until independently checked.

An optional `connection_reliability()` engine draws fictional shared disruptions, per-leg delays and cancellations; results are reproducible Monte Carlo what-if rates. No fitted punctuality statistics, real missed connection rates or permitted codeshare arrangements are included. It does not implement actual reaccommodation or crew/aircraft recovery.

## Emissions

`aerolens/sustainability.py` computes great-circle geometry with the haversine function and hypothetical fuel and CO2 usage:

```
fuel_kg = assumed_block_hours × assumed_fuel_kg_per_block_hour × flight_count
CO2_kg = fuel_kg × assumed_kgCO2_per_kg_fuel
intensity_kgCO2_per_pax_km = CO2_kg / assumed_passenger_km
```

Inputs are exposed so a reviewer can inspect sensitivity. These are NOT measured emissions, emissions-offset claims, airline climate reporting, aircraft performance certification or lifecycle emissions analysis.

## Technical records and quality gates

`aerolens/assurance.py` models evidence IDs, requirements, document revisions, approved revisions, approval flags, dates and criticality. A record is ready only if its current version is approved and the approval flag is true. Late blocked records are escalated. **Every bundled record is fictional; the release gate is documentation readiness, not authority certification.**

## Forecast laboratory

The Python and browser implementations require at least **30 consecutive months**; the current CAA source supplies two annual observations and cannot feed it. For each holdout month starting at month 25, the models use only earlier observations. Seasonal naive predicts `y[t-12]`; the seasonal-level variant adjusts last year's month by the historical difference of successive 12-month totals divided by 12. Lower MAE wins. The next six months are modelled with an illustrative absolute backtest-error band. This is neither a calibrated causal forecast nor a probabilistic confidence interval.

## Browser architecture

- `index.html` and `assets/style.css` are the accessible responsive dashboard shell.
- `assets/data.js` is generated observed market data.
- `assets/advanced_data.js` is generated fictional dated timetable data.
- `assets/enterprise_data.js` is generated scenario + QA data.
- `assets/app.js`, `assets/advanced.js` and `assets/enterprise.js` implement the nine offline workspaces.
- `assets/enterprise.css` adds v3 controls.

The bundled standalone HTML in the release embeds the same files without any backend. Runtime never transmits uploaded CSVs to an external service.

## Power BI architecture

`powerbi/AeroLensIntelligence/` is a documented project-format source, not a PBIX executable. Six imported tables, 26 model measures, six report pages and 24 native built-in visuals are version-controlled. It uses Power Query embedded `#table(...)` expressions so it has no broken absolute file paths. All six tables are **distinct analytics exercises**, intentionally without invented relational joins between observed facts and fictional operational data.

Offline structural lint verifies every visual's Entity/Property binding resolves to a source table/measure. **Power BI Desktop and Fabric are not available for execution here**, so create a `.pbix` only after opening, refreshing, inspecting and saving in Power BI Desktop on Windows.
