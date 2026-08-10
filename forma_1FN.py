import pandas as pd

def transformar_a_1fn(df, pk_col):
    """
    Convierte una tabla a 1FN creando nuevas relaciones estrictamente 
    para los atributos multivalor (separados por comas) y propagando la PK.
    """
    tablas_1fn = {}
    columnas_multivalor = []

    for col in df.columns:
        if df[col].dtype == 'object' and df[col].astype(str).str.contains(',').any():
            columnas_multivalor.append(col)

    if not columnas_multivalor and df.duplicated(subset=[pk_col]).any():
        for col in df.columns:
            if col != pk_col:
                if df.groupby(pk_col)[col].nunique().max() > 1:
                    columnas_multivalor.append(col)

    columnas_base = [col for col in df.columns if col not in columnas_multivalor]
    df_base = df[columnas_base].drop_duplicates(subset=[pk_col]).reset_index(drop=True)
    tablas_1fn['Tabla_Base_1FN'] = df_base

    for col in columnas_multivalor:
        df_rel = df[[pk_col, col]].copy()

        if df_rel[col].dtype == 'object':
            df_rel[col] = df_rel[col].astype(str).str.split(',')
            df_rel = df_rel.explode(col)
            df_rel[col] = df_rel[col].str.strip()

        df_rel = df_rel.dropna(subset=[col])
        df_rel = df_rel[~df_rel[col].astype(str).isin(["nan", "None", ""])]
        df_rel = df_rel.drop_duplicates().reset_index(drop=True)
        
        tablas_1fn[f'Tabla_{col}_1FN'] = df_rel

    return tablas_1fn