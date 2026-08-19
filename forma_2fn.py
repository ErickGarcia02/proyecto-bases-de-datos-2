import pandas as pd

def transformar_a_2fn(tablas_1fn):
    """
    Convierte las tablas 1FN en 2FN.
    Añade una llave subrogada (ID auto-incremental) a las tablas extraídas 
    para que funcione como su propia PK oficial, y define la PK original como llave foránea (FK).
    """
    tablas_2fn = {}

    # 1. Identificar la tabla base para saber cuál es la llave original
    nombre_base = next((nombre for nombre in tablas_1fn.keys() if "Base" in nombre), None)
    if not nombre_base:
        nombre_base = list(tablas_1fn.keys())[0]

    df_base = tablas_1fn[nombre_base].copy()
    pk_base = df_base.columns[0]

    # Guardar la tabla base 
    tablas_2fn[nombre_base.replace("_1FN", "_2FN")] = {
        "tabla": df_base,
        "PK": pk_base,
        "FK": []
    }

    # 2. Procesar las nuevas tablas de dependencias
    for nombre_tabla, df in tablas_1fn.items():
        if nombre_tabla == nombre_base:
            continue
        
        df_rel = df.copy()
        
        atributo = nombre_tabla.replace("Tabla_", "").replace("_1FN", "")
        nombre_pk_nueva = f"ID_{atributo}"
        
        # Insertar la nueva columna de ID 
        df_rel.insert(0, nombre_pk_nueva, range(1, len(df_rel) + 1))
        
        # La PK de la tabla base pasa a ser la FK oficial de esta nueva tabla
        fk_heredada = pk_base
        
        tablas_2fn[nombre_tabla.replace("_1FN", "_2FN")] = {
            "tabla": df_rel,
            "PK": nombre_pk_nueva,  
            "FK": [fk_heredada]  
        }

    return tablas_2fn