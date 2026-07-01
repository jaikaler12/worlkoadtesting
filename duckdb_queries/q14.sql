-- Redbench synthetic query for TPC-H Q14
-- Feature fingerprint: tpch_q14
-- Run against: db_augmented_x2.duckdb

SELECT DISTINCT ON("lineitem_0"."l_orderkey", "lineitem_0"."l_linenumber") "lineitem_0"."l_shipinstruct" FROM "lineitem_0" JOIN partsupp_0 ON "lineitem_0"."l_partkey" = "partsupp_0"."ps_partkey" AND "lineitem_0"."l_suppkey" = "partsupp_0"."ps_suppkey" WHERE "lineitem_0"."l_shipdate" BETWEEN '1994-10-22T00:00:00' AND '1995-02-20T00:00:00' AND "partsupp_0"."ps_comment" BETWEEN 'refully bold instructions. even packages are-- regular epitaphs wake alongside of the carefully even accounts. bold pinto beans wake blithely at the re' AND 's sleep alongside of the furiously special deposits. furiously final id';
