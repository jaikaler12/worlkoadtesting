-- Redbench synthetic query for TPC-H Q11
-- Feature fingerprint: tpch_q11
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("orders_1"."o_orderkey") "orders_1"."o_orderdate", "orders_1"."o_orderkey", "orders_1"."o_custkey" FROM "orders_1" JOIN lineitem_1 ON "orders_1"."o_orderkey" = "lineitem_1"."l_orderkey" JOIN part_1 ON "lineitem_1"."l_partkey" = "part_1"."p_partkey" JOIN customer_1 ON "orders_1"."o_custkey" = "customer_1"."c_custkey" WHERE "part_1"."p_brand" BETWEEN 'Brand#11' AND 'Brand#55' AND "customer_1"."c_address" BETWEEN 'cSQC5d1NM' AND 'zzxGktzXTMKS1BxZlgQ9nqQ' AND "lineitem_1"."l_linestatus" BETWEEN 'F' AND 'O' AND "orders_1"."o_orderstatus" BETWEEN 'F' AND 'P';
