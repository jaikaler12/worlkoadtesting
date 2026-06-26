-- Redbench synthetic query for TPC-H Q15
-- Feature fingerprint: tpch_q15

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_suppkey", "lineitem"."l_orderkey", "lineitem"."l_shipdate", "lineitem"."l_orderkey", "lineitem"."l_discount" FROM "lineitem" JOIN supplier ON "lineitem"."l_suppkey" = "supplier"."s_suppkey" WHERE "lineitem"."l_commitdate" BETWEEN '1994-05-06' AND '1997-10-06' AND "supplier"."s_name" BETWEEN 'Supplier#000001200' AND 'Supplier#000006400';
