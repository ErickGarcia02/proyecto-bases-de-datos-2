import pandas as pd

def transformar_a_2fn(tablas_1fn):
    tablas_2fn = {}

    for nombre_tabla, df in tablas_1fn.items():
        df = df.copy()

        if "Base" in nombre_tabla:
            pk_base = df.columns[0]
            nombre_limpio = nombre_tabla.replace("_1FN", "")
            tablas_2fn[f"{nombre_limpio}_2FN"] = {
                "tabla": df,
                "PK": pk_base,
                "FK": []
            }
        
        else:
            # Identificar la columna que viene de la tabla base como FK
            fk_heredada = df.columns[0]
            
            # Limpiar el nombre para la nueva PK
            nombre_elemento = nombre_tabla.replace("Tabla_", "").replace("_1FN", "")
            nueva_pk = f"Codigo_{nombre_elemento}"
            
            # Agregar la nueva PK subrogada (autonumérica) al INICIO del dataframe
            df.insert(0, nueva_pk, range(1, len(df) + 1))
            
            tablas_2fn[f"Tabla_{nombre_elemento}_2FN"] = {
                "tabla": df,
                "PK": nueva_pk,
                "FK": [fk_heredada]
            }

    return tablas_2fn