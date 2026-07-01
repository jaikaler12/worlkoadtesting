-- Redbench synthetic query for TPC-H Q10
-- Feature fingerprint: tpch_q10
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("supplier_0"."s_suppkey") "supplier_0"."s_nationkey" FROM "supplier_0" JOIN nation_0 ON "supplier_0"."s_nationkey" = "nation_0"."n_nationkey" JOIN customer_0 ON "nation_0"."n_nationkey" = "customer_0"."c_nationkey" JOIN lineitem_0 ON "supplier_0"."s_suppkey" = "lineitem_0"."l_suppkey" WHERE "nation_0"."n_name" BETWEEN 'MOZAMBIQUE' AND 'PERU' AND "customer_0"."c_comment" BETWEEN 'deas among the carefully unusual pinto beans are sometimes ironic deposits: slyly final' AND 'efully ironic excuses. furiously regular requests according to the carefully final requests kindle blithe' AND "lineitem_0"."l_shipdate" BETWEEN '1996-08-25T00:00:00' AND '1996-12-23T00:00:00' AND "supplier_0"."s_comment" BETWEEN 'against the carefully ironic request' AND 'furiously regular requests haggle furiously bold pinto beans. quickly silent requests haggle a';
