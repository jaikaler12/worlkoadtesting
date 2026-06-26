-- Redbench synthetic query for TPC-H Q13
-- Feature fingerprint: tpch_q13

SELECT DISTINCT ON("supplier"."s_suppkey") "supplier"."s_suppkey", "supplier"."s_acctbal", "supplier"."s_phone" FROM "supplier" JOIN partsupp ON "supplier"."s_suppkey" = "partsupp"."ps_suppkey" WHERE "partsupp"."ps_availqty" BETWEEN 99 AND 9999 AND "supplier"."s_phone" BETWEEN '10-306-516-3320' AND '34-998-900-4911';
