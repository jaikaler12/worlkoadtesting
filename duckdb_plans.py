import duckdb
import json
import os

# Configuration paths
QUERY_DIR = os.path.expanduser("/home/kaler/worlkoadtesting/duckdb_queries")
OUTPUT_FILE = "all_query_plans.json"

con = duckdb.connect("~/Redbench/output/tmp_generation/tpch/db_augmented_x2.duckdb")
con.execute("SET memory_limit='16GB'")
# Enable profiling once up front
con.sql("PRAGMA enable_profiling='json'")
con.sql("PRAGMA profiling_output='/tmp/profile.json'")

results = {}
for i in range(1, 23):
    query_file = os.path.join(QUERY_DIR, f"q{i}.sql")
    query_key = f"query_{i}"

    if not os.path.exists(query_file):
        print(f"[-] {query_file} not found. Skipping.")
        continue

    with open(query_file, "r") as f:
        sql = f.read().strip()

    try:
        # con.sql() is LAZY — it only builds a relation, it does not execute.
        # .fetchall() forces actual execution so the profiler captures real work.
        con.sql(sql).fetchall()

        # Read JSON profile
        with open("/tmp/profile.json") as pf:
            plan = json.load(pf)
        results[query_key] = plan
        print(f"[+] {query_key} OK")

    except Exception as e:
        results[query_key] = {"error": str(e)}
        print(f"[-] {query_key} failed: {e}")

con.close()

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=4)

print(f"\nDone! All query plans saved to {OUTPUT_FILE}")
