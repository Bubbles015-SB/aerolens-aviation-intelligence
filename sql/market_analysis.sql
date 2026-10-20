-- AeroLens example analytical queries (SQLite dialect)
-- Data contract: lhr_us_routes(code TEXT, city TEXT, region TEXT,
--                          y2024 INTEGER, y2025 INTEGER)
-- 2024/2025 annual UK CAA total airport-pair passengers, all airlines, both directions.
-- IMPORTANT: This is not Virgin Atlantic airline-level data, revenue or route profitability.

-- 1. Overall curated market change: conditional aggregation and defensive divide-by-zero.
SELECT COUNT(*) AS selected_airport_pairs,
       SUM(y2024) AS passengers_2024,
       SUM(y2025) AS passengers_2025,
       SUM(y2025 - y2024) AS absolute_change,
       ROUND(100.0*(SUM(y2025) - SUM(y2024)) / NULLIF(SUM(y2024),0), 2) AS yoy_percent
FROM lhr_us_routes;

-- 2. Contribution of each route to overall year-on-year absolute movement.
SELECT code, city, region, y2024, y2025,
       (y2025 - y2024) AS delta,
       ROUND(100.0*(y2025-y2024) / NULLIF(y2024,0), 1) AS growth_pct,
       ROUND(100.0*y2025 / SUM(y2025) OVER (), 2) AS curated_sample_share_pct
FROM lhr_us_routes
ORDER BY ABS(delta) DESC;

-- 3. Which U.S. region of this curated selection had the largest movements?
SELECT region,
       COUNT(*) AS markets,
       SUM(y2024) AS market_pax_2024,
       SUM(y2025) AS market_pax_2025,
       SUM(y2025)-SUM(y2024) AS change_pax,
       ROUND(100.0*(SUM(y2025)-SUM(y2024))/NULLIF(SUM(y2024),0), 2) AS change_pct
FROM lhr_us_routes
GROUP BY region
ORDER BY change_pax DESC;

-- 4. Top gaining markets with a material 2024 baseline (>100,000 pax).
SELECT code, city, y2025-y2024 AS delta,
       ROUND(100.0*(y2025-y2024)/NULLIF(y2024,0), 1) AS yoy_pct
FROM lhr_us_routes
WHERE y2024 >= 100000 AND y2025 > y2024
ORDER BY yoy_pct DESC
LIMIT 10;
