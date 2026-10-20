# Validation, known limitations and release gate

## Validation performed

- Python standard-library unit suite: **45 tests passing** (on the packaged version at initial v3 validation).
- Includes brute-force comparison for fleet optimisation, infeasibility, capacity/spill invariants, deterministic random-seed stress, Haversine geometry, document revision/approval gates, forecasting input requirements, no-leakage rolling holdout properties and external schedule time-zone offsets.
- Headless Chromium checked all nine web pages at desktop and mobile sizes, interactive fleet/carbon/fare controls, synthetic emissions adjustments, technical record filters, monthly demo model, and legacy network/carrier pages.
- `scripts/validate_powerbi.py` verifies PBIP report pointer, model paths, six imported table definitions, 26 DAX measure names, six pages, 24 visuals and their 47 visual field bindings.

## Not validated here

1. **Power BI Desktop rendering or refresh.** Windows Power BI Desktop was not available. TMDL/PBIR source was generated and structurally checked; opening and saving the PBIP in Desktop is required before claiming a working native Power BI report or producing PBIX.
2. **Source authenticity of uploaded files.** Importers cannot independently authenticate a CSV or a licensed schedule.
3. **Full-scale airline economics.** Actual airline demand, yields, costs, fleets, slot access, emissions inventories, protection/settlement rules and published flights were not obtained.
4. **Live operations.** No data ingestion scheduler, authentication service, production datastore, paid schedule feed, deployment SLA, active airline integration or real-time airline optimisation.
5. **Statistical predictive accuracy.** Synthetic Monte Carlo factors aren't empirically fitted and forecast error bands aren't predictive intervals with calibrated coverage.
6. **Engineering sign-off.** Fictional technical records and automated readiness checks do not replace accountable engineering, safety, regulatory or certification sign-off.
7. **Professional authorship.** Initial implementation is AI-assisted; the end user should personally contribute and verify before claiming independent development or proficiency with Power BI/Python.

## How to complete Power BI validation

See [`POWERBI_DESKTOP_CHECKLIST.md`](POWERBI_DESKTOP_CHECKLIST.md) for concrete Desktop checks. If Desktop reports errors, fix the original TMDL/PBIR project and check measured values rather than renaming arbitrary files to `.pbix`.

## What would enable production-grade modelling

- Airline/airport datasets under appropriate licence, including tail-level rotations, cabin seats, paid loads, fares and actual segment costs.
- 24–36+ months of genuine monthly observations for predictive validation; ideally separate holdout periods and known interventions.
- Actual operating timetables, minimum connection rules, code-share agreements, MCT, delay distributions, maintenance and crew controls.
- Environmental calibration per aircraft/engine and operating profile, including uncertainty and non-CO2 policy scope.
- Real documentary evidence mapped to controlled, verified requirements and authorised approval workflows.
- Formal stakeholder sign-off, source validation, calibrated backtesting, operational risk/quality controls and independent model review.
