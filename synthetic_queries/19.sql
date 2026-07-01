-- Redbench synthetic query for TPC-H Q19
-- Feature fingerprint: tpch_q19

SELECT DISTINCT ON("lineitem"."l_orderkey", "lineitem"."l_linenumber") "lineitem"."l_linestatus", "lineitem"."l_shipmode" FROM "lineitem" JOIN partsupp ON "lineitem"."l_partkey" = "partsupp"."ps_partkey" AND "lineitem"."l_suppkey" = "partsupp"."ps_suppkey" WHERE "lineitem"."l_shipinstruct" BETWEEN 'DELIVER IN PERSON' AND 'TAKE BACK RETURN' AND "partsupp"."ps_comment" BETWEEN '. slyly even theodolites about the packages cajole slyly regular asymptotes. slyly ironic pac' AND 'ously ironic theodolites wake slyly across the unusu';
