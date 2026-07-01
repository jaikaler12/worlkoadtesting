-- Redbench synthetic query for TPC-H Q6
-- Feature fingerprint: tpch_q06
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("lineitem_0"."l_orderkey", "lineitem_0"."l_linenumber") "lineitem_0"."l_extendedprice" FROM "lineitem_0" WHERE "lineitem_0"."l_shipinstruct" BETWEEN 'COLLECT COD' AND 'DELIVER IN PERSON';
