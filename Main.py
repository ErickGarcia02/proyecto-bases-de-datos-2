import os
import pandas as pd
import numpy as np
import streamlit as st
from read_file import read_sql_file
from Normalizacion import evaluar_forma_normal
from forma_1FN import transformar_a_1fn

def prenormalizar_tabla(df):

    df_prenorm = df.copy()
    for col in df_prenorm.columns:
        if df_prenorm[col].dtype == 'object':
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
    /* Fondo general con degradado sutil */
    .stApp {
        background: radial-gradient(circle at 20% 0%, #1D1330 0%, #120B1F 45%, #0B0715 100%);
    }

    /* Tipografías */
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

    /* Tablas */
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
                datos[col] = pd.to_numeric(datos[col], errors='ignore')

# FLUJO LÓGICO: VISTAS -> DIAGNÓSTICO -> TRANSFORMACIÓN

if datos is not None:

    st.markdown("### Vista previa de los datos")
    tab_datos, tab_columnas = st.tabs(["Datos", "Columnas y Metadatos"])

    with tab_datos:
        st.dataframe(datos, use_container_width=True)

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
        st.dataframe(info_cols, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # 2. DIAGNÓSTICO DE NORMALIZACIÓN
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
    
    # 3. HERRAMIENTAS DE TRANSFORMACIÓN
    st.markdown(" Herramientas de Transformación")
    
    if st.button("0. Aplicar Prenormalización (Crear registros nuevos)"):
        with st.spinner("Descomponiendo valores separados por comas..."):
            datos_prenorm = prenormalizar_tabla(datos)
            
            st.session_state['datos_procesados'] = datos_prenorm
            st.session_state['mostrar_prenorm'] = True

    if st.session_state.get('mostrar_prenorm', False):
        st.success("Prenormalizacion completada. Los valores con comas se han dividido en nuevas filas.")
        st.dataframe(st.session_state['datos_procesados'], use_container_width=True)

    st.markdown("---")

    if st.button("1. Transformar a 1FN (Separar en tablas)", type="primary"):
        with st.spinner("Generando nuevas relaciones y propagando claves..."):
            
            columna_pk = datos.columns[0] 
            tablas_resultantes = transformar_a_1fn(datos, pk_col=columna_pk)
            
            st.session_state['tablas_1fn'] = tablas_resultantes
            st.session_state['mostrar_1fn'] = True

    if st.session_state.get('mostrar_1fn', False):
        st.success("Transformacion a 1FN completada. Se han generado las tablas independientes.")
        for nombre_t, df_resultado in st.session_state['tablas_1fn'].items():
            st.markdown(f"#### {nombre_t}")
            st.dataframe(df_resultado, use_container_width=True, hide_index=True)