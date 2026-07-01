-- Redbench synthetic query for TPC-H Q13
-- Feature fingerprint: tpch_q13
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("supplier_0"."s_suppkey") "supplier_0"."s_name", "supplier_0"."s_comment" FROM "supplier_0" JOIN lineitem_0 ON "supplier_0"."s_suppkey" = "lineitem_0"."l_suppkey" WHERE "lineitem_0"."l_shipmode" BETWEEN 'AIR' AND 'AIR' AND "supplier_0"."s_address" BETWEEN '9aNuRZI46e6b01tUcwkNoImkBE1' AND 'EyOgjdxcfyTvyw4MIs3YQoREk4FJ9Vt';
