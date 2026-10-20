# AeroLens v2 data dictionary and contracts

| Dataset | File | Actual or hypothetical? | Grain | Main fields |
|---|---|---|---|---|
| CAA market selection | `data/raw/caa_lhr_us_annual_2025_2024_curated.csv` | **OBSERVED**, UK CAA Table 12.1, manually curated | one Heathrow–US airport pair | airport, city, region (analyst assigned), passengers_2024, passengers_2025 |
| CAA derived metrics | `data/derived/route_summary.csv` | **DETERMINISTIC FROM OBSERVED** | airport pair | code, y2024, y2025, delta, growth_pct |
| Time-expanded flight scenario | `data/advanced/synthetic_time_aware_schedule.json` | **ENTIRELY SYNTHETIC** | one dated flight leg | id, origin, destination, carrier label, local and UTC dates/times, duration_minutes, schedule_status |
| Optional genuine BTS segments | user-selected BTS T-100 CSV file | **OBSERVED IF AUTHENTIC INPUT SUPPLIED** | carrier × leg × month/year | carrier, origin, destination, year, month, passengers, seats, departures_performed |
| Commercial inputs | browser sliders | **ENTIRELY SYNTHETIC** | one scenario | share, frequency, seats, net fare, flight cost, variable cost, fixed cost, sigma |

Annual UK CAA data are **all-carrier, both-direction** market movements. They are not direct O&D traffic, airline-specific sales, Virgin Atlantic passenger totals, yields, margins or seat capacity. Public UK CAA statistical data may not be resold and must be attributed. Source: https://www.caa.co.uk/data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-2025/annual-2025/

Carrier-level seat load factor is calculated only from an authentic BTS segment export: `sum(segment_passengers) / sum(segment_seats)`, including a zero-seat guard. This is **segment seat utilisation**, not market share, full O&D itinerary occupancy, or commercial profitability. Source: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FJE

Synthetic flight times are in IANA airport time zones, converted to UTC for all duration and transfer arithmetic. Every flight is identified as `synthetic`, including carrier labels. The algorithm does NOT establish real codeshare eligibility or valid minimum transfer rules.
