# Power BI implementation kit — AeroLens 2

This repository includes a **real working HTML/JavaScript dashboard** and source code for reproducing the observed route analysis in Power BI Desktop. There is **no generated `.pbix`** or validated `.pbip` file, because Power BI Desktop is a separate Windows application and has not been used to validate such an artifact in this build environment.

## Quick setup

1. Open Microsoft Power BI Desktop → **Home → Get Data → Text/CSV**, choose `data/derived/route_summary.csv`.
2. In Power Query, set `code`, `city` and `region` to Text; `y2024`, `y2025`, `delta` to Whole Number; `growth_pct` to Decimal Number. Name the query **Routes**.
3. Alternatively paste `bi/route_analysis.m` into Power Query Advanced Editor. **Replace the placeholder absolute path** inside that query with the location where you extracted the repository.
4. Paste individual measures from `bi/measures.dax` into Modeling → New Measure.
5. Use three report pages: Market Monitor (route growth and weighted totals), Route Explorer (slicers and rank), Hypothetical Sensitivity (What-if parameter assumptions).

## Recommended layout

**Market Monitor:** Cards for `2025 Passengers`, `Weighted Growth`, `Markets Growing`, and `Data Integrity Failures`. Bar chart: city vs `2024 Passengers` and `2025 Passengers`. Add region slicer.

**Route Explorer:** Table: code, city, y2024, y2025, delta, growth_pct; conditional formatting and cards for total selected passenger movements. Use weighted growth, not sum of per-route growth rates.

**Sensitivity:** Use What-if parameter tables with 0.5%–12% assumed capture, 200–1500 assumed fare, 100–2000 annual departures, 150–450 seats per flight. `bi/measures.dax` shows capped load-factor measure examples. Explicitly add a visual disclaimer: ONLY all-airline airport traffic comes from the CAA. All other settings are invented.

## Why no Power BI revenue, actual capacity or connection metrics appear by default

They cannot be derived from annual CAA Table 12.1; pretending otherwise would be misleading. Use the `scripts/ingest_bts.py` adapter for authentic BTS segment capacity where available, and maintain careful differences in population, period and measurement basis when comparing to CAA data.

You may save a genuine `.pbix` or `.pbip` from Desktop after you build and verify the report. Never rename a text or HTML file to `.pbix` as a shortcut.
