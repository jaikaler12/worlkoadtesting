-- Redbench synthetic query for TPC-H Q22
-- Feature fingerprint: tpch_q22
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("supplier_0"."s_suppkey") "supplier_0"."s_nationkey", "supplier_0"."s_phone", "supplier_0"."s_name", "supplier_0"."s_name" FROM "supplier_0" JOIN nation_0 ON "supplier_0"."s_nationkey" = "nation_0"."n_nationkey" JOIN region_0 ON "nation_0"."n_regionkey" = "region_0"."r_regionkey" JOIN lineitem_0 ON "supplier_0"."s_suppkey" = "lineitem_0"."l_suppkey" JOIN part_0 ON "lineitem_0"."l_partkey" = "part_0"."p_partkey" WHERE "region_0"."r_comment" BETWEEN 'ges. thinly even pinto beans ca' AND 'ges. thinly even pinto beans ca' AND "supplier_0"."s_address" BETWEEN 'UZUhxJGMhAV2dev7aQ3bn4J' AND 'YKxTys0SBFcdjS2B9Dk8D GWwE4u' AND "part_0"."p_retailprice" BETWEEN 1599.59 AND 1659.65 AND "nation_0"."n_name" BETWEEN 'UNITED STATES' AND 'VIETNAM' AND "lineitem_0"."l_comment" BETWEEN 'nt requests according to the quickly' AND 'packages cajole slyly e';
