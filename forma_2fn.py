import pandas as pd

def transformar_a_2fn(tablas_1fn):
    """
    Convierte una o mas tablas 1fn en 2fn
    - Asigna PKs Subrogadas a las tablas multivalor (Ej. Telefonos, Proyectos).
    - La tabla Base pasa intacta declarando su PK.
    """
    tablas_2fn = {}

    for nombre_tabla, df in tablas_1fn.items():
        df = df.copy()
        nombre_limpio = nombre_tabla.replace("_1FN", "")

        # TABLA BASE
        if "Base" in nombre_tabla:
            # En la tabla base, la PK es simple (la primera columna, Ej. CodigoEmpleado)
            pk = df.columns[0]
            
            tablas_2fn[f"{nombre_limpio}_2FN"] = {
                "tabla": df,
                "PK": pk,
                "FK": []
            }

        #TABLAS MULTIVALOR (Teléfonos, Proyectos)
        else:
            # Identificamos qué columna es la Foránea y cuál es el Dato
            fk_heredada = df.columns[0]
            columna_dato = df.columns[1]
            
            # Nombre de la nueva PK inventada (Subrogada)
            nombre_elemento = nombre_tabla.replace("Tabla_", "").replace("_1FN", "")
            nueva_pk = f"Codigo_{nombre_elemento}"
            
            # Creamos un dataframe limpio desde cero con las 3 columnas
            df_limpio = pd.DataFrame({
                nueva_pk: range(1, len(df) + 1),
                fk_heredada: df[fk_heredada].values,
                columna_dato: df[columna_dato].values
            })
            
            tablas_2fn[f"Tabla_{nombre_elemento}_2FN"] = {
                "tabla": df_limpio,
                "PK": nueva_pk,
                "FK": [fk_heredada]
            }

    return tablas_2fn