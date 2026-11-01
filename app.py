import os
import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright

# Instalar Chromium automáticamente si no existe en el contenedor
os.system("playwright install chromium")

from exito import extraer_exito
from alkosto import extraer_alkosto
from ktronix import extraer_ktronix

st.set_page_config(
    page_title="Cazador de Gangas (En Vivo)",
    page_icon="🎯",
    layout="wide"
)

st.sidebar.title("Control de Extractores")
almacen_seleccionado = st.sidebar.selectbox(
    "Elija el almacén a rastrear:",
    ["Éxito", "Alkosto", "Ktronix"]
)

btn_ejecutar = st.sidebar.button("🚀 Ejecutar Extracción")
btn_limpiar = st.sidebar.button("🗑️ Limpiar Historial")

st.title("🎯 Panel de Control: Cazador de Gangas (En Vivo)")
st.write("Seleccione el almacén que desea rastrear, pulse el botón y el sistema traerá las ofertas reales directamente a su pantalla.")

if "ofertas" not in st.session_state:
    st.session_state["ofertas"] = []

if btn_limpiar:
    st.session_state["ofertas"] = []
    st.success("Historial de ofertas limpiado correctamente.")

if btn_ejecutar:
    with st.spinner(f"Rastreando ofertas en {almacen_seleccionado}... Por favor espere."):
        try:
            nuevas_ofertas = []
            
            # Inicializar el navegador con Playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                if almacen_seleccionado == "Éxito":
                    url_exito = "https://www.exito.com/tecnologia"
                    nuevas_ofertas = extraer_exito(page, "Tecnología", url_exito)
                elif almacen_seleccionado == "Alkosto":
                    # Ajustar según parámetros requeridos por alkosto.py
                    nuevas_ofertas = extraer_alkosto(page)
                elif almacen_seleccionado == "Ktronix":
                    # Ajustar según parámetros requeridos por ktronix.py
                    nuevas_ofertas = extraer_ktronix(page)

                browser.close()

            if nuevas_ofertas:
                st.session_state["ofertas"].extend(nuevas_ofertas)
                st.success(f"¡Extracción completada! Se encontraron {len(nuevas_ofertas)} ofertas.")
            else:
                st.warning("No se encontraron ofertas o la página tardó en responder.")

        except Exception as e:
            st.error(f"Error durante la extracción: {str(e)}")

if st.session_state["ofertas"]:
    df = pd.DataFrame(st.session_state["ofertas"])
    st.subheader("📋 Gangas Detectadas")
    st.dataframe(df, use_container_width=True)
else:
    st.info("👈 Seleccione el almacén en la barra lateral y presione 'Ejecutar Extracción' para comenzar a acumular gangas.")
