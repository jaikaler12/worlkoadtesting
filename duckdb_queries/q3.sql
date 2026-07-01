-- Redbench synthetic query for TPC-H Q3
-- Feature fingerprint: tpch_q03
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("supplier_0"."s_suppkey") "supplier_0"."s_name" FROM "supplier_0" JOIN nation_0 ON "supplier_0"."s_nationkey" = "nation_0"."n_nationkey" JOIN partsupp_0 ON "supplier_0"."s_suppkey" = "partsupp_0"."ps_suppkey" WHERE "nation_0"."n_comment" BETWEEN 'haggle. carefully final deposits detect slyly agai' AND 'y final packages. slow foxes cajole quickly. quickly silent platelets breach ironic accounts. unusual pinto be' AND "partsupp_0"."ps_availqty" BETWEEN 99 AND 9999 AND "supplier_0"."s_acctbal" BETWEEN -888.33 AND 9999.72;
