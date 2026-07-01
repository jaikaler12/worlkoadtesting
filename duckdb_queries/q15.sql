-- Redbench synthetic query for TPC-H Q15
-- Feature fingerprint: tpch_q15
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("lineitem_0"."l_orderkey", "lineitem_0"."l_linenumber") "lineitem_0"."l_returnflag", "lineitem_0"."l_extendedprice", "lineitem_0"."l_receiptdate" FROM "lineitem_0" JOIN supplier_0 ON "lineitem_0"."l_suppkey" = "supplier_0"."s_suppkey" JOIN orders_0 ON "lineitem_0"."l_orderkey" = "orders_0"."o_orderkey" WHERE "orders_0"."o_orderstatus" BETWEEN 'F' AND 'O' AND "lineitem_0"."l_commitdate" BETWEEN '1995-12-03T00:00:00' AND '1996-04-02T00:00:00' AND "supplier_0"."s_comment" BETWEEN 'de of the express requests. pinto beans are' AND 'efully regular courts. furiousl';
