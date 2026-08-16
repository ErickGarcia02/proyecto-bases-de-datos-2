import pandas as pd

def _tipo_sql(columna):
    """Infiere el tipo SQL a partir del dtype de una columna de pandas."""
    tipo_pd = str(columna.dtype)
    if "int" in tipo_pd:
        return "INT"
    elif "float" in tipo_pd:
        return "FLOAT"
    else:
        return "VARCHAR(255)"


def _valor_sql(valor):
    """Convierte un valor de pandas al literal SQL correspondiente."""
    if pd.isna(valor):
        return "NULL"
    if isinstance(valor, str):
        texto = valor.replace("'", "''")
        return f"'{texto}'"
    return str(valor)


def generar_script_sql(tablas_normalizadas, nombre_bd="BaseDeDatosNormalizada"):
    """
    Recibe el diccionario resultante de transformar_3fn (o de cualquier fase,
    ya que todas usan el mismo formato):
    {nombre_tabla: {"tabla": DataFrame, "PK": str, "FK": [str, ...]}}

    Devuelve un string con el script SQL completo (DROP + CREATE + INSERT).
    """

    lineas = [
        f"-- Base de datos normalizada (3FN): {nombre_bd}",
        "",
    ]


    mapa_pk_simple = {}
    for nombre_tabla, info in tablas_normalizadas.items():
        pk = info["PK"]
        if " + " not in pk:
            mapa_pk_simple[pk] = nombre_tabla

   
    orden_tablas = sorted(
        tablas_normalizadas.items(),
        key=lambda item: len(item[1]["FK"])
    )

    # --- CREATE TABLE ---
    for nombre_tabla, info in orden_tablas:
        df = info["tabla"]
        pk_cols = [c.strip() for c in info["PK"].split(" + ")]
        fk_cols = info["FK"]

        lineas.append(f"DROP TABLE IF EXISTS {nombre_tabla};")
        lineas.append(f"CREATE TABLE {nombre_tabla} (")

        definiciones = [f"    {col} {_tipo_sql(df[col])}" for col in df.columns]
        definiciones.append(f"    PRIMARY KEY ({', '.join(pk_cols)})")

        for fk in fk_cols:
            tabla_ref = mapa_pk_simple.get(fk)
            if tabla_ref and tabla_ref != nombre_tabla:
                definiciones.append(
                    f"    FOREIGN KEY ({fk}) REFERENCES {tabla_ref}({fk})"
                )

        lineas.append(",\n".join(definiciones))
        lineas.append(");")
        lineas.append("")

    # --- INSERT INTO ---
    for nombre_tabla, info in orden_tablas:
        df = info["tabla"]
        columnas = ", ".join(df.columns)

        for _, fila in df.iterrows():
            valores = ", ".join(_valor_sql(v) for v in fila)
            lineas.append(f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({valores});")

        lineas.append("")

    return "\n".join(lineas)