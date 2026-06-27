import subprocess
import json
import os
import re

DB_USER = "kaler"
DB_NAME = "imdbjob"
os.environ["PGPASSWORD"] = "jaideep.34"
os.environ["PAGER"] = ""

QUERY_DIR = os.path.expanduser("/home/kaler/worlkoadtesting/imdb_job_queries")
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

for i in range(1, 114):
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

        create_parts = [s for s in parts if re.match(r"\s*create", s, re.I)]
        select_parts = [s for s in parts if re.match(r"\s*select", s, re.I)]
        
        
        
       
        # Use the LAST SELECT - synthetic files sometimes have a setup SELECT first
        stmt = select_parts[-1] if select_parts else parts[-1]
        raw_out = run_psql(f"EXPLAIN (ANALYZE ,FORMAT JSON, BUFFERS)\n{stmt};")
        results[query_key] = json.loads(raw_out)

        print("    OK")

    except subprocess.CalledProcessError as e:
        print(f"[-] {query_key} failed.")
        print(f"    stderr: {e.stderr.strip()}")
        results[query_key] = {"error": "Execution failed", "stderr": e.stderr}

    except json.JSONDecodeError:
        print(f"[-] Failed to parse JSON for {query_key}.")
        results[query_key] = {"error": "Invalid JSON output"}

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=4)

print(f"\nDone! Plans saved to {OUTPUT_FILE}")
