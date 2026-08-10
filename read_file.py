import os
import pandas as pd
import re
import sqlite3

def read_sql_file(path: str) -> dict:

    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        script = f.read()

    script = re.sub(r"(?im)^\s*GO\s*$", "", script)                    
    script = re.sub(r"\[(\w+)\]", r"\1", script)                       
    script = re.sub(r"(?i)IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)", "", script)
    script = re.sub(r"(?i)\bNVARCHAR\b", "VARCHAR", script)
    script = re.sub(r"(?i)\bDATETIME2?\b", "TEXT", script)
    script = re.sub(r"(?i)\bBIT\b", "INTEGER", script)
    script = re.sub(r"(?i)\bUNIQUEIDENTIFIER\b", "TEXT", script)
    script = re.sub(r"(?i)CREATE\s+SCHEMA\s+\w+\s*;", "", script)

    conn = sqlite3.connect(":memory:")
    conn.executescript(script)

    tables = {}
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for (tname,) in cur.fetchall():
        df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
        tables[tname] = df.astype(str)

    conn.close()
    return tables