-- Redbench synthetic query for TPC-H Q14
-- Feature fingerprint: tpch_q14

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_comment", "lineitem"."l_partkey" FROM "lineitem" JOIN supplier ON "lineitem"."l_suppkey" = "supplier"."s_suppkey" WHERE "lineitem"."l_commitdate" BETWEEN '1994-06-23' AND '1998-01-10' AND "supplier"."s_address" BETWEEN '9aNuRZI46e6b01tUcwkNoImkBE1' AND 'iXhvx5pFwt,AssHirVoyWjfn';
