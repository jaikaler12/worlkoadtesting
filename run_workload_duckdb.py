import duckdb
import csv
import glob
import os

DB_PATH = os.path.expanduser(
    "~/Redbench/output/tmp_generation/tpch/db_augmented_x2.duckdb"
)
WORKLOAD_GLOB = os.path.expanduser(
    "~/Redbench/output/generated_workloads/tpch/provisioned/cluster_1/database_1/*/workload.csv"
)

wl_files = glob.glob(WORKLOAD_GLOB)
if not wl_files:
    raise FileNotFoundError(f"No workload.csv found matching {WORKLOAD_GLOB}")
wl_file = wl_files[0]
print(f"Using workload: {wl_file}")

# read_only=True avoids grabbing an exclusive lock (safe alongside the CLI)
conn = duckdb.connect(DB_PATH, read_only=True)

results = {}
with open(wl_file) as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        sql = row["sql"]
        fp = row.get("feature_fingerprint", f"query_{i+1}")
        try:
            result = conn.sql(sql).fetchall()
            print(f"query_{i+1} ({fp}): OK — {len(result)} rows")
            results[f"query_{i+1}"] = {"status": "ok", "fingerprint": fp, "rows": len(result)}
        except Exception as e:
            print(f"query_{i+1} ({fp}): ERROR — {e}")
            results[f"query_{i+1}"] = {"status": "error", "fingerprint": fp, "error": str(e)}

conn.close()

ok = sum(1 for v in results.values() if v["status"] == "ok")
print(f"\nDone: {ok}/{len(results)} queries ran successfully")
