import os
import streamlit as st
import pandas as pd

# ==========================================
# 1. FORZAR INSTALACIÓN DE CHROMIUM EN LA NUBE
# ==========================================
os.system("playwright install chromium")

from playwright.sync_api import sync_playwright

# Importación de las funciones exactas de cada almacén
from exito import extraer_exito
from alkosto import extraer_alkosto
from ktronix import extraer_ktronix
# Si tiene falabella.py con función extraer_falabella, descomente la siguiente línea:
# from falabella import extraer_falabella

# ==========================================
# 2. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Cazador de Gangas (En Vivo)",
    page_icon="🎯",
    layout="wide"
)

# ==========================================
# 3. BARRA LATERAL - CONTROL DE EXTRACTORES
# ==========================================
st.sidebar.title("Control de Extractores")

almacen_seleccionado = st.sidebar.selectbox(
    "Elija el almacén a rastrear:",
    ["Éxito", "Alkosto", "Ktronix"]
)

btn_ejecutar = st.sidebar.button("🚀 Ejecutar Extracción")
btn_limpiar = st.sidebar.button("🗑️ Limpiar Historial")

# ==========================================
# 4. PANEL PRINCIPAL
# ==========================================
st.title("🎯 Panel de Control: Cazador de Gangas (En Vivo)")
st.write("Seleccione el almacén que desea rastrear, pulse el botón y el sistema traerá las ofertas reales directamente a su pantalla.")

# Inicializar almacenamiento de resultados en la sesión
if "ofertas" not in st.session_state:
    st.session_state["ofertas"] = []

if btn_limpiar:
    st.session_state["ofertas"] = []
    st.success("Historial de ofertas limpiado correctamente.")

# ==========================================
# 5. EJECUCIÓN DEL RASTREO
# ==========================================
if btn_ejecutar:
    with st.spinner(f"Rastreando ofertas en {almacen_seleccionado}... Por favor espere."):
        try:
            # Llamada exacta a la función de cada módulo
            if almacen_seleccionado == "Éxito":
                nuevas_ofertas = extraer_exito()
            elif almacen_seleccionado == "Alkosto":
                nuevas_ofertas = extraer_alkosto()
            elif almacen_seleccionado == "Ktronix":
                nuevas_ofertas = extraer_ktronix()
            else:
                nuevas_ofertas = []

            if nuevas_ofertas:
                st.session_state["ofertas"].extend(nuevas_ofertas)
                st.success(f"¡Extracción completada! Se encontraron {len(nuevas_ofertas)} ofertas.")
            else:
                st.warning("No se encontraron ofertas o la página tardó en responder.")
                
        except Exception as e:
            st.error(f"Error durante la extracción: {str(e)}")

# ==========================================
# 6. VISUALIZACIÓN DE RESULTADOS
# ==========================================
if st.session_state["ofertas"]:
    df = pd.DataFrame(st.session_state["ofertas"])
    st.subheader("📋 Gangas Detectadas")
    st.dataframe(df, use_container_width=True)
else:
    st.info("👈 Seleccione el almacén en la barra lateral y presione 'Ejecutar Extracción' para comenzar a acumular gangas.")
