# Interview walkthrough: talking about AeroLens without overclaiming

## 60-second project explanation

> I built AeroLens as an independent analysis of selected Heathrow–US aviation markets using the UK CAA's published 2025 annual route statistics and 2024 comparisons. It validates and visualises passenger volumes across 28 airport pairs, highlights changes that deserve commercial investigation, and demonstrates a hypothetical alliance connectivity model. I deliberately separated verified observed traffic from invented schedule and fare scenarios. The output is a screening tool, not a revenue forecast or a recommendation to change capacity.

**Only use the first-person script if Salonee can independently explain the implementation and genuinely understands the work.** This code was initially developed with AI assistance; she must review, personalise and be able to reproduce or modify it before presenting it as her own technical contribution.

## Technical walkthrough

1. **Raw source:** CAA annual 2025 Table 12.1 PDF. 28 Heathrow–US airport pairs transcribed into CSV.
2. **Data quality:** Python checks for expected schema, duplicated IATA codes, positive integer counts, and route-level consistency; the browser also recomputes key totals.
3. **Transformations:** 2024/2025 absolute deltas, route growth percentages, sample-level weighted totals.
4. **SQL analysis:** SQLite queries for aggregation, segment breakdown, route rankings and window-function shares.
5. **Dashboard:** Dependency-free HTML/JavaScript with filters, sortable market register, comparisons, scenario sliders and CSV export.
6. **Alliances model:** A time-expanded, date-aware graph search across explicitly fictional flight labels, using real time-zone arithmetic, fictitious minimum connection thresholds, up to two transfers, Pareto screening and a hypothetical reliability objective. It is **not** an airline-approved scheduling or QSI system.
7. **Commercial reading:** Why raw demand changes are necessary but insufficient evidence for route decisions.

## Likely hiring-manager questions

**Why did you choose annual market traffic?** It was a high-credibility public source that offered comparable 2024–2025 airport-pair totals. A next iteration would incorporate monthly traffic, airline seat supply and O&D data.

**Can you calculate Virgin Atlantic market share?** No. The CAA table includes all carriers and has no airline split; a carrier-specific dataset is required.

**Is your model a forecast of Virgin Atlantic revenue or route profitability?** No. The new scenario engine caps requested demand at invented offered seat capacity, then applies explicitly assumed fares, flight costs, per-passenger costs and a fixed-cost allowance. Without airline traffic, actual yields and costs it has no forecasting validity.

**Why are you using imaginary flights?** To demonstrate the underlying algorithm and tradeoffs without implying access to commercial timetable/PNR data or a licensed schedules database.

**Why not just use the biggest-growth market?** Changes can reflect capacity, airport substitution, aircraft gauge or an unusual base year; feasibility, margins and network effects matter.

**How would you improve the project next?** Add officially sourced UK CAA monthly records and properly licensed schedules, genuine origin-destination demand and commercial data, and a Power BI report authored in Desktop. Compare connection quality with a method validated by network-planning colleagues.

**What evidence supports your Power BI skill?** The project includes Power BI-ready CSV and a build guide, **not an authored `.pbix`**. If presenting as Power BI experience, build the report in Power BI Desktop first and be able to demonstrate it.
