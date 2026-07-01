-- Redbench synthetic query for TPC-H Q16
-- Feature fingerprint: tpch_q16

SELECT DISTINCT ON("customer"."c_custkey") "customer"."c_address" FROM "customer" JOIN nation ON "customer"."c_nationkey" = "nation"."n_nationkey" WHERE "nation"."n_name" BETWEEN 'ALGERIA' AND 'VIETNAM' AND "customer"."c_comment" BETWEEN 'against the slyly even ideas. carefully final accounts integrate a' AND 'zzle. blithely regular instructions cajol';
