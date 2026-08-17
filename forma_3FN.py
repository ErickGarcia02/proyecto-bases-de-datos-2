import pandas as pd

def transformar_3fn(tablas_2fn):
    tablas_3fn = {}
    catalogos_por_determinante = {}
    conflictos_detectados = []

    for nombre_tabla, info in tablas_2fn.items():
        df_resultado = info['tabla'].copy()
        df_original = info['tabla'].copy()
        pk = info['PK']
        pk_cols = [c.strip() for c in pk.split(" + ")]
        columnas_candidatas = [c for c in df_original.columns if c not in pk_cols]

       
        dependencias = {}
        for col_a in columnas_candidatas:
            if df_original[col_a].nunique() >= len(df_original):
                continue
            for col_b in columnas_candidatas:
                if col_a == col_b:
                    continue
                sub = df_original[[col_a, col_b]].dropna()
                if sub.empty:
                    continue
                if sub.groupby(col_a)[col_b].nunique().max() == 1:
                    dependencias.setdefault(col_a, set()).add(col_b)

      
        determinantes_finales = {}
        columnas_procesadas = set()

        for col_a in columnas_candidatas:
            if col_a in columnas_procesadas or col_a not in dependencias:
                continue

            grupo_mutuo = {col_a}
            for col_b in dependencias.get(col_a, set()):
                if col_b in dependencias and col_a in dependencias[col_b]:
                    grupo_mutuo.add(col_b)

            canonico = sorted(grupo_mutuo)[0]
            otros_del_grupo = grupo_mutuo - {canonico}

            dependientes = set()
            for miembro in grupo_mutuo:
                dependientes |= dependencias.get(miembro, set())
            dependientes -= grupo_mutuo
            dependientes |= otros_del_grupo

            determinantes_finales[canonico] = dependientes
            columnas_procesadas |= grupo_mutuo

        
        dependientes_ya_asignados = set()

        for det, dependientes in determinantes_finales.items():
            deps = [d for d in dependientes if d not in dependientes_ya_asignados and d != det]
            if not deps:
                continue

            nueva_tabla_df = df_original[[det] + deps].drop_duplicates(subset=[det]).reset_index(drop=True)

            if det in catalogos_por_determinante:
                nombre_catalogo = catalogos_por_determinante[det]
                catalogo_existente = tablas_3fn[nombre_catalogo]["tabla"]
                columnas_comunes = [c for c in deps if c in catalogo_existente.columns]
                columnas_nuevas = [c for c in deps if c not in catalogo_existente.columns]

                conflicto_en_esta_tabla = False
                for col_dep in columnas_comunes:
                    comparacion = nueva_tabla_df[[det, col_dep]].merge(
                        catalogo_existente[[det, col_dep]], on=det, suffixes=("_nuevo", "_existente")
                    )
                    discrepancias = comparacion[
                        comparacion[f"{col_dep}_nuevo"] != comparacion[f"{col_dep}_existente"]
                    ]
                    if not discrepancias.empty:
                        conflicto_en_esta_tabla = True
                        for _, fila in discrepancias.iterrows():
                            conflictos_detectados.append(
                                f"Conflicto en '{det}'={fila[det]}: '{col_dep}' vale "
                                f"'{fila[f'{col_dep}_nuevo']}' en '{nombre_tabla}' pero "
                                f"'{fila[f'{col_dep}_existente']}' en el catálogo '{nombre_catalogo}'."
                            )

                if conflicto_en_esta_tabla:
                    continue

                if columnas_nuevas:
                    catalogo_existente = catalogo_existente.merge(
                        nueva_tabla_df[[det] + columnas_nuevas], on=det, how="outer"
                    )
                else:
                    catalogo_existente = pd.concat([catalogo_existente, nueva_tabla_df], ignore_index=True)

                catalogo_existente = catalogo_existente.drop_duplicates(subset=[det]).reset_index(drop=True)
                tablas_3fn[nombre_catalogo]["tabla"] = catalogo_existente
            else:
                nombre_catalogo = f"Cat_{det}"
                catalogos_por_determinante[det] = nombre_catalogo
                tablas_3fn[nombre_catalogo] = {"tabla": nueva_tabla_df, "PK": det, "FK": []}

            for d in deps:
                dependientes_ya_asignados.add(d)
                if d in df_resultado.columns:
                    df_resultado = df_resultado.drop(columns=[d])

        fk_original = [f for f in info['FK'] if f in df_resultado.columns]
        fk_nuevas = [d for d in determinantes_finales.keys() if d in df_resultado.columns and d not in pk_cols]
        fk_final = list(dict.fromkeys(fk_original + fk_nuevas))

        tablas_3fn[nombre_tabla.replace("_2FN", "_3FN")] = {
            "tabla": df_resultado,
            "PK": pk,
            "FK": fk_final
        }

    return tablas_3fn, conflictos_detectados