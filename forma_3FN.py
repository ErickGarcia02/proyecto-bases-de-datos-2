import pandas as pd

def transformar_3fn(tablas_2fn):
    tablas_3fn = {}

    for nombre_tabla, info in tablas_2fn.items():
        df_resultado = info['tabla'].copy()
        df_original = info['tabla'].copy()
        pk = info['PK']
        columnas_candidatas = [c for c in df_original.columns if c != pk]
        
        # Guardaremos qué columnas son "determinantes" para no borrarlas
        determinantes_a_mantener = set()
        columnas_a_eliminar = set()

        # Detección de dependencias
        for col_a in columnas_candidatas:
            for col_b in columnas_candidatas:
                if col_a == col_b: continue
                
                # Identificar si A determina a B
                if df_original.groupby(col_a)[col_b].nunique().max() == 1:
                    # Si A se repite, es una tabla de catálogo
                    if df_original[col_a].nunique() < len(df_original):
                        # B depende de A -> B debe irse, A se queda como FK
                        if col_b not in determinantes_a_mantener:
                            columnas_a_eliminar.add(col_b)
                            determinantes_a_mantener.add(col_a)

        for det in determinantes_a_mantener:
            # Sacamos las columnas que dependen de este determinante
            deps = [c for c in columnas_a_eliminar if df_original.groupby(det)[c].nunique().max() == 1]
            if deps:
                # Crear la tabla de catálogo
                nueva_tabla_df = df_original[[det] + deps].drop_duplicates().reset_index(drop=True)
                tablas_3fn[f"Cat_{nombre_tabla}_{det}"] = {
                    "tabla": nueva_tabla_df,
                    "PK": det,
                    "FK": []
                }
                # Borrar de la principal
                for d in deps:
                    if d in df_resultado.columns:
                        df_resultado = df_resultado.drop(columns=[d])

        # Guardar la original con sus FKs
        tablas_3fn[nombre_tabla] = {
            "tabla": df_resultado,
            "PK": pk,
            "FK": list(determinantes_a_mantener)
        }

    return tablas_3fn