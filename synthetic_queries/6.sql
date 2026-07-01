-- Redbench synthetic query for TPC-H Q6
-- Feature fingerprint: tpch_q06

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_extendedprice", "lineitem"."l_commitdate" FROM "lineitem" WHERE "lineitem"."l_discount" BETWEEN 0.04 AND 0.09;
