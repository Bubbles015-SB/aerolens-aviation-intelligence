# Data and provenance register

## Source A — UK Civil Aviation Authority (observed, curated)

- Publisher: UK Civil Aviation Authority.
- Publication: [Annual airport data 2025](https://www.caa.co.uk/data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-2025/annual-2025/), Table **12.1 Intl Air Passenger Traffic Route Analysis**.
- Raw selection committed: `data/raw/caa_lhr_us_annual_2025_2024_curated.csv` (28 selected Heathrow–US airport pairs, annual 2024 vs 2025).
- Includes **both directions and all airlines combined** for each selected airport pair; source is compiled and attributed by the CAA.
- This is **not** an exhaustive list of Heathrow–US destinations and is **not** carrier-specific.
- Data checksum is computed at generation time and stored in `data/scenarios/enterprise_summary.json`.
- CAA requires attribution and prohibits reselling its statistical data. The project attributes the CAA and does not commercially resell the data.

## Source B — BTS T-100 (external import only)

- Publisher: US Bureau of Transportation Statistics.
- Source: [T-100 International Segment (All Carriers)](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FJE).
- No downloaded carrier-level extract is distributed. The importers require the user to supply the source file and provenance note; only then can the model compute carrier-specific seats and seat load factors.
- Structural validation cannot authenticate an arbitrary CSV or determine actual carrier commercial revenue.

## Source C — user-provided dated flight schedules (optional)

- No licensed real flight schedule is bundled. External CSV requires `flight_id,carrier,origin,destination,departure_local,arrival_local` where local datetimes include valid time zone offset.
- `aerolens/operations.py` checks UTC, airport IANA offsets, duplicate flight IDs and flight chronology.
- The user must verify permission, original publication, schedule accuracy, interline eligibility and downstream legal rights.

## Source D — synthetic scenario engine

All route planning fares, costs, weekly demand conversion, flight capacities, fuel burn, aircraft block hours, emissions, financial uncertainty, alliances, fictional carrier codes and assurance records are **illustrative assumptions**.

- Network: 154 hypothetical dated legs, carriers AX/BX/CX/DX. Valid UTC chronology is a test result, not evidence those flights operated.
- Fleet: 9 hypothetical routes; the related market size is observed from CAA, **but conversion to weekly route demand and every economic input is assumed**.
- Engineering assurance: 40 fictional technical records. Not personal data or confidential aircraft documents.
- Monthly forecast demo: 48 synthetic observations. Used only to exercise the backtest system, not to claim observed seasonality.
- Emissions: geometric great-circle distance is computed from public airport coordinates; assumed burn factor and fuel use do not indicate real aircraft emissions.

## Reproducibility

Run `python scripts/build_data.py && python scripts/build_advanced.py && python scripts/build_enterprise.py && python scripts/build_powerbi.py`. Observed and synthetic material are labelled and exported to different files. Any extension must include source URL, retrieval date, licence/redistribution rights and file checksum.
