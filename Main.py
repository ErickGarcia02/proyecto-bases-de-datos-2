import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Entrada de Datos", 
    layout="wide"
)

st.title("Proyecto I: Normalización Automatizada")
st.write("**Grupo #3 - Administración de Base de Datos 2**")
st.markdown("---")

st.subheader("1. Carga y Visualización de Datos (Input)")

archivo_subido = st.file_uploader("Sube tu script de base de datos (.sql)", type=["sql"])

if archivo_subido is not None:
    codigo_sql = archivo_subido.getvalue().decode("utf-8")
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    try:
        cursor.executescript(codigo_sql)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        if tablas:
            st.success("Archivo SQL leído con exito")

            for tabla in tablas:
                nombre_tabla = tabla[0]
                st.write(f"### Vista de la Tabla: `{nombre_tabla}`")
                
                df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conn)
                
                st.dataframe(df, use_container_width=True)
                
        else:
            st.warning("El archivo SQL se leyó bien, pero no contiene instrucciones para crear tablas (CREATE TABLE).")
            st.code(codigo_sql, language="sql")
            
    except Exception as e:

        st.error(f"Hubo un error al leer el código SQL: {e}")
        st.info("Asegúrate de que tu archivo .sql tenga instrucciones estándar de SQL (CREATE TABLE y INSERT INTO).")
        
    finally:
        conn.close() 

else:
    st.info("ingresar archivo sql.")