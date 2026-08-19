def generar_esquema_plano(tablas_normalizadas):
    """Genera el documento de texto descriptivo (sin el gráfico)"""
    lineas = [
        "==================================================",
        " ESQUEMA ENTIDAD-RELACIÓN (DOCUMENTACIÓN) ",
        "==================================================",
        ""
    ]
    
    mapa_pk = {info["PK"]: nombre for nombre, info in tablas_normalizadas.items() if " + " not in info["PK"]}

    for nombre_tabla, info in tablas_normalizadas.items():
        df = info["tabla"]
        pk = info["PK"]
        fks = info["FK"]
        
        lineas.append(f"ENTIDAD: {nombre_tabla}")
        lineas.append(f"  [PK] Identificador único : {pk}")
        
        if fks:
            fk_text = [f"1:N -> '{mapa_pk.get(fk, 'Tabla_Base')}' ({fk})" for fk in fks]
            lineas.append(f"  [FK] Relaciones          : {', '.join(fk_text)}")
        else:
            lineas.append("  [FK] Relaciones          : Ninguna (Entidad Fuerte / Catálogo)")
            
        cols_extras = [c for c in df.columns if c not in pk.split(" + ") and c not in fks]
        if cols_extras:
            lineas.append(f"  [--] Otros Atributos     : {', '.join(cols_extras)}")
        else:
            lineas.append(f"  [--] Otros Atributos     : Ninguno")
            
        lineas.append("-" * 50)
        
    return "\n".join(lineas)

def generar_codigo_mermaid(tablas_normalizadas):
    """Genera el código estricto para dibujar el gráfico ER"""
    lineas = ["erDiagram"]
    mapa_pk = {info["PK"]: nombre for nombre, info in tablas_normalizadas.items() if " + " not in info["PK"]}
    
    for nombre_tabla, info in tablas_normalizadas.items():
        df = info["tabla"]
        pk_cols = [c.strip() for c in info["PK"].split(" + ")]
        fks = info["FK"]
        
        # Atributos de la tabla
        lineas.append(f"    {nombre_tabla} {{")
        for p in pk_cols:
            lineas.append(f"        string {p} PK")
        for fk in fks:
            if fk not in pk_cols:
                lineas.append(f"        string {fk} FK")
                
        cols_extras = [c for c in df.columns if c not in pk_cols and c not in fks]
        for col in cols_extras:
            col_limpia = col.replace(" ", "_").replace("-", "_")
            lineas.append(f"        string {col_limpia}")
        lineas.append("    }")
        
        # Relaciones (Líneas)
        if fks:
            for fk in fks:
                tabla_destino = mapa_pk.get(fk, "Tabla_Base")
                if tabla_destino != nombre_tabla:
                    lineas.append(f"    {tabla_destino} ||--o{{ {nombre_tabla} : \"({fk})\"")

    return "\n".join(lineas)