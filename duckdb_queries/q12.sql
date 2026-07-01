-- Redbench synthetic query for TPC-H Q12
-- Feature fingerprint: tpch_q12
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("lineitem_0"."l_orderkey", "lineitem_0"."l_linenumber") "lineitem_0"."l_linenumber" FROM "lineitem_0" JOIN orders_0 ON "lineitem_0"."l_orderkey" = "orders_0"."o_orderkey" WHERE "lineitem_0"."l_extendedprice" BETWEEN 46071.5 AND 52749.48 AND "orders_0"."o_comment" BETWEEN 'riously ironic instructio' AND 't dugouts about the excuses sleep slyly against';
