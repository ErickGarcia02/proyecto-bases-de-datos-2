import os
import pandas as pd
import numpy as np
import streamlit as st

from read_file import read_sql_file
from Normalizacion import evaluar_forma_normal
from forma_1FN import transformar_a_1fn
from forma_2fn import transformar_a_2fn
from forma_3FN import transformar_3fn
from esquema import generar_esquema_plano, generar_codigo_mermaid
from output import generar_script_sql

def prenormalizar_tabla(df):
    df_prenorm = df.copy()
    for col in df_prenorm.columns:
        if pd.api.types.is_string_dtype(df_prenorm[col]) or df_prenorm[col].dtype == 'object':
            if df_prenorm[col].astype(str).str.contains(',').any():
                df_prenorm[col] = df_prenorm[col].astype(str).str.split(',')
                df_prenorm = df_prenorm.explode(col)
                df_prenorm[col] = df_prenorm[col].str.strip()
    return df_prenorm.reset_index(drop=True)

st.set_page_config(
    page_title="Normalizador de Bases de Datos",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 0%, #1D1330 0%, #120B1F 45%, #0B0715 100%);
    }
    h1 {
        color: #C4B5FD;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    h2, h3, h4 {
        color: #DDD6FE;
    }
    p, label, span {
        color: #E9E3FB;
    }
    .hero {
        background: linear-gradient(135deg, #4C2E8C 0%, #7C3AED 50%, #A78BFA 100%);
        padding: 1.8rem 2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.35);
    }
    .hero h1 {
        color: white;
        margin-bottom: 0.2rem;
    }
    .hero p {
        color: #EDE9FE;
        font-size: 1.05rem;
        margin: 0;
    }
    div[data-testid="stMetric"] {
        background-color: #1D1330;
        border: 1px solid #4C2E8C;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetricLabel"] { color: #C4B5FD !important; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; }
    [data-testid="stDataFrame"] {
        border: 1px solid #7C3AED;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(124, 58, 237, 0.18);
    }
    section[data-testid="stFileUploaderDropzone"] {
        border-color: #4C2E8C !important;
        background-color: #1D1330 !important;
        border-radius: 16px !important;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #A78BFA !important;
    }
    button[kind="primary"], .stDownloadButton button {
        background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    button[kind="primary"]:hover, .stDownloadButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(167, 139, 250, 0.4) !important;
    }
    details {
        border: 1px solid #4C2E8C !important;
        border-radius: 12px !important;
        background-color: #1D1330 !important;
    }
    div[data-testid="stAlert"] {
        border-left: 4px solid #A78BFA;
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #150C24;
        border-right: 1px solid #2E1C4E;
    }
    button[data-baseweb="tab"] {
        color: #C4B5FD !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #A78BFA !important;
    }
    hr {
        border-color: #2E1C4E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Normalizador de Bases de Datos</h1>
        <p>Grupo #3 · Normalización de datos a la Tercera Forma Normal (3FN)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Acerca del Programa")
    st.write(
        "Este proyecto tiene la finalidad de ayudar a los usuarios a normalizar sus bases de datos a la Tercera Forma Normal (3FN). "
        "Con la opción de visualizar la estructura de la base de datos y descargarla en formato SQL, este programa facilita la gestión y optimización de datos."
    )
    st.markdown("---")
    st.markdown("### Formato Soportado")
    st.markdown("Script SQL (`.sql`)")
    st.markdown("---")
    st.markdown("### Grupo #3 · Normalización a 3FN")

st.markdown("### Sube la base de datos")
archivo = st.file_uploader(
    "Subir Base de Datos",
    type=["sql"],
    accept_multiple_files=False,
    help="Sube tu Script SQL",
    label_visibility="collapsed",
)

if archivo is None:
    st.info("Sube el script .sql para comenzar.")
    st.session_state.clear()
    st.stop()

extension = archivo.name.split(".")[-1].lower()
datos = None
nombre_tabla = None

with st.spinner("Procesando archivo..."):
    if extension == "sql":
        ruta_temp = "_temp_subida.sql"
        with open(ruta_temp, "wb") as f:
            f.write(archivo.getvalue())

        tablas_en_sql = read_sql_file(ruta_temp)
        os.remove(ruta_temp)

        if not tablas_en_sql:
            st.error("No se encontraron tablas (CREATE TABLE) en el archivo .sql.")
        else:
            st.markdown("Seleccione una tabla")
            nombre_tabla = st.selectbox(
                "¿Qué tabla del script quieres ver?",
                list(tablas_en_sql.keys()),
                label_visibility="collapsed",
            )

            if 'tabla_actual' not in st.session_state or st.session_state['tabla_actual'] != nombre_tabla:
                st.session_state.clear()
                st.session_state['tabla_actual'] = nombre_tabla

            datos = tablas_en_sql[nombre_tabla]
            datos = datos.replace(["NULL", "null", "None", ""], np.nan)

            for col in datos.columns:
                try:
                    datos[col] = pd.to_numeric(datos[col])
                except (ValueError, TypeError):
                    pass

if datos is not None:
    st.markdown("### Vista previa de los datos")
    tab_datos, tab_columnas = st.tabs(["Datos", "Columnas y Metadatos"])

    with tab_datos:
        st.dataframe(datos, width="stretch")

    with tab_columnas:
        tipos_sql, es_pk, es_fk = [], [], []

        for i, col in enumerate(datos.columns):
            tipo_pd = str(datos[col].dtype)
            if "int" in tipo_pd or "float" in tipo_pd:
                tipos_sql.append("INT" if "int" in tipo_pd else "FLOAT")
            else:
                tipos_sql.append("VARCHAR(255)")

            col_baja = col.lower()
            if i == 0 and ("codigo" in col_baja or "id" in col_baja):
                es_pk.append("Sí")
                es_fk.append("No")
            elif i > 0 and ("codigo" in col_baja or "id" in col_baja or "depto" in col_baja):
                es_pk.append("No")
                es_fk.append("Sí")
            else:
                es_pk.append("No")
                es_fk.append("No")

        info_cols = pd.DataFrame(
            {
                "Columna": datos.columns,
                "Tipo SQL": tipos_sql,
                "Nulos": datos.isna().sum().values,
                "PK (Clave Principal)": es_pk,
                "FK (Clave Foránea)": es_fk,
            }
        )
        st.dataframe(info_cols, width="stretch", hide_index=True)

    st.markdown("---")
    st.markdown("### Diagnóstico de Normalización")

    estado, tipo_alerta, detalles = evaluar_forma_normal(datos)

    if tipo_alerta == "error":
        st.error(f"Estado detectado: {estado}")
    elif tipo_alerta == "warning":
        st.warning(f"Estado detectado: {estado}")
    else:
        st.success(f"Estado detectado: {estado}")

    with st.expander("Ver detalles del análisis"):
        for detalle in detalles:
            st.write(detalle)

    st.markdown("---")
    st.markdown("### Herramientas de Transformación")

    if st.button("0. Aplicar Prenormalización (Crear registros nuevos)"):
        with st.spinner("Descomponiendo valores separados por comas..."):
            datos_prenorm = prenormalizar_tabla(datos)
            st.session_state['datos_procesados'] = datos_prenorm
            st.session_state['mostrar_prenorm'] = True

    if st.session_state.get('mostrar_prenorm', False):
        st.success("Prenormalización completada. Los valores con comas se han dividido en nuevas filas.")
        st.dataframe(st.session_state['datos_procesados'], width="stretch")

    st.markdown("---")

    if st.button("1. Transformar a 1FN (Separar en tablas)", type="primary"):
        with st.spinner("Generando nuevas relaciones y propagando claves..."):
            columna_pk = datos.columns[0]
            datos_entrada_1fn = st.session_state.get('datos_procesados', datos)
            tablas_resultantes = transformar_a_1fn(datos_entrada_1fn, pk_col=columna_pk)

            st.session_state['tablas_1fn'] = tablas_resultantes
            st.session_state['mostrar_1fn'] = True

    if st.session_state.get('mostrar_1fn', False):
        st.success("Transformación a 1FN completada. Se han generado las tablas independientes.")
        for nombre_t, df_resultado in st.session_state['tablas_1fn'].items():
            st.markdown(f"#### {nombre_t}")
            st.dataframe(df_resultado, width="stretch", hide_index=True)

    st.markdown("---")

    if st.button("2. Transformar a 2FN (Eliminar dependencias parciales)", type="primary"):
        if 'tablas_1fn' not in st.session_state:
            st.warning("⚠️ Por favor, ejecuta el Paso 1 (Transformar a 1FN) primero.")
        else:
            with st.spinner("Identificando claves y separando dependencias parciales..."):
                tablas_2fn_res = transformar_a_2fn(st.session_state['tablas_1fn'])
                st.session_state['tablas_2fn'] = tablas_2fn_res
                st.session_state['mostrar_2fn'] = True

    if st.session_state.get('mostrar_2fn', False):
        st.success("Transformación a 2FN completada. Se eliminaron las dependencias parciales.")
        for nombre_t, info in st.session_state['tablas_2fn'].items():
            df_resultado = info["tabla"]
            pk_col = info["PK"]
            fk_cols = info["FK"]

            st.markdown(f"#### {nombre_t}")
            col_pk, col_fk = st.columns(2)
            with col_pk:
                st.markdown(f"**Clave Primaria (PK):** `{pk_col}`")
            with col_fk:
                fks_texto = ", ".join([f"`{f}`" for f in fk_cols]) if fk_cols else "Ninguna"
                st.markdown(f"**Claves Foráneas (FK):** {fks_texto}")

            st.dataframe(df_resultado, width="stretch", hide_index=True)

    st.markdown("---")

    if st.button("3. Transformar a 3FN (Eliminar dependencias transitivas)", type="primary"):
        if 'tablas_2fn' not in st.session_state:
            st.warning("⚠️ Por favor, ejecuta el Paso 2 (Transformar a 2FN) primero.")
        else:
            with st.spinner("Detectando dependencias transitivas y extrayendo catálogos..."):
                tablas_3fn_res, conflictos = transformar_3fn(st.session_state['tablas_2fn'])
                st.session_state['tablas_3fn'] = tablas_3fn_res
                st.session_state['conflictos_3fn'] = conflictos
                st.session_state['mostrar_3fn'] = True

    if st.session_state.get('mostrar_3fn', False):
        if st.session_state['conflictos_3fn']:
            st.warning(
                f"Se detectaron {len(st.session_state['conflictos_3fn'])} conflicto(s) de datos. "
                "Las columnas involucradas NO se movieron a un catálogo compartido para evitar corromper la información."
            )
            with st.expander("Ver detalles de los conflictos"):
                for conflicto in st.session_state['conflictos_3fn']:
                    st.write(f"- {conflicto}")

        st.success("Transformación a 3FN completada. Se eliminaron las dependencias transitivas.")
        for nombre_t, info in st.session_state['tablas_3fn'].items():
            df_resultado = info["tabla"]
            pk_col = info["PK"]
            fk_cols = info["FK"]

            st.markdown(f"#### {nombre_t}")
            col_pk, col_fk = st.columns(2)
            with col_pk:
                st.markdown(f"**Clave Primaria (PK):** `{pk_col}`")
            with col_fk:
                fks_texto = ", ".join([f"`{f}`" for f in fk_cols]) if fk_cols else "Ninguna"
                st.markdown(f"**Claves Foráneas (FK):** {fks_texto}")

            st.dataframe(df_resultado, width="stretch", hide_index=True)

    st.markdown("---")

    if st.button("4. Generar Script SQL Final y Esquema Plano", type="primary"):
        if 'tablas_3fn' not in st.session_state:
            st.warning("⚠️ Por favor, ejecuta el Paso 3 (Transformar a 3FN) primero antes de generar el script.")
        else:
            with st.spinner("Generando archivos y dibujando diagrama..."):
                script_generado = generar_script_sql(
                    st.session_state['tablas_3fn'],
                    nombre_bd=nombre_tabla
                )
                st.session_state['script_sql'] = script_generado
                
                esquema_generado = generar_esquema_plano(st.session_state['tablas_3fn'])
                st.session_state['esquema_plano'] = esquema_generado
                
                codigo_mermaid = generar_codigo_mermaid(st.session_state['tablas_3fn'])
                st.session_state['codigo_mermaid'] = codigo_mermaid
                
                st.session_state['mostrar_script'] = True

    if st.session_state.get('mostrar_script', False):
        st.success("Archivos y diagrama generados correctamente.")
        
        tab_sql, tab_esquema, tab_diagrama = st.tabs(["Script SQL", "Esquema (Archivo Plano)", "Diagrama Visual ER"])
        
        with tab_sql:
            st.code(st.session_state['script_sql'], language="sql")
            st.download_button(
                label="Descargar Script SQL",
                data=st.session_state['script_sql'],
                file_name=f"{nombre_tabla}_normalizado.sql",
                mime="text/sql",
            )
            
        with tab_esquema:
            st.code(st.session_state['esquema_plano'], language="text")
            st.download_button(
                label="Descargar Esquema (Archivo Plano)",
                data=st.session_state['esquema_plano'],
                file_name=f"{nombre_tabla}_esquema.txt",
                mime="text/plain",
            )
            
        with tab_diagrama:
            st.info("💡 Este diagrama Entidad-Relación se genera automáticamente a partir de tu base de datos en 3FN.")
            st.markdown(f"```mermaid\n{st.session_state['codigo_mermaid']}\n```")