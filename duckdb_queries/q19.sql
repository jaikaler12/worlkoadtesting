-- Redbench synthetic query for TPC-H Q19
-- Feature fingerprint: tpch_q19
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("lineitem_0"."l_orderkey", "lineitem_0"."l_linenumber") "lineitem_0"."l_shipdate" FROM "lineitem_0" JOIN partsupp_0 ON "lineitem_0"."l_partkey" = "partsupp_0"."ps_partkey" AND "lineitem_0"."l_suppkey" = "partsupp_0"."ps_suppkey" WHERE "lineitem_0"."l_comment" BETWEEN 'riously ironic ideas. i' AND 'uffily express ideas. packages are a' AND "partsupp_0"."ps_supplycost" BETWEEN 740.22 AND 889.72;
