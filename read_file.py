import os
import pandas as pd
import re
import sqlite3

def read_sql_file(path: str) -> dict:

    with open(path, "rb") as f:
        raw = f.read()

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        script = raw.decode("utf-16")
    elif raw.startswith(b"\xef\xbb\xbf"):
        script = raw.decode("utf-8-sig")
    else:
        try:
            script = raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                script = raw.decode("utf-16")
            except UnicodeDecodeError:
                script = raw.decode("latin-1")

    script = script.replace("\x00", "")

    # --- Limpieza T-SQL -> SQLite ---
    script = re.sub(r"(?im)^\s*GO\s*$", ";", script)
    script = re.sub(r"(?im)^\s*USE\s+\w+\s*;?\s*$", "", script)
    script = re.sub(r"(?im)^\s*SET\s+.*?;?\s*$", "", script)
    script = re.sub(r"\[(\w+)\]", r"\1", script)
    script = re.sub(r"(?i)IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)", "", script)
    script = re.sub(r"(?i)\bNVARCHAR\b", "VARCHAR", script)
    script = re.sub(r"(?i)\bDATETIME2?\b", "TEXT", script)
    script = re.sub(r"(?i)\bBIT\b", "INTEGER", script)
    script = re.sub(r"(?i)\bUNIQUEIDENTIFIER\b", "TEXT", script)
    script = re.sub(r"(?i)CREATE\s+SCHEMA\s+\w+\s*;", "", script)
    script = re.sub(r";\s*;", ";", script)

    script = _add_missing_semicolons(script)   # <- NUEVO: arregla el caso de tu script

    conn = sqlite3.connect(":memory:")
    conn.executescript(script)

    tables = {}
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for (tname,) in cur.fetchall():
        df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
        tables[tname] = df.astype(str)

    conn.close()
    return tables


def _add_missing_semicolons(script: str) -> str:
    """Inserta ';' antes de cada nueva sentencia si el bloque anterior no la tiene."""
    keywords = (
        r"(CREATE\s+TABLE|CREATE\s+VIEW|CREATE\s+(?:UNIQUE\s+)?INDEX|"
        r"INSERT\s+INTO|ALTER\s+TABLE|DROP\s+TABLE|DROP\s+VIEW|"
        r"UPDATE|DELETE\s+FROM)"
    )
    pattern = re.compile(keywords, re.IGNORECASE)

    result = []
    last_end = 0
    for m in pattern.finditer(script):
        start = m.start()
        before = script[last_end:start]
        stripped = before.rstrip()
        if stripped == "" or stripped.endswith(";"):
            result.append(before)
        else:
            idx = len(stripped)
            result.append(before[:idx] + ";" + before[idx:])
        last_end = start
    result.append(script[last_end:])
    return "".join(result)