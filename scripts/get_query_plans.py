import subprocess
import json
import os
import re

DB_USER = "kaler"
DB_NAME = "tpchdb"
os.environ["PGPASSWORD"] = "jaideep.34"
os.environ["PAGER"] = ""

QUERY_DIR = os.path.expanduser("/home/kaler/worlkoadtesting/synthetic_queries")
OUTPUT_FILE = "all_query_plans.json"

results = {}


def run_psql(sql):
    cmd = ["psql", "-U", DB_USER, "-h", "127.0.0.1", "-d", DB_NAME,
           "-q", "-t", "--no-psqlrc", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return re.sub(r' *\+\n', '', result.stdout).strip()


def split_sql_statements(sql):
    # Split on semicolons that are NOT inside single-quoted strings.
    statements = []
    current = []
    in_string = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        if in_string:
            if ch == "\\":
                current.append(ch)
                i += 1
                if i < len(sql):
                    current.append(sql[i])
                    i += 1
                continue
            elif ch == "'":
                current.append(ch)
                i += 1
                if i < len(sql) and sql[i] == "'":
                    current.append(sql[i])
                    i += 1
                else:
                    in_string = False
                continue
        else:
            if ch == "'":
                in_string = True
                current.append(ch)
                i += 1
                continue
            elif ch == ";":
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue
        current.append(ch)
        i += 1
    stmt = "".join(current).strip()
    if stmt:
        statements.append(stmt)
    return statements


def strip_line_comments(sql):
    clean_lines = []
    in_str = False
    for line in sql.splitlines():
        out = []
        j = 0
        while j < len(line):
            c = line[j]
            if in_str:
                if c == "\\":
                    out.append(c); j += 1
                    if j < len(line):
                        out.append(line[j]); j += 1
                    continue
                elif c == "'":
                    out.append(c); j += 1
                    if j < len(line) and line[j] == "'":
                        out.append(line[j]); j += 1
                    else:
                        in_str = False
                    continue
            else:
                if c == "'":
                    in_str = True
                elif c == "-" and j + 1 < len(line) and line[j+1] == "-":
                    break
            out.append(c)
            j += 1
        clean_lines.append("".join(out))
    return "\n".join(clean_lines)


print("Starting EXPLAIN analyze for 22 TPC-H queries...")

for i in range(1, 23):
    query_file = os.path.join(QUERY_DIR, f"{i}.sql")
    query_key = f"query_{i}"

    if not os.path.exists(query_file):
        print(f"[-] {query_file} not found. Skipping.")
        continue

    print(f"[+] Running {query_key}...")

    with open(query_file, "r") as f:
        raw_sql = f.read().strip()

    try:
        clean_sql = strip_line_comments(raw_sql)
        parts = split_sql_statements(clean_sql)

        # Identify the position of the main SELECT statement
        target_idx = -1
        for idx, s in enumerate(parts):
            if re.match(r"\s*select", s, re.I):
                target_idx = idx

        # Fallback if no explicit standalone SELECT is detected
        if target_idx == -1:
            target_idx = len(parts) - 1

        target_stmt = parts[target_idx]

        # 1. Execute setup statements (e.g., CREATE VIEW) preceding the SELECT
        for idx in range(target_idx):
            run_psql(f"{parts[idx]};")

        # 2. Run EXPLAIN ANALYZE on the primary SELECT statement
        try:
            raw_out = run_psql(f"EXPLAIN ( ANALYZE, FORMAT JSON, BUFFERS)\n{target_stmt};")
            results[query_key] = json.loads(raw_out)
            print("    OK")
        except subprocess.CalledProcessError as e:
            print(f"[-] {query_key} failed during EXPLAIN execution.")
            print(f"    stderr: {e.stderr.strip()}")
            results[query_key] = {"error": "EXPLAIN execution failed", "stderr": e.stderr}
        except json.JSONDecodeError:
            print(f"[-] Failed to parse JSON for {query_key}.")
            results[query_key] = {"error": "Invalid JSON output"}

        # 3. Execute cleanup statements (e.g., DROP VIEW) following the SELECT
        for idx in range(target_idx + 1, len(parts)):
            try:
                run_psql(f"{parts[idx]};")
            except subprocess.CalledProcessError as e:
                print(f"    [Warning] Cleanup statement failed: {parts[idx][:40]}... -> {e.stderr.strip()}")

    except subprocess.CalledProcessError as e:
        print(f"[-] {query_key} failed during setup environment stage.")
        print(f"    stderr: {e.stderr.strip()}")
        results[query_key] = {"error": "Setup execution failed", "stderr": e.stderr}

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=4)

print(f"\nDone! Plans saved to {OUTPUT_FILE}")
