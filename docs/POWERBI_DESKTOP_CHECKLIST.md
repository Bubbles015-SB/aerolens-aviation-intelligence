# Power BI Desktop acceptance checklist (Windows)

The source project is stored at:

`powerbi/AeroLensIntelligence/AeroLensIntelligence.pbip`

**This is a complete editable PBIP/TMDL/PBIR source scaffold with six data tables and report pages. It is not a PBIX file.** Microsoft Power BI Desktop is needed to finish testing and create a PBIX.

## Steps

1. Install the current [Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop) on Windows.
2. Extract the entire AeroLens folder locally. Do not open the `.pbip` inside a compressed ZIP.
3. Under Power BI Desktop → File → Options and settings → Options, enable project and enhanced report/TMDL features if your installed build requires them.
4. Open `powerbi/AeroLensIntelligence/AeroLensIntelligence.pbip`.
5. Check that the semantic model contains **MarketObservations, FleetScenarios, EvidenceRegister, NetworkScenarios, EmissionsScenarios, ForecastDemo**.
6. Refresh model data. The six imported queries use embedded `#table` expressions and therefore should require no local file-path parameter or network authentication.
7. Confirm all six pages load. Expected KPI measurements can be independently compared against the generated `data/bi/*.csv` and `data/scenarios/enterprise_summary.json`.
8. In Model view, confirm 26 explicit DAX measures. Verify at least 2025 Market Movements, Market YoY Growth %, Readiness %, Synthetic Flight Legs and Scenario Weekly CO2 Tonnes.
9. Confirm the six pages contain **24 native visuals in total**. If a visual field binding fails, fix the JSON and re-open. Do not report it as tested until errors are resolved.
10. Save a local `.pbix` copy using File → Save As → Power BI Desktop (.pbix). Capture a screenshot of each functioning page and record your Power BI Desktop version.

## How to refresh with future real data

The initial PBIP intentionally embeds tiny data tables for portability. In Power Query, replace the `Source = #table(...)` expression for an individual table with a suitably typed CSV/Web/SQL source **only after validating its provenance**. Keep `classification` on every table and do not mix source categories. Rebuild the Power BI model/visuals after renaming columns.

Real cost, punctuality and route performance can't be populated by simply replacing a file path unless those variables are actually present in the source.

## Important statement for interviews

Until the desktop checks are complete, say: *“I have a version-controlled, AI-assisted Power BI project in PBIP format with a TMDL model and PBIR report definitions. The structural references pass automated checks, and I'm working through Desktop verification.”*

Never say *“I built and verified a production Power BI system for an airline”* or claim an exported `.pbix` exists before it does.
