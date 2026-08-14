import re

import pandas as pd

#tablas_1fn es un diccionario de tablas {nombre_tabla: DataFrame}
#Se retornara otro diccionario {nombre_tabla: {tabla: DataFrame, PK: nombre_columna, FK: nombres_columnas[]}}
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
    pks_generadas = set()  # tablas a las que se les tuvo que inventar una PK

    # 1) Detectar PK/FK de cada tabla ("codigo"/"id"/"numero" en el nombre de columna)
    for nombre_tabla, df in tablas_1fn.items():
        df = df.copy()
        columnas_clave = [c for c in df.columns if "codigo" in c.lower() or "id" in c.lower() or "numero" in c.lower()]

        pk = columnas_clave[0] if columnas_clave else df.columns[0]
        fk = columnas_clave[1:]

        # Si la PK ya pertenece a otra tabla, se crea una PK propia y la original pasa a FK
        if pk in pks_usadas:
            nueva_pk = f"Codigo{nombre_tabla}"
            df.insert(0, nueva_pk, range(1, len(df) + 1))
            fk = [pk] + fk
            pk = nueva_pk
            pks_generadas.add(nombre_tabla)
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
            if col == info["PK"]:
                clave_actual = col
            elif col in info["FK"]:
                # Una FK tambien puede depender de la clave anterior (ej. CodigoDepto
                # depende de CodigoEmpleado dentro de "empleados") antes de pasar a
                # ser ella misma la clave de las columnas que le siguen
                if clave_actual in dependientes_por_fk:
                    dependientes_por_fk[clave_actual].append(col)
                clave_actual = col
            elif clave_actual in dependientes_por_fk:
                dependientes_por_fk[clave_actual].append(col)

        # Se juntan las columnas a eliminar y se quitan todas al final: una FK
        # encadenada (ej. CodigoDepto) puede necesitarse todavia como selector
        # para separar sus propias columnas dependientes antes de desaparecer
        columnas_a_eliminar = []

        for fk, columnas_dependientes in dependientes_por_fk.items():
            if not columnas_dependientes:
                continue

            # El nombre incluye la tabla de origen para que dos tablas distintas
            # con la misma FK (ej. CodigoEmpleado) no generen tablas nuevas con
            # el mismo nombre y se sobreescriban entre si
            if fk:
                nombre_nueva_tabla = f"Tabla_{nombre_tabla}_{fk}"
            else:
                nombre_nueva_tabla = f"Tabla_{nombre_tabla}_{'_'.join(columnas_dependientes)}"

            df_nueva = df[[fk] + columnas_dependientes].drop_duplicates().reset_index(drop=True)
            tablas_2fn[nombre_nueva_tabla] = {"tabla": df_nueva, "PK": fk, "FK": []}

            columnas_a_eliminar.extend(columnas_dependientes)

        df = df.drop(columns=columnas_a_eliminar)

        # Si a esta tabla se le invento una PK y no le queda ningun dato propio
        # (solo la PK inventada y columnas FK), sus FK ya quedaron como PK de las
        # tablas nuevas creadas arriba: se descarta en vez de dejar un mapeo inutil
        columnas_restantes = set(df.columns) - {info["PK"]}
        if nombre_tabla in pks_generadas and columnas_restantes <= set(info["FK"]):
            del tablas_2fn[nombre_tabla]
            continue

        info["tabla"] = df

    # 3) Renombrar las tablas nuevas (las que tienen "Tabla" en el nombre) segun
    # su segunda columna: se divide en palabras por las mayusculas y a cada
    # palabra se le agrega "es" si termina en consonante o "s" si termina en vocal
    VOCALES = "aeiouáéíóúü"
    for nombre_tabla in list(tablas_2fn.keys()):
        if "Tabla" not in nombre_tabla:
            continue

        segunda_columna = tablas_2fn[nombre_tabla]["tabla"].columns[1]
        palabras = re.findall(r"[A-ZÁÉÍÓÚÑ][^A-ZÁÉÍÓÚÑ]*", segunda_columna)

        palabras_plural = []
        for palabra in palabras:
            if palabra[-1].lower() in VOCALES:
                palabras_plural.append(palabra + "s")
            else:
                palabras_plural.append(palabra + "es")

        nombre_nuevo = "".join(palabras_plural)

        # Si ese nombre ya esta en uso (dos tablas distintas comparten el nombre
        # de su segunda columna, se le agrega la PK de esta tabla para diferenciarlas
        if nombre_nuevo in tablas_2fn:
            nombre_nuevo = f"{nombre_nuevo}_{tablas_2fn[nombre_tabla]['PK']}"

        tablas_2fn[nombre_nuevo] = tablas_2fn.pop(nombre_tabla)

    return tablas_2fn
