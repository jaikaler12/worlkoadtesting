-- Redbench synthetic query for TPC-H Q3
-- Feature fingerprint: tpch_q03

SELECT DISTINCT ON("supplier"."s_suppkey") "supplier"."s_nationkey", "supplier"."s_nationkey" FROM "supplier" JOIN nation ON "supplier"."s_nationkey" = "nation"."n_nationkey" JOIN lineitem ON "supplier"."s_suppkey" = "lineitem"."l_suppkey" WHERE "lineitem"."l_returnflag" BETWEEN 'A' AND 'N' AND "nation"."n_comment" BETWEEN 'slyly express asymptotes. regular deposits haggle slyly. carefully ironic hockey players sleep blithely. carefull' AND 'ts. silent requests haggle. closely express packages sleep across the blithely' AND "supplier"."s_phone" BETWEEN '18-462-213-5795' AND '34-792-190-3269';
