-- Redbench synthetic query for TPC-H Q1
-- Feature fingerprint: tpch_q01

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_receiptdate", "lineitem"."l_comment" FROM "lineitem" WHERE "lineitem"."l_discount" BETWEEN 0.0 AND 0.05;
