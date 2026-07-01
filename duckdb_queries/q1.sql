-- Redbench synthetic query for TPC-H Q1
-- Feature fingerprint: tpch_q01
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("lineitem_0"."l_orderkey", "lineitem_0"."l_linenumber") "lineitem_0"."l_receiptdate" FROM "lineitem_0" WHERE "lineitem_0"."l_discount" BETWEEN 0.0 AND 0.05;
