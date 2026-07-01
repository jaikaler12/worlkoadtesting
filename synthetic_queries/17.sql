-- Redbench synthetic query for TPC-H Q17
-- Feature fingerprint: tpch_q17

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_linestatus", "lineitem"."l_comment", "lineitem"."l_orderkey" FROM "lineitem" JOIN orders ON "lineitem"."l_orderkey" = "orders"."o_orderkey" JOIN partsupp ON "lineitem"."l_partkey" = "partsupp"."ps_partkey" AND "lineitem"."l_suppkey" = "partsupp"."ps_suppkey" WHERE "lineitem"."l_linestatus" BETWEEN 'F' AND 'O' AND "partsupp"."ps_comment" BETWEEN 'even foxes. silent, ironic deposits sleep above the enticingly p' AND 'ular theodolites. furiously express theodolites haggle blithely according to the quickly even packages. packages alo' AND "orders"."o_orderstatus" BETWEEN 'F' AND 'O';
