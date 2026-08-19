import pandas as pd

def evaluar_forma_normal(df):

    if df is None or df.empty:
        return "No hay datos para evaluar", "error", []

    detalles = []

    # 1. PRUEBA 1FN: 
    falla_1fn_comas = False
    for columna in df.columns:
        if df[columna].dtype == 'object':
            if df[columna].astype(str).str.contains(r'[,;]').any():
                falla_1fn_comas = True
                detalles.append(f"Atributo multivalor detectado en '{columna}'.")
    
    if falla_1fn_comas:
        return "No Normalizada", "error", detalles

    # 2. PRUEBA 1FN: Llave duplicada (Relaciones anidadas)
    pk_col = df.columns[0] 
    if df.duplicated(subset=[pk_col]).any():
        detalles.append(f"La Clave Principal '{pk_col}' está duplicada.")
        detalles.append("Remedio: Aplica la Transformación a 1FN para separar atributos.")
        return "Prenormalizada (Falta separar a 1FN)", "warning", detalles

    detalles.append("Los datos son atómicos y no hay relaciones anidadas (Cumple 1FN).")
    
    # 3. PRUEBA 2FN/3FN: Dependencias Funcionales Reales
    dependencia_detectada = False
    columnas_candidatas = [c for c in df.columns if c != pk_col]

    for col_a in columnas_candidatas:
        # Ignorar columnas que son únicas para cada fila (no pueden ser determinantes comunes)
        if df[col_a].nunique() >= len(df):
            continue
            
        for col_b in columnas_candidatas:
            if col_a != col_b:
                sub = df[[col_a, col_b]].dropna()
                if not sub.empty:
                    # La prueba matemática de dependencia funcional
                    if sub.groupby(col_a)[col_b].nunique().max() == 1:
                        dependencia_detectada = True
                        detalles.append(f"Redundancia detectada: '{col_b}' depende lógicamente de '{col_a}'.")
                        break 
        
        if dependencia_detectada:
            break

    if dependencia_detectada:
        return "1FN o 2FN (Requiere normalizar a 3FN)", "warning", detalles

    detalles.append("No se detectaron dependencias parciales ni transitivas.")
    return "Posible 3FN (Tercera Forma Normal)", "success", detalles