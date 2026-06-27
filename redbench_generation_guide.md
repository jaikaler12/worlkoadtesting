**Redbench Generation Strategy**

Running on a Custom Database & Custom Parquet Trace

*A complete guide: how it works, what broke, what was fixed, and a reusable pipeline*

# **1\. What is Redbench Generation Strategy?**

Redbench is a workload generator that synthesises SQL queries for a target database by learning structural patterns from a real-world cloud trace (Redset). The

**generation strategy** builds queries bottom-up: it samples query skeletons (join count, scan count, query type) from the trace, maps trace table IDs to your physical schema, then synthesises realistic SQL predicates using column statistics.

The

**matching strategy** (not covered here) instead takes an existing benchmark (TPC-DS, IMDB) and selects queries whose structure matches the trace. No custom schema needed, but less flexible.

## **1.1 High-Level Pipeline**

Redset trace (.parquet)

|

v

load\_and\_preprocess\_redset() <- filters, deduplicates, computes query\_hash

|

v

create\_normalized\_dataset() <- reads your CSVs, writes normalised copies

|

v

create\_quantiles() <- builds column\_statistics.json

|

v

prepare\_and\_scale\_dataset() <- duplicates tables (schema\_augmentation\_factor)

|

v

create\_duckdb() <- loads augmented CSVs into DuckDB

|

v

create\_workload() <- samples groups, maps tables, generates SQL

|

v

workload.csv <- final output

## **1.2 What the Trace (.parquet) Does**

Redbench does NOT execute queries against your database to learn from it. It reads the trace to answer two questions:

-   What query shapes exist? (num\_joins, num\_scans, query\_type, read\_table\_ids)
-   How often does each shape repeat? (arrival\_timestamp, feature\_fingerprint)

It then generates SQL that has the same structural distribution. The trace must follow the Redset schema exactly.

## **1.3 Key Config Parameters**

| **Parameter** | What it does |
| --- | --- |
| **database\_name** | Matches the folder name under tmp_generation/. Must equal your schema name. |
| **raw\_database\_tables** | Path to your CSV files. Each file must be named {tablename}.csv. |
| **schema\_augmentation\_factor** | Redbench duplicates your tables N times (e.g. 2 = region_0, region_1). Needed so it can generate INSERT/UPDATE across "universes". |
| **start\_date / end\_date** | Date window to filter trace rows. Must overlap with arrival_timestamp in your parquet. |
| **limit\_redset\_rows\_read** | Cap on trace rows loaded. 1000 is fast for testing; remove/raise for production. |
| **min\_table\_scan\_selectivity** | Minimum fraction of rows a scan predicate must touch (0.05 = 5%). |
| **start\_mapping\_largest\_table** | Map the largest trace table ID to the largest physical table first. |
| **force\_setup\_creation** | Set true to re-run normalisation even if cached files exist. |
| **force\_workload\_creation** | Set true to re-run query generation even if workload.csv exists. |

# **2\. The Three Input Files You Must Provide**

## **2.1 The Parquet Trace**

This replaces the real Redset parquet. For a custom database you synthesise it from your own query plans or execution logs. Every column in the Redset schema must be present.

**Critical columns actually read by Redbench:**

-   instance\_id, database\_id — must match --instance\_id and --database\_id flags
-   arrival\_timestamp — must be within start\_date/end\_date in config
-   query\_type — must be "select", "insert", "update", or "delete"
-   num\_joins, num\_scans, num\_aggregations — extracted from your query plans
-   read\_table\_ids, write\_table\_ids — comma-separated integer IDs; must be VARCHAR not NULL/integer
-   mbytes\_scanned — used for table size mapping; must be float, never NULL
-   was\_aborted, was\_cached — integers (0/1)
-   feature\_fingerprint — string hash; used to group repeated queries

**Filename rule:** the parquet filename MUST contain the word "provisioned" or "serverless". Redbench calls determine\_redset\_dataset\_type() which raises a ValueError if neither word appears.

\# CORRECT

tpch\_provisioned.parquet

mytrace\_serverless.parquet

\# WRONG - will crash with ValueError

tpch.parquet

my\_trace.parquet

## **2.2 schema.json**

Lives at output/tmp\_generation/{database\_name}/schema.json . Describes table columns, data types, primary keys, join relationships, and CSV parsing options.

{

"name": "mydb", <- must match database\_name in config

"csv\_kwargs": {

"sep": "|", <- your delimiter

"header": 0 <- 0 = first row is header

},

"relationships": \[ <- \[table1, \[col1\], table2, \[col2\]\]

\["orders", \["o\_custkey"\], "customer", \["c\_custkey"\]\]

\],

"table\_col\_info": {

"customer": {

"c\_custkey": { "type": "integer", "pk": true },

"c\_name": { "type": "varchar(25)", "pk": false }

}

}

}

header: 0 means "row 0 is the header". Your CSV files must have a header row with exact column names matching table\_col\_info keys.

## **2.3 postgres.sql**

Lives at output/tmp\_generation/{database\_name}/postgres.sql . Standard DDL. Two hard requirements from Redbench:

-   Every CREATE TABLE must be preceded by DROP TABLE IF EXISTS {tablename};
-   The opening parenthesis ( must be on a new line after the table name — not on the same line as CREATE TABLE

\-- CORRECT format

DROP TABLE IF EXISTS customer;

CREATE TABLE customer

(

c\_custkey integer NOT NULL,

c\_name varchar(25) NOT NULL

);

\-- WRONG: ( on same line as CREATE TABLE

CREATE TABLE customer ( <- Redbench rename regex fails here

c\_custkey integer NOT NULL

);

Why? prepare\_and\_scale.py renames tables to customer\_0, customer\_1 etc. by matching the exact string "CREATE TABLE customer\\n". If ( is on the same line, the match fails silently and all versions get the same name.

# **3\. Every Error We Hit and Why It Happened**

| **Error** | **Root Cause & Fix** |
| --- | --- |
| KeyError: 'r_regionkey' | TPC-H dbgen files have a trailing \| on every row, causing pandas to read N+1 columns with integer names (0,1,2...). The dtype dict has named keys so column mapping fails. Fix: strip trailing \| and add header rows to CSV files. |
| ValueError: Unable to parse string 'c_custkey' at position 0 | sed -i '1s/^/header\n/' ran twice because the CSV pipeline was re-run after partial fix. The header row was inserted twice. Fix: restore from original .tbl.csv files and use a Python script to prepend headers exactly once. |
| NotImplementedError: Expecting that DROP TABLE IF EXISTS is in the schema | Our postgres.sql had no DROP TABLE IF EXISTS statements. Redbench uses this as a string separator to split the schema into per-table blocks. Fix: add DROP TABLE IF EXISTS tablename; before each CREATE TABLE. |
| CatalogException: Table supplier_1 does not exist | The opening ( was on the same line as CREATE TABLE. Redbench checks for 'CREATE TABLE supplier\n' (newline after name) to rename tables. With ( on the same line, the rename silently fails — schema_augmented_x2.sql had duplicate originals not versioned copies. Fix: move ( to its own line. |
| BinderException: No function matches string_split(INTEGER, STRING_LITERAL) | write_table_ids column was stored as pyarrow null/integer type instead of string in the parquet. DuckDB tried to call string_split() on an integer column. Fix: explicitly cast all nullable string columns (write_table_ids, read_table_ids, cache_source_query_id) to pa.string() when writing the parquet. |

# **4\. Final Error-Free Pipeline for Any Database**

Follow these steps exactly for any new database. Replace mydb with your database name throughout.

## **Step 0: Prerequisites**

-   Redbench repo cloned, uv synced, venv activated
-   Your table data as CSV files with | separator and header row
-   Python 3.11+, pyarrow, pandas installed in your env

## **Step 1: Prepare Your CSV Files**

Each file must be named exactly {tablename}.csv (no .tbl, no extra extensions), have a header row, and no trailing | at end of lines.

\# Create a clean directory for renamed/fixed CSVs

mkdir -p ~/myproject/data/clean

\# If your files have trailing pipes (TPC-H dbgen output):

\# Use the Python script below instead of sed

python3 << 'EOF'

import os

headers = {

"customer": "col1|col2|col3", # pipe-separated column names

"orders": "col1|col2|col3",

\# ... one entry per table

}

src\_dir = os.path.expanduser("~/myproject/data/raw")

dst\_dir = os.path.expanduser("~/myproject/data/clean")

os.makedirs(dst\_dir, exist\_ok=True)

for table, header in headers.items():

src = os.path.join(src\_dir, f"{table}.tbl.csv") # adjust extension

dst = os.path.join(dst\_dir, f"{table}.csv")

with open(src) as f:

lines = f.readlines()

lines = \[l.rstrip("|\\n") + "\\n" for l in lines\] # strip trailing pipe

lines = \[header + "\\n"\] + lines # prepend header

with open(dst, "w") as f:

f.writelines(lines)

print(f"{table}: {len(lines)-1} rows")

EOF

## **Step 2: Create schema.json**

Save as ~/Redbench/output/tmp\_generation/mydb/schema.json .

mkdir -p ~/Redbench/output/tmp\_generation/mydb

cat > ~/Redbench/output/tmp\_generation/mydb/schema.json << 'EOF'

{

"name": "mydb",

"csv\_kwargs": { "sep": "|", "header": 0 },

"relationships": \[

\["child\_table", \["fk\_col"\], "parent\_table", \["pk\_col"\]\]

\],

"table\_col\_info": {

"mytable": {

"id": { "type": "integer", "pk": true },

"name": { "type": "varchar(50)", "pk": false }

}

}

}

EOF

Supported types: integer, bigint, decimal(p,s), float, double, char(n), varchar(n), date, timestamp, boolean

## **Step 3: Create postgres.sql**

Save as ~/Redbench/output/tmp\_generation/mydb/postgres.sql . Remember: DROP TABLE IF EXISTS before each table, and ( on its own line.

cat > ~/Redbench/output/tmp\_generation/mydb/postgres.sql << 'EOF'

DROP TABLE IF EXISTS parent\_table;

CREATE TABLE parent\_table

(

pk\_col integer NOT NULL,

name\_col varchar(50) NOT NULL

);

DROP TABLE IF EXISTS child\_table;

CREATE TABLE child\_table

(

id integer NOT NULL,

fk\_col integer NOT NULL

);

EOF

## **Step 4: Generate the Parquet Trace**

Run this Python script. Edit the TABLE\_IDS and plan data sections for your database.

\# generate\_trace.py

import pandas as pd, pyarrow as pa, pyarrow.parquet as pq

from datetime import datetime, timedelta

import random; random.seed(42)

\# Map your table names to stable integer IDs

TABLE\_IDS = { "mytable": 101, "other": 102 }

\# Each entry = one query shape from your workload

QUERIES = \[

{ "qid": 1, "joins": 1, "scans": 2, "aggs": 1,

"tables": \["mytable","other"\], "cost": 50000 },

\# ... one entry per distinct query

\]

INSTANCE\_ID, DATABASE\_ID = 1, 1

rows = \[\]

base\_ts = datetime(2024, 1, 1, 8, 0, 0)

for i, q in enumerate(QUERIES):

read\_ids = ",".join(str(TABLE\_IDS\[t\]) for t in q\["tables"\])

for rep in range(3): # repeat each query 3x

rows.append({

"instance\_id": INSTANCE\_ID,

"cluster\_size": 1, "user\_id": 1,

"database\_id": DATABASE\_ID,

"query\_id": q\["qid"\] \* 10 + rep,

"arrival\_timestamp": base\_ts + timedelta(seconds=(i\*3+rep)\*30),

"compile\_duration\_ms": random.randint(5,50),

"queue\_duration\_ms": 0,

"execution\_duration\_ms": max(10, q\["cost"\]//100),

"feature\_fingerprint": f"q{q\['qid'\]:03d}",

"was\_aborted": 0, "was\_cached": 0,

"cache\_source\_query\_id": None,

"query\_type": "select",

"num\_permanent\_tables\_accessed": len(q\["tables"\]),

"num\_external\_tables\_accessed": 0,

"num\_system\_tables\_accessed": 0,

"read\_table\_ids": read\_ids,

"write\_table\_ids": None,

"mbytes\_scanned": float(max(1, q\["cost"\]//1000)),

"mbytes\_spilled": 0.0,

"num\_joins": q\["joins"\],

"num\_scans": q\["scans"\],

"num\_aggregations": q\["aggs"\],

})

df = pd.DataFrame(rows)

df\["arrival\_timestamp"\] = pd.to\_datetime(df\["arrival\_timestamp"\])

\# CRITICAL: force string type on all nullable string columns

for col in \["write\_table\_ids","read\_table\_ids","cache\_source\_query\_id"\]:

df\[col\] = df\[col\].astype(pd.StringDtype())

schema = pa.schema(\[

("instance\_id", pa.int64()), ("cluster\_size", pa.int64()),

("user\_id", pa.int64()), ("database\_id", pa.int64()),

("query\_id", pa.int64()),

("arrival\_timestamp", pa.timestamp("us")),

("compile\_duration\_ms", pa.int64()),

("queue\_duration\_ms", pa.int64()),

("execution\_duration\_ms", pa.int64()),

("feature\_fingerprint", pa.string()),

("was\_aborted", pa.int64()), ("was\_cached", pa.int64()),

("cache\_source\_query\_id", pa.string()),

("query\_type", pa.string()),

("num\_permanent\_tables\_accessed", pa.int64()),

("num\_external\_tables\_accessed", pa.int64()),

("num\_system\_tables\_accessed", pa.int64()),

("read\_table\_ids", pa.string()),

("write\_table\_ids", pa.string()),

("mbytes\_scanned", pa.float64()),

("mbytes\_spilled", pa.float64()),

("num\_joins", pa.int64()), ("num\_scans", pa.int64()),

("num\_aggregations", pa.int64()),

\])

\# filename MUST contain "provisioned" or "serverless"

pq.write\_table(pa.Table.from\_pandas(df, schema=schema),

"mydb\_provisioned.parquet")

print("done")

## **Step 5: Create the Generation Config**

Save as ~/Redbench/src/redbench/generation/config/mydb.json .

{

"raw\_database\_tables": "/home/youruser/myproject/data/clean",

"database\_name": "mydb",

"schema\_augmentation\_factor": 2,

"repetition\_exponent": 1,

"seed": 3123,

"enable\_random\_table\_ids": false,

"enable\_random\_databases": false,

"add\_conflict\_logic": true,

"apply\_sampling": false,

"max\_size\_qig": 100000,

"deactivate\_repeating\_inserts": true,

"force\_setup\_creation": false,

"force\_workload\_creation": false,

"start\_date": "2024-01-01 00:00:00",

"end\_date": "2024-12-31 00:00:00",

"limit\_redset\_rows\_read": 1000,

"include\_copy": false,

"include\_analyze": false,

"interpret\_deviating\_mbytes\_as\_structural\_repetition": false,

"redset\_exclude\_tables\_never\_read": false,

"validate\_query\_produces\_rows": false,

"min\_table\_scan\_selectivity": 0.05,

"start\_mapping\_largest\_table": true

}

## **Step 6: Place the Parquet and Run**

cp mydb\_provisioned.parquet ~/Redbench/data/

cd ~/Redbench

python src/redbench/run.py \\

\--redset\_path data/mydb\_provisioned.parquet \\

\--output\_dir output \\

\--generation\_strategy generation \\

\--config\_path\_generation src/redbench/generation/config/mydb.json \\

\--instance\_id 1 \\

\--database\_id 1

## **Step 7: Find Your Output**

ls output/generated\_workloads/mydb/provisioned/cluster\_1/database\_1/

\# -> generation\_<hash>/

cat output/generated\_workloads/mydb/provisioned/cluster\_1/database\_1/generation\_\*/workload.csv | head -5

## **Cache Invalidation Cheatsheet**

When something goes wrong mid-run, know what to delete:

| **What changed** | **What to delete** |
| --- | --- |
| CSV files / schema.json | tables_normalized/, column_statistics.json, db_original.duckdb |
| postgres.sql | schema_augmented_x2.sql, db_augmented_x2.duckdb |
| Parquet / config only | Nothing — all intermediate files can be reused |
| Nuclear option / fresh start | rm -rf output/tmp_generation/mydb/ |

*Generated from session debugging TPC-H on Redbench — IIT Hyderabad*