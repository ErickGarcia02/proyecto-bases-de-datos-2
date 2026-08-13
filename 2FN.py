import pandas as pd

#tablas_1fn es un diccionario de tablas {nombre_tabla: DataFrame}
def transformar_a_2fn(tablas_1fn):
    """
    Convierte una o mas tablas 1fn en 2fn
    """

    #Lo que debe hacer esta funcion:
    
    #recorrer cada tabla en tablas_1fn y crear un nuevo diccionario
    #{nombre_tabla: {tabla: DataFrame, PK: nombre_columna, FK: nombres_columnas[]}}

    #PK se identificara si el nombre de la columna contiene "codigo" o "ID", si hay mas de una, la primera sera PK
    #y las siguientes FK
   
    #Si una columna es PK y se repite en varias tablas como PK, solo la primera sera PK, y en las tablas subsecuentes se creara
    #una nueva columna "Codigo<nombre de tabla>" como PK y la PK original se volvera FK

    #El nombre de una nueva tabla se basa en el nombre de la PK si esta era una FK en la tabla anterior, o en una combinacion de
    #las columnas dependientes si la PK se debe crear
    
    #Si hay columnas a la derecha de una PK o FK dependen de dicha PK o FK si estan a izquierda de otra
    #FK, no son FK o no hay mas FK a la derecha

    #Si se encuentran columnas que dependen de una FK, crear una nueva tabla con FK como PK y sus columnas dependientes, y eliminar
    #las columnas dependientes de la tabla original pero dejar la FK

    tablas_2fn = {}
    pks_usadas = {}  # nombre_columna_pk -> nombre_tabla que ya la usa como PK

    # 1) Detectar PK/FK de cada tabla ("codigo"/"id" en el nombre de columna)
    for nombre_tabla, df in tablas_1fn.items():
        df = df.copy()
        columnas_clave = [c for c in df.columns if "codigo" in c.lower() or "id" in c.lower()]

        pk = columnas_clave[0] if columnas_clave else df.columns[0]
        fk = columnas_clave[1:]

        # Si la PK ya pertenece a otra tabla, se crea una PK propia y la original pasa a FK
        if pk in pks_usadas:
            nueva_pk = f"Codigo{nombre_tabla}"
            df.insert(0, nueva_pk, range(1, len(df) + 1))
            fk = [pk] + fk
            pk = nueva_pk
        else:
            pks_usadas[pk] = nombre_tabla

        tablas_2fn[nombre_tabla] = {"tabla": df, "PK": pk, "FK": fk}

    # 2) Separar columnas que dependen solo de una FK (dependencia parcial)
    for nombre_tabla, info in list(tablas_2fn.items()):
        df = info["tabla"]
        claves = [info["PK"]] + info["FK"]

        dependientes_por_fk = {fk: [] for fk in info["FK"]}
        clave_actual = info["PK"]
        for col in df.columns:
            if col in claves:
                clave_actual = col
            elif clave_actual in dependientes_por_fk:
                dependientes_por_fk[clave_actual].append(col)

        for fk, columnas_dependientes in dependientes_por_fk.items():
            if not columnas_dependientes:
                continue

            # El nombre se basa en la PK (que ya era FK en la tabla original); si no
            # hubiera FK de la cual tomar el nombre, se usan las columnas dependientes
            if fk:
                nombre_nueva_tabla = f"Tabla_{fk}"
            else:
                nombre_nueva_tabla = f"Tabla_{'_'.join(columnas_dependientes)}"

            df_nueva = df[[fk] + columnas_dependientes].drop_duplicates().reset_index(drop=True)
            tablas_2fn[nombre_nueva_tabla] = {"tabla": df_nueva, "PK": fk, "FK": []}

            df = df.drop(columns=columnas_dependientes)

        info["tabla"] = df

    return tablas_2fn
