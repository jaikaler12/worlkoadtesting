-- Redbench synthetic query for TPC-H Q18
-- Feature fingerprint: tpch_q18

SELECT DISTINCT ON("supplier"."s_suppkey") "supplier"."s_comment", "supplier"."s_phone", "supplier"."s_comment" FROM "supplier" JOIN partsupp ON "supplier"."s_suppkey" = "partsupp"."ps_suppkey" JOIN lineitem ON "partsupp"."ps_partkey" = "lineitem"."l_partkey" AND "partsupp"."ps_suppkey" = "lineitem"."l_suppkey" JOIN part ON "partsupp"."ps_partkey" = "part"."p_partkey" WHERE "part"."p_comment" BETWEEN 'ding dolph' AND 'unts wake silen' AND "lineitem"."l_discount" BETWEEN 0.01 AND 0.08 AND "partsupp"."ps_supplycost" BETWEEN 141.43 AND 790.07 AND "supplier"."s_acctbal" BETWEEN 1540.35 AND 8686.17;
