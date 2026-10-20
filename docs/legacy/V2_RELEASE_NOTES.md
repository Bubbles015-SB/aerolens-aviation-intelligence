# AeroLens 2 release notes

The initial single-day arithmetic connectivity mock-up was replaced in the visible application by a **time-zone-aware 7-day network simulation**; the prior v1 code still exists as a legacy module for comparison, but its model is not displayed in the v2 Alliance Lab. For v2 use `assets/advanced.js` and `aerolens/connectivity.py` rather than the old `findItineraries` method in `assets/app.js`.

**Added:** 154 independently synthetic dated flight legs, IANA time-zone aware travel, DST unit tests, UTC transfers with assumed buffer rules, up to 2 transfers, multiple ranking methods, Pareto screen, distance proxy, new capacity-constrained commercial model, break-even feasibility, 2,500-draw interactive stress test, CLI 2,500-draw stress test, optional BTS real segment CSV import (Python and browser), explicit checksums, validation, SQL/DAX/Power Query kit, screenshots, CI and extended tests.

**Not added:** airline proprietary profitability, real protected booking itineraries, real on-time probability calibration, real Virgin Atlantic load factors, live external booking APIs, actual `.pbix` (requires Windows Power BI Desktop). Do not present those as included.

**Known differences across independent implementations:** the Python and JavaScript Monte Carlo tools use different seeded pseudorandom generators; percentile point estimates will differ slightly. This is a *scenario sensitivity exercise*, not statistically validated confidence bounds.
