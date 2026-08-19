def generar_esquema_plano(tablas_normalizadas):
    """
    Genera un archivo de texto con el esquema descriptivo Entidad-Relación
    y el código compatible con Mermaid.js para dibujar un diagrama gráfico.
    """
    lineas = [
        "==================================================",
        " ESQUEMA ENTIDAD-RELACIÓN (DESCRIPTIVO) ",
        "==================================================",
        ""
    ]
    
    # Mapear tablas que sirven de origen para las Foráneas
    mapa_pk = {}
    for nombre, info in tablas_normalizadas.items():
        pk = info["PK"]
        if " + " not in pk:
            mapa_pk[pk] = nombre

    # 1. PARTE DESCRIPTIVA (Lectura Humana)
    for nombre_tabla, info in tablas_normalizadas.items():
        df = info["tabla"]
        pk = info["PK"]
        fks = info["FK"]
        
        lineas.append(f"ENTIDAD: {nombre_tabla}")
        lineas.append(f"  [PK] Identificador único : {pk}")
        
        if fks:
            fk_text = []
            for fk in fks:
                tabla_destino = mapa_pk.get(fk, "Tabla_Base")
                fk_text.append(f"1:N -> Pertenece a la entidad '{tabla_destino}' ({fk})")
            lineas.append(f"  [FK] Relaciones          : {', '.join(fk_text)}")
        else:
            lineas.append("  [FK] Relaciones          : Ninguna (Entidad Fuerte / Catálogo)")
            
        cols_extras = [c for c in df.columns if c not in pk.split(" + ") and c not in fks]
        if cols_extras:
            lineas.append(f"  [--] Otros Atributos     : {', '.join(cols_extras)}")
        else:
            lineas.append(f"  [--] Otros Atributos     : Ninguno")
            
        lineas.append("-" * 50)
        
    # 2. PARTE GRÁFICA (Código para renderizar el diagrama ER)
    lineas.extend([
        "",
        "==================================================",
        " CÓDIGO DE DIAGRAMA ER GRÁFICO (MERMAID) ",
        "==================================================",
        " Instrucciones: Copia todo el bloque de abajo y pégalo ",
        " en https://mermaid.live para visualizar el diagrama gráfico.",
        "",
        "erDiagram"
    ])
    
    for nombre_tabla, info in tablas_normalizadas.items():
        df = info["tabla"]
        pk_cols = [c.strip() for c in info["PK"].split(" + ")]
        fks = info["FK"]
        
        # Bloque de atributos de la entidad
        lineas.append(f"    {nombre_tabla} {{")
        for p in pk_cols:
            lineas.append(f"        string {p} PK")
        for fk in fks:
            if fk not in pk_cols:
                lineas.append(f"        string {fk} FK")
                
        cols_extras = [c for c in df.columns if c not in pk_cols and c not in fks]
        for col in cols_extras:
            # Limpiar nombres de columnas para evitar errores de sintaxis en Mermaid
            col_limpia = col.replace(" ", "_").replace("-", "_")
            lineas.append(f"        string {col_limpia}")
        lineas.append("    }")
        
        # Bloque de relaciones (Líneas que conectan las tablas)
        if fks:
            for fk in fks:
                tabla_destino = mapa_pk.get(fk, "Tabla_Base")
                if tabla_destino != nombre_tabla:
                    # Dibuja la relación de 1 a muchos (1:N)
                    lineas.append(f"    {tabla_destino} ||--o{{ {nombre_tabla} : \"tiene ({fk})\"")

    return "\n".join(lineas)