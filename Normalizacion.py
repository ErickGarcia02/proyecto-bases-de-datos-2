import pandas as pd

def evaluar_forma_normal(df):

    if df is None or df.empty:
        return "No hay datos para evaluar", "error", []

    detalles = []

    # PRUEBA 1FN: Atributos atómicos (sin comas)

    falla_1fn_comas = False
    for columna in df.columns:
        if df[columna].dtype == 'object':
            if df[columna].astype(str).str.contains(r'[,;]').any():
                falla_1fn_comas = True
                detalles.append(f"Atributo multivalor (separado por comas) detectado en '{columna}'.")
    
    if falla_1fn_comas:
        return "No Normalizada", "error", detalles

    pk_col = df.columns[0] 
    if df.duplicated(subset=[pk_col]).any():
        detalles.append(f"La Clave Principal '{pk_col}' está duplicada porque hay relaciones anidadas en la misma tabla.")
        detalles.append(" Remedio: Aplica la Transformación a 1FN para separar los atributos en nuevas tablas.")
        return "Prenormalizada (Falta separar a 1FN)", "warning", detalles

    detalles.append("Los datos son atómicos y no hay relaciones anidadas (Cumple 1FN).")
    
    filas_totales = len(df)
    redundancias = 0
    if filas_totales > 1:
        for columna in df.columns:
            if df[columna].nunique() < filas_totales and df[columna].nunique() > 1:
                redundancias += 1
                
    if redundancias > 2:
        detalles.append("Se detectaron redundancias que sugieren dependencias parciales (2FN) o transitivas (3FN).")
        return "1FN (Primera Forma Normal)", "warning", detalles

    detalles.append("No se detectaron redundancias evidentes.")
    return "Posible 3FN (Tercera Forma Normal)", "success", detalles