-- Redbench synthetic query for TPC-H Q22
-- Feature fingerprint: tpch_q22

SELECT DISTINCT ON("supplier"."s_suppkey") "supplier"."s_nationkey", "supplier"."s_suppkey", "supplier"."s_phone" FROM "supplier" JOIN partsupp ON "supplier"."s_suppkey" = "partsupp"."ps_suppkey" WHERE "partsupp"."ps_comment" BETWEEN 'against the ironic, special theodolites. blithely fluffy accounts mold quickly even packages; blithely unusual accounts boost sly' AND 'zzle. unusual decoys detect slyly blithely express frays. furiously ironic packages about the bold accounts are close requests. slowly silent reque' AND "supplier"."s_phone" BETWEEN '10-306-516-3320' AND '34-998-900-4911';
