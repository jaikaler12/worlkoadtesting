-- Redbench synthetic query for TPC-H Q16
-- Feature fingerprint: tpch_q16
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("customer_1"."c_custkey") "customer_1"."c_address" FROM "customer_1" JOIN orders_1 ON "customer_1"."c_custkey" = "orders_1"."o_custkey" JOIN nation_1 ON "customer_1"."c_nationkey" = "nation_1"."n_nationkey" JOIN lineitem_1 ON "orders_1"."o_orderkey" = "lineitem_1"."l_orderkey" WHERE "customer_1"."c_phone" BETWEEN '10-325-233-9271' AND '34-999-618-6881' AND "lineitem_1"."l_shipinstruct" BETWEEN 'COLLECT COD' AND 'TAKE BACK RETURN' AND "nation_1"."n_name" BETWEEN 'ALGERIA' AND 'VIETNAM' AND "orders_1"."o_orderpriority" BETWEEN '1-URGENT' AND '5-LOW';
