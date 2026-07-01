-- Redbench synthetic query for TPC-H Q12
-- Feature fingerprint: tpch_q12

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_shipinstruct" FROM "lineitem" JOIN orders ON "lineitem"."l_orderkey" = "orders"."o_orderkey" WHERE "lineitem"."l_shipdate" BETWEEN '1993-03-23' AND '1997-05-16' AND "orders"."o_orderpriority" BETWEEN '2-HIGH' AND '5-LOW';
