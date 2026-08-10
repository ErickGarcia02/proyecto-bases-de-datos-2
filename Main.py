import os
import pandas as pd
import streamlit as st
from read_file import read_sql_file

st.set_page_config(
    page_title="Normalizador de Bases de Datos",
    page_icon="🗄",
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
    h2, h3 {
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
        <h1>🗄 Normalizador de Bases de Datos</h1>
        <p>Grupo #3 · Normalización de datos a la Tercera Forma Normal (3FN)</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("### ℹ️ Acerca del Programa")
    st.write(
        "Este proyecto tiene la finalidad de ayudar a los usuarios a normalizar sus bases de datos a la Tercera Forma Normal (3FN). "
        "Con la opción de visualizar la estructura de la base de datos y descargarla en formato SQL, este programa facilita la gestión y optimización de datos."
    )
    st.markdown("---")
    st.markdown("### 📂 Formato Soportado")
    st.markdown("🧾 Script SQL (`.sql`)")
    st.markdown("---")
    st.markdown("### 📌 Grupo #3 · Normalización a 3FN")


st.markdown("### 📤 Sube la base de datos")
archivo = st.file_uploader(
    "Subir Base de Datos",
    type=["sql"],
    accept_multiple_files=False,
    help="Sube tu Script SQL",
    label_visibility="collapsed",
)

if archivo is None:
    st.info("⬆️ Sube la base de datos.")
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
            st.markdown("###  Seleccione una tabla")
            nombre_tabla = st.selectbox(
                "¿Qué tabla del script quieres ver?",
                list(tablas_en_sql.keys()),
                label_visibility="collapsed",
            )
            datos = tablas_en_sql[nombre_tabla]

if datos is not None:
    
    st.markdown("Vista previa de los datos")
    tab_datos, tab_columnas = st.tabs(["📋 Datos", "🔎 Columnas"])

    with tab_datos:
        st.dataframe(datos, use_container_width=True)

    with tab_columnas:
        info_cols = pd.DataFrame(
            {
                "Columna": datos.columns,
                "Tipo": [str(t) for t in datos.dtypes],
                "Valores nulos": datos.isna().sum().values,
            }
        )
        st.dataframe(info_cols, use_container_width=True, hide_index=True)
        
        
        