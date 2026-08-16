import pandas as pd


def transformar_a_2fn(tablas_1fn):
    """
    Convierte una o mas tablas 1fn en 2fn
    """


    tablas_2fn = {}

    for nombre_tabla, df in tablas_1fn.items():
        df = df.copy()
        nombre_limpio = nombre_tabla.replace("_1FN", "")

        # --- TABLA BASE ---
        if "Base" in nombre_tabla:
           
            pk = df.columns[0]
            
            tablas_2fn[f"{nombre_limpio}_2FN"] = {
                "tabla": df,
                "PK": pk,
                "FK": []
            }

       
        else:
           
            pk_compuesta = list(df.columns)
            
          
            fk_heredada = df.columns[0]
            
            tablas_2fn[f"{nombre_limpio}_2FN"] = {
                "tabla": df,
                "PK": " + ".join(pk_compuesta),
                "FK": [fk_heredada]
            }

    return tablas_2fn