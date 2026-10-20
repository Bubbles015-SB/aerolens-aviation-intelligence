# AeroLens 2 — Technical architecture

## Separation of concerns

```text
                  UK CAA 2025 TABLE 12.1  (OBSERVED)
                               |
      data/raw/caa_lhr_us_annual_2025_2024_curated.csv
                               |
                      scripts/build_data.py
                     /                       \
             route_summary.csv           assets/data.js
                     |                       |
       Power Query / SQL / DAX       Market intelligence UI
                                             |
                                      Commercial scenario UI
                                      (ALL OTHER INPUTS
                                        INVENTED ASSUMPTIONS)

           synthetic local flight templates (NOT REAL AIRLINES)
                              |
                     aerolens/connectivity.py
                              |
                      scripts/build_advanced.py
                             /          \
                 dated schedule JSON    advanced_data.js
                                              |
                                     UTC itinerary optimiser

                 USER-SUPPLIED AUTHENTIC BTS T100 (OPTIONAL)
                              |
                aerolens/ingest.py OR browser CSV import
                              |
           genuine segment capacity / seat load factor
               (never silently merged with CAA totals)
```

## What makes v2 more rigorous than v1

1. **Absolute chronology:** Flight records contain a calendar date, IANA time zone, ISO-8601 local departure/arrival and corresponding UTC instants. Connecting legs are compared in UTC, including overnight travel and daylight saving changes. Every leg is *synthetic*; time-zone rules themselves are real.
2. **Graph search with constraints:** The schedule becomes a directed time-expanded multigraph. A path is feasible only if the next departure follows arrival plus the assumed airport MCT and user buffer, layover is <=480 minutes, itinerary <=2400 elapsed minutes, stops are within configured bounds and there are no loops. Search is capped at 2 transfers in the web UI.
3. **Explicit multi-objective trade-off:** Paths are compared on total elapsed time, transfer count, and an assumed completion-probability model. Pareto screening rejects strictly dominated alternatives in the searched subset. **The score is not airline QSI.**
4. **Physically constrained scenarios:** The commercial simulator calculates desired market capture, offered seats, carried volume capped at seats, load factor <=100%, gross receipts, variable-plus-flight-plus-fixed costs and break-even load factor. Only the base all-airline airport passenger pool is observed.
5. **Transparent uncertainty:** A seeded Monte Carlo applies independent, hypothetical Gaussian shocks to market demand, captured share, fare and per-flight cost. The output is **not an empirical confidence interval**, financial forecast or model trained on airline data.
6. **Capacity enrichment is optional:** A BTS T-100 adapter can use authentic user-supplied segment data to calculate observed carrier-level passengers, seats and load factor. If no official BTS export is provided, the UI displays no fabricated carrier load factors.
7. **Evidence and governance:** Source CSV is SHA-256 fingerprinted; numerical claims are tagged observed or hypothetical; Python tests cover the boundary cases; GitHub Actions reruns builds/tests after commits.

## Model formulas

Market change:

```text
absolute_change = passengers_2025 - passengers_2024
weighted_annual_growth = sum(changes) / sum(passengers_2024)
```

Time-feasible transfer:

```text
UTC(next_departure) - UTC(previous_arrival) >= assumed_mct + user_buffer
UTC(next_departure) - UTC(previous_arrival) <= max_layover
```

Hypothetical commercial scenario:

```text
offered_seats = annual_flights * seats_per_flight
requested_pax = all_airline_market_pax * assumed_capture_rate
carried_pax = min(requested_pax, offered_seats)
model_load_factor = carried_pax / offered_seats
model_contribution = carried_pax*(assumed_fare - assumed_variable_cost_per_pax)
                     - flights*assumed_cost_per_flight - assumed_fixed_cost
break_even_pax = (flights*assumed_cost_per_flight+assumed_fixed_cost)
                 / (assumed_fare-assumed_variable_cost_per_pax)
```

If marginal fare contribution <=0, break-even is infeasible. A break-even load factor >100% is also infeasible within that assumed capacity plan.

## Limitations that cannot honestly be “fixed” without additional licensed or proprietary data

- UK CAA Table 12.1 is **annual, airport-to-airport, all-airline, both-direction traffic**. It does not identify a particular airline's route profit, average fare, seat inventory, annual load factor, network flows, market yield, or connection product.
- Production operational performance requires actual booked O&D data, real validated timetables, airspace schedules, reliable minimum-connection rules, traffic rights, protected-transfer agreements and appropriate user licensing.
- Live fares and share cannot be reverse-engineered from public aggregate passenger numbers. Actual revenue management and schedule optimisation would require a governed modelling environment and stronger data.
- Power BI Desktop is not installed in this environment. This repository includes an **M + DAX implementation kit**, not a validated `.pbix` or `.pbip`. The live web app is independently executable offline.
- Airline emissions cannot be inferred from great-circle distance alone. Any distance-based illustration is a proxy with invented coefficients, not verified CO₂ per passenger.
- The examples are not recommendations to alter service frequencies, enter/exit routes, or make commercial commitments.

## Project ownership and interview ethics

The prototype code was initially generated with AI assistance for Salonee's portfolio. She should personally audit source data, reproduce outputs, test control settings, make her own improvements, and author the final business recommendations before representing a level of independent project contribution in applications. It is legitimate to state that AI-assisted tools helped create a research prototype; not legitimate to claim undisclosed professional airline experience or production impact.
