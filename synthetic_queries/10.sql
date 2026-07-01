-- Redbench synthetic query for TPC-H Q10
-- Feature fingerprint: tpch_q10

SELECT DISTINCT ON("supplier"."s_suppkey") "supplier"."s_name", "supplier"."s_acctbal" FROM "supplier" JOIN partsupp ON "supplier"."s_suppkey" = "partsupp"."ps_suppkey" JOIN part ON "partsupp"."ps_partkey" = "part"."p_partkey" JOIN lineitem ON "supplier"."s_suppkey" = "lineitem"."l_suppkey" WHERE "part"."p_comment" BETWEEN 'e qui' AND 'ut the pending pac' AND "lineitem"."l_comment" BETWEEN 'ending accoun' AND 'y unusual req' AND "partsupp"."ps_supplycost" BETWEEN 141.43 AND 790.07 AND "supplier"."s_phone" BETWEEN '17-244-746-2199' AND '33-484-154-9190';
