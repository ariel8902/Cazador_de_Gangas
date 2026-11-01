import os
import streamlit as st
import pandas as pd

# ==========================================
# 1. FORZAR INSTALACIÓN DE CHROMIUM EN LA NUBE
# ==========================================
# Esto descarga automáticamente los ejecutables del navegador al arrancar Streamlit Cloud
os.system("playwright install chromium")

from playwright.sync_api import sync_playwright

# Importación de extractores por almacén
import exito
import alkosto
import falabella
import ktronix
import notificador

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
    ["Éxito", "Alkosto", "Falabella", "Ktronix"]
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
            # Llamada al módulo del almacén según la selección
            if almacen_seleccionado == "Éxito":
                nuevas_ofertas = exito.extraer_ofertas()
            elif almacen_seleccionado == "Alkosto":
                nuevas_ofertas = alkosto.extraer_ofertas()
            elif almacen_seleccionado == "Falabella":
                nuevas_ofertas = falabella.extraer_ofertas()
            elif almacen_seleccionado == "Ktronix":
                nuevas_ofertas = ktronix.extraer_ofertas()
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
