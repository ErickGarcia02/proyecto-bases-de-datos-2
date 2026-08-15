import pandas as pd

def transformar_3fn(tablas_2fn):
    tablas_3fn = {}

    for nombre_tabla, info in tablas_2fn.items():
        df_resultado = info['tabla'].copy()
        df_original = info['tabla'].copy()
        pk = info['PK']
        
        # 1. Recuperamos las Claves Foráneas que ya traía la tabla desde la 2FN
        fks_heredadas = info.get('FK', [])
        
        # Proteger pk compuesta si la hay
        columnas_pk = [c.strip() for c in str(pk).split('+')]
        columnas_candidatas = [c for c in df_original.columns if c not in columnas_pk]
        
        # Guardaremos qué columnas son "determinantes" para no borrarlas
        determinantes_a_mantener = set()
        columnas_a_eliminar = set()

        # Detección de dependencias
        for col_a in columnas_candidatas:
            
            #Un catálogo debe tener como llave un Código o ID
            if "codigo" not in col_a.lower() and "id" not in col_a.lower() and "numero" not in col_a.lower():
                continue
                
            for col_b in columnas_candidatas:
                if col_a == col_b: continue
                
                # Identificar si A determina a B
                if df_original.groupby(col_a)[col_b].nunique(dropna=True).max() == 1:
                    # Si A se repite, es una tabla de catálogo
                    if df_original[col_a].nunique() < len(df_original):
                        # B depende de A -> B debe irse, A se queda como FK
                        if col_b not in determinantes_a_mantener:
                            columnas_a_eliminar.add(col_b)
                            determinantes_a_mantener.add(col_a)

        for det in determinantes_a_mantener:
            # Sacamos las columnas que dependen de este determinante
            deps = [c for c in columnas_a_eliminar if c != det and df_original.groupby(det)[c].nunique(dropna=True).max() == 1]
            
            if deps:
                # Crear la tabla de catálogo
                nueva_tabla_df = df_original[[det] + deps].drop_duplicates().reset_index(drop=True)
                
                # Le asignamos _3FN a los catálogos nuevos
                nombre_limpio = nombre_tabla.replace("_2FN", "").replace("_1FN", "")
                tablas_3fn[f"Cat_{nombre_limpio}_{det}_3FN"] = {
                    "tabla": nueva_tabla_df,
                    "PK": det,
                    "FK": []
                }
                
                # Borrar de la principal
                for d in deps:
                    if d in df_resultado.columns:
                        df_resultado = df_resultado.drop(columns=[d])

        # 2. Reemplazamos "_2FN" por "_3FN" para el título de la tabla modificada
        nombre_final = nombre_tabla.replace("_2FN", "") + "_3FN"

        # 3. Unimos las FKs viejas con las nuevas que detectó la 3FN sin duplicados
        fks_finales = list(set(fks_heredadas) | determinantes_a_mantener)

        # Guardar la original con sus FKs actualizados
        tablas_3fn[nombre_final] = {
            "tabla": df_resultado,
            "PK": pk,
            "FK": fks_finales
        }

    return tablas_3fn