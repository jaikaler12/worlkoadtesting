-- Redbench synthetic query for TPC-H Q4
-- Feature fingerprint: tpch_q04

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_linenumber" FROM "lineitem" JOIN supplier ON "lineitem"."l_suppkey" = "supplier"."s_suppkey" WHERE "lineitem"."l_extendedprice" BETWEEN 12981.65 AND 59571.0 AND "supplier"."s_comment" BETWEEN 'the slyly ironic packages nod fluffily according to the s' AND 'requests cajole about the fluffily regular accounts. pending courts after the ironic packages cajole';
