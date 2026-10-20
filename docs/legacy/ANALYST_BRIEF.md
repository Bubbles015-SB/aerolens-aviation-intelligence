# Analyst brief — Heathrow–US passenger movements, 2025 vs 2024

**Prepared for Salonee Shrigandhamurthy as an AI-assisted independent portfolio prototype.** This is a transparent route-screening demonstration, **not an airline commercial plan, Virgin Atlantic forecast or investment recommendation.**

## Executive readout

An extract of 28 Heathrow–US airport pairs from the UK Civil Aviation Authority's [2025 Annual Table 12.1](https://www.caa.co.uk/Documents/Download/24007/87fb7670-4e10-4aeb-942d-509238aa25a1/17511) shows total passenger throughput of **17,126,332 in 2025**, compared with **17,338,833 in 2024**, a **decrease of 212,501 (−1.23%)** in this curated selection.

Of the 28 markets, **15 grew** and **13 declined**. These observations do not imply that all Heathrow–US traffic declined by the same amount, because the sample is not exhaustive. They also cannot be attributed to any particular airline.

### Three signals worth pursuing

1. **Los Angeles (LAX): 1,459,443 (2025), down 220,440 vs 2024 (−13.1%).** This is the largest absolute change in the sample. A route-performance analyst should investigate whether seats, competition, operating patterns, aircraft deployment or underlying traffic demand changed. The annual totals alone cannot establish which explanation is correct.
2. **Austin (AUS): 247,328 (2025), up 42,299 (+20.6%).** A large relative increase on a smaller base. Investigate origin-destination demand, capacity additions and business-travel mix before classifying the market as a network opportunity.
3. **Atlanta (ATL): 790,122 (2025), up 50,500 (+6.8%).** The greatest positive change in raw passenger count among the selected markets. Analyse carrier mix and connecting traffic to determine what portion is accessible to any individual airline.

### Region-level screen within the sample

| Analyst-assigned region | 2024 passengers | 2025 passengers | Change | Growth |
|---|---:|---:|---:|---:|
| Northeast | 6,632,599 | 6,706,295 | +73,696 | +1.11% |
| South | 4,365,078 | 4,360,800 | −4,278 | −0.10% |
| Midwest | 1,417,262 | 1,383,326 | −33,936 | −2.39% |
| West | 4,923,894 | 4,675,911 | −247,983 | −5.04% |

**Critical boundary:** U.S. regional groupings are manually assigned for convenience, not CAA-provided categories. They do not imply all routes in a region are comparable in distance, passenger mix, economics or carrier competition.

## Commercial hypotheses, not conclusions

**Hypothesis A — LAX contraction:** The 2025 decrease may be more strongly linked to changed seat supply than deteriorating underlying demand. Test with airline-specific weekly seats, aircraft gauge, load factors, city-pair O&D, average fares, other airports and seasonality.

**Hypothesis B — ATL opportunity:** Growing market-level traffic may support commercial opportunities through a strengthened partnership, but only if there is a feasible schedule, competitive price, favourable connection quality and positive incremental contribution. Evaluate realistic transit flows and cost allocation.

**Hypothesis C — route portfolio resilience:** Market-by-market differences warrant segmentation rather than a single network-wide assumption. Integrate market size, growth, carrier share, revenue yield, and sensitivity to fuel and exchange rates into a common appraisal framework.

## Alliance demonstration

The accompanying **Alliance Lab** illustrates graph-based path discovery and an explicitly simplified connection ranking approach. All 154 dated illustrative flight legs, carrier labels, transfer requirements and itinerary eligibility remain **synthetic**, but local times are now converted using real IANA airport time zones and compared as UTC instants. These are neither published timetables nor verified direct flights or protected ticketed itineraries. The exercise demonstrates potential tool design, not real joint-venture performance.

## Decision gate

**Do not recommend adding or removing capacity on the evidence in this project.** A defensible recommendation would require the full commercial data pack: airline-level traffic and yield, fleet/crew constraints, passenger preference, cabin mix, network connections, existing capacity, operating costs, slots and sensitivity to schedule changes.

## Reproducibility

```bash
python scripts/build_data.py
python scripts/build_advanced.py
python scripts/run_sql_demo.py
python -m unittest discover -s tests -v
```

Use `data/derived/route_summary.csv`, or the interactive web dashboard at `index.html`. Source and transformation details live in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

## AeroLens 2: capacity-constrained scenarios

The v2 Contribution & Risk Studio enforces seat-capacity limits and calculates break-even seat load factor from explicitly invented flights, seat count, fare and cost assumptions. Its seeded Monte Carlo produces **illustrative** scenario percentiles only. Do not confuse it with an empirically calibrated airline forecast. Carrier-specific load factors can be computed only if the user independently provides a legitimate BTS T-100 segment extract and validates its source.
