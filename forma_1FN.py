import pandas as pd

def transformar_a_1fn(df, pk_col):

    tablas_1fn = {}
    df_temp = df.copy()
    
    columnas_a_separar = []

    for col in df_temp.columns:
        if col != pk_col:

            if df_temp.groupby(pk_col)[col].nunique().max() > 1:
                columnas_a_separar.append(col)
                
    if not columnas_a_separar:
        for col in df_temp.columns:
            if df_temp[col].dtype == 'object' and df_temp[col].astype(str).str.contains(',').any():
                columnas_a_separar.append(col)
                df_temp[col] = df_temp[col].astype(str).str.split(',')
                df_temp = df_temp.explode(col)
                df_temp[col] = df_temp[col].str.strip()

    columnas_base = [col for col in df_temp.columns if col not in columnas_a_separar]
    df_base = df_temp[columnas_base].drop_duplicates().reset_index(drop=True)
    tablas_1fn['Tabla_Base_1FN'] = df_base

    for col in columnas_a_separar:

        df_relacion = df_temp[[pk_col, col]].copy()
        
        df_relacion = df_relacion.drop_duplicates().reset_index(drop=True)
        
        df_relacion = df_relacion.dropna(subset=[col])
        df_relacion = df_relacion[df_relacion[col] != ""]
        
        tablas_1fn[f'Tabla_{col}_1FN'] = df_relacion
        
    return tablas_1fn