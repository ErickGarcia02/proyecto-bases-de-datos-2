import pandas as pd

def evaluar_forma_normal(df):
    if df is None or df.empty:
        return "No hay datos para evaluar", "error", []

    detalles = []

    # 1. PRUEBA 0FN (Sin normalizar)
    falla_1fn_comas = False
    for columna in df.columns:
        if df[columna].dtype == 'object':
            if df[columna].astype(str).str.contains(r'[,;]').any():
                falla_1fn_comas = True
                detalles.append(f"Atributo multivalor detectado en '{columna}'.")
    
    if falla_1fn_comas:
        detalles.append("Remedio: Aplicar Prenormalización o 1FN para separar listas.")
        return "0FN (Sin Normalizar)", "error", detalles

    # 2. PRUEBA PRENORMALIZADA:
    pk_col = df.columns[0] 
    if df.duplicated(subset=[pk_col]).any():
        detalles.append(f"La Clave Principal '{pk_col}' está duplicada (datos anidados).")
        detalles.append("Remedio: Aplica la Transformación a 1FN para separar atributos.")
        return "Prenormalizada (Falta 1FN)", "warning", detalles

    detalles.append("Cumple 1FN: Datos atómicos y sin grupos repetidos.")
    
  
    dependencia_transitiva = False
    columnas_no_pk = [c for c in df.columns if c != pk_col]

    for col_a in columnas_no_pk:
        if df[col_a].nunique() >= len(df):
            continue
            
        for col_b in columnas_no_pk:
            if col_a != col_b:
                sub = df[[col_a, col_b]].dropna()
                if not sub.empty:
                    if sub.groupby(col_a)[col_b].nunique().max() == 1:
                        dependencia_transitiva = True
                        detalles.append(f"Dependencia Transitiva: '{col_b}' depende lógicamente de '{col_a}'.")
                        break 
        
        if dependencia_transitiva:
            break

    if dependencia_transitiva:
        detalles.append("Remedio: Aplica la 3FN para extraer estos atributos a un catálogo.")
        return "2FN (Segunda Forma Normal)", "warning", detalles

    detalles.append("No se detectaron dependencias transitivas.")
    return "3FN (Tercera Forma Normal)", "success", detalles