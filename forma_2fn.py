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

    # Si nos apegamos estrictamente a la teoria (2FN elimina dependencias parciales):
    # - La tabla base tiene una PK simple (ej. CodigoEmpleado), por lo que es imposible que tenga dependencias parciales.
    # - Las tablas extraidas en 1FN (Telefonos, Proyectos) tienen PK compuesta, pero no tienen atributos adicionales,
    #   asi que tampoco tienen dependencias parciales.
    # Por lo tanto, en la 2FN estricta las tablas pasan intactas declarando sus claves. La extraccion de catalogos
    # (como CodigoDepto -> NombreDepartamento) se hara en la 3FN por ser dependencias transitivas.

    tablas_2fn = {}

    for nombre_tabla, df in tablas_1fn.items():
        df = df.copy()
        nombre_limpio = nombre_tabla.replace("_1FN", "")

        # --- TABLA BASE ---
        if "Base" in nombre_tabla:
            # En la tabla base, la PK es simple (la primera columna, Ej. CodigoEmpleado)
            # Como solo hay una columna clave, cumple 2FN automaticamente
            pk = df.columns[0]
            
            tablas_2fn[f"{nombre_limpio}_2FN"] = {
                "tabla": df,
                "PK": pk,
                "FK": []
            }

        # --- TABLAS MULTIVALOR (Telefonos, Proyectos) ---
        else:
            # En la teoria estricta, si extraes atributos multivalor, 
            # TODAS sus columnas forman la Clave Primaria Compuesta de esta tabla.
            pk_compuesta = list(df.columns)
            
            # La primera columna que heredo de la tabla base sigue siendo Clave Foranea
            fk_heredada = df.columns[0]
            
            tablas_2fn[f"{nombre_limpio}_2FN"] = {
                "tabla": df,
                "PK": " + ".join(pk_compuesta),
                "FK": [fk_heredada]
            }

    return tablas_2fn