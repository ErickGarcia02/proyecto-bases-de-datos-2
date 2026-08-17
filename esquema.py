def generar_esquema_plano(tablas_normalizadas):
    """
    Genera un archivo de texto plano con el esquema/diagrama relacional
    de la base de datos normalizada, detallando Tablas, PKs, FKs y Atributos.
    """
    lineas = [
        "==================================================",
        " ESQUEMA RELACIONAL (ARCHIVO PLANO / DIAGRAMA) ",
        "==================================================",
        ""
    ]
    
    # Mapear tablas que sirven de origen para las Foráneas
    mapa_pk = {}
    for nombre, info in tablas_normalizadas.items():
        pk = info["PK"]
        if " + " not in pk:
            mapa_pk[pk] = nombre

    # Construir el esquema tabla por tabla
    for nombre_tabla, info in tablas_normalizadas.items():
        df = info["tabla"]
        pk = info["PK"]
        fks = info["FK"]
        
        lineas.append(f"TABLA: {nombre_tabla}")
        lineas.append(f"  [PK] Clave Primaria : {pk}")
        
        if fks:
            fk_text = []
            for fk in fks:
                tabla_destino = mapa_pk.get(fk, "Tabla_Base")
                fk_text.append(f"{fk} -> {tabla_destino}")
            lineas.append(f"  [FK] Claves Foráneas: {', '.join(fk_text)}")
        else:
            lineas.append("  [FK] Claves Foráneas: Ninguna")
            
        cols_extras = [c for c in df.columns if c not in pk.split(" + ") and c not in fks]
        if cols_extras:
            lineas.append(f"  [--] Otros Atributos: {', '.join(cols_extras)}")
        else:
            lineas.append(f"  [--] Otros Atributos: Ninguno")
            
        lineas.append("-" * 50)
        
    return "\n".join(lineas)