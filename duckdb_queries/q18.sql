-- Redbench synthetic query for TPC-H Q18
-- Feature fingerprint: tpch_q18
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("supplier_0"."s_suppkey") "supplier_0"."s_name", "supplier_0"."s_suppkey" FROM "supplier_0" JOIN nation_0 ON "supplier_0"."s_nationkey" = "nation_0"."n_nationkey" JOIN partsupp_0 ON "supplier_0"."s_suppkey" = "partsupp_0"."ps_suppkey" JOIN customer_0 ON "nation_0"."n_nationkey" = "customer_0"."c_nationkey" WHERE "nation_0"."n_name" BETWEEN 'ALGERIA' AND 'VIETNAM' AND "partsupp_0"."ps_supplycost" BETWEEN 11.01 AND 1000.0 AND "customer_0"."c_address" BETWEEN 'cSQC5d1NM' AND 'zzxGktzXTMKS1BxZlgQ9nqQ' AND "supplier_0"."s_acctbal" BETWEEN -888.33 AND 9999.72;
