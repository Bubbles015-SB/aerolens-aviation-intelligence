-- SQLite, aviation analytics example. All CAA inputs are annual all-airline two-way totals.
-- table lhr_us_routes(code TEXT,city TEXT,region TEXT,y2024 INTEGER,y2025 INTEGER)
-- table bts_carrier_segments(year INT,month INT,carrier TEXT,airport_a TEXT,airport_b TEXT,
--       passengers INT,seats INT,departures INT) -- OPTIONAL, REAL SOURCE ONLY.

-- Market concentration WITHIN THE SELECTED CAA SAMPLE only (NOT carrier HHI).
WITH sample AS (
 SELECT code,city,region,y2024,y2025,
        1.0*y2025/SUM(y2025) OVER () AS sample_share
 FROM lhr_us_routes
)
SELECT code,city,ROUND(sample_share*100,2) AS curated_sample_share_pct,
       ROUND(sample_share*sample_share*10000,1) AS sample_share_sq_index
FROM sample ORDER BY sample_share DESC;

-- Ranked market screens with a volume threshold, not a route recommendation.
WITH changes AS (
 SELECT code,city,region,y2024,y2025,
        y2025-y2024 AS delta,
        100.0*(y2025-y2024)/NULLIF(y2024,0) AS pct_change
 FROM lhr_us_routes
)
SELECT *, DENSE_RANK() OVER (ORDER BY ABS(delta) DESC) AS magnitude_rank
FROM changes WHERE y2024>=100000 ORDER BY magnitude_rank;

-- Run ONLY after ingesting authentic BTS T100 segment data into a database table.
-- Illustrates how a truly observed carrier seat-load factor would be computed.
SELECT year,carrier,CASE WHEN airport_a='LHR' THEN airport_b ELSE airport_a END AS other_airport,
       SUM(passengers) AS observed_carrier_segment_pax,
       SUM(seats) AS observed_carrier_segment_seats,
       ROUND(100.0*SUM(passengers)/NULLIF(SUM(seats),0),2) AS observed_segment_load_factor_pct
FROM bts_carrier_segments
WHERE airport_a='LHR' OR airport_b='LHR'
GROUP BY year,carrier,other_airport
ORDER BY year,observed_carrier_segment_pax DESC;
