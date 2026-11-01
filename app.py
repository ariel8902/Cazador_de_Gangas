import os
import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright

# Instalar ejecutable de Chromium en Streamlit Cloud
os.system("playwright install chromium")

from exito import extraer_exito
from alkosto import extraer_alkosto
from ktronix import extraer_ktronix

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Cazador de Gangas",
    page_icon="🎯",
    layout="wide"
)

# Estilos CSS personalizados para las tarjetas de productos
st.markdown("""
    <style>
    .card-producto {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #333333;
        text-align: center;
    }
    .badge-descuento {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
    }
    .precio-normal {
        text-decoration: line-through;
        color: #888888;
        font-size: 13px;
    }
    .precio-oferta {
        color: #2e7d32;
        font-size: 18px;
        font-weight: bold;
    }
    .btn-comprar {
        display: inline-block;
        background-color: #ff4b4b;
        color: white !important;
        padding: 8px 16px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
        width: 100%;
    }
    .btn-comprar:hover {
        background-color: #d32f2f;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL - CONFIGURACIÓN
# ==========================================
st.sidebar.title("🎯 Cazador de Gangas")

almacen_seleccionado = st.sidebar.selectbox(
    "Elija el almacén a rastrear:",
    ["Éxito", "Alkosto", "Ktronix"]
)

btn_ejecutar = st.sidebar.button("🚀 Rastrear Gangas")
btn_limpiar = st.sidebar.button("🗑️ Limpiar Resultados")

st.sidebar.markdown("---")
modo_vista = st.sidebar.radio("Seleccione el modo de visualización:", ["Catálogo Comercial 🛍️", "Tabla de Control 📊"])

# ==========================================
# PANEL PRINCIPAL
# ==========================================
st.title("🎯 Las Mejores Ofertas en Tiempo Real")
st.write("Encuentre los descuentos más altos verificados directamente desde las grandes superficies de Colombia.")

if "ofertas" not in st.session_state:
    st.session_state["ofertas"] = []

if btn_limpiar:
    st.session_state["ofertas"] = []
    st.success("Historial de ofertas limpiado correctamente.")

# ==========================================
# EJECUCIÓN DEL RASTREO
# ==========================================
if btn_ejecutar:
    with st.spinner(f"Buscando las mejores ofertas en {almacen_seleccionado}..."):
        try:
            nuevas_ofertas = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                if almacen_seleccionado == "Éxito":
                    url_exito = "https://www.exito.com/tecnologia"
                    nuevas_ofertas = extraer_exito(page, "Tecnología", url_exito)
                elif almacen_seleccionado == "Alkosto":
                    nuevas_ofertas = extraer_alkosto(page)
                elif almacen_seleccionado == "Ktronix":
                    nuevas_ofertas = extraer_ktronix(page)

                browser.close()

            if nuevas_ofertas:
                st.session_state["ofertas"].extend(nuevas_ofertas)
                st.success(f"¡Rastreo exitoso! Se agregaron {len(nuevas_ofertas)} gangas al catálogo.")
            else:
                st.warning("No se encontraron ofertas en este momento.")

        except Exception as e:
            st.error(f"Error durante la extracción: {str(e)}")

# ==========================================
# RENDERS DE RESULTADOS
# ==========================================
if st.session_state["ofertas"]:
    
    # OPCCIÓN A: CATÁLOGO COMERCIAL CON TARJETAS
    if modo_vista == "Catálogo Comercial 🛍️":
        st.subheader("🛍️ Vitrina de Productos en Descuento")
        
        # Crear cuadrícula de 3 columnas para productos
        cols = st.columns(3)
        for idx, prod in enumerate(st.session_state["ofertas"]):
            col = cols[idx % 3]
            with col:
                # Extraer atributos de la oferta con valores por defecto
                titulo = prod.get("Nombre", prod.get("Producto", "Producto en oferta"))
                precio_norm = prod.get("Precio Normal", "N/A")
                precio_ofe = prod.get("Precio Oferta", "N/A")
                descuento = prod.get("Descuento", "Oferta")
                enlace = prod.get("Enlace Directo", prod.get("Enlace", "#"))
                imagen = prod.get("Imagen", "https://via.placeholder.com/200?text=Sin+Imagen")

                st.markdown(f"""
                    <div class="card-producto">
                        <img src="{imagen}" style="max-width: 100%; height: 180px; object-fit: contain; margin-bottom: 10px;">
                        <span class="badge-descuento">-{descuento}</span>
                        <h4 style="font-size: 15px; margin: 10px 0; height: 40px; overflow: hidden;">{titulo}</h4>
                        <p class="precio-normal">Antes: {precio_norm}</p>
                        <p class="precio-oferta">Ahora: {precio_ofe}</p>
                        <a href="{enlace}" target="_blank" class="btn-comprar">Ver Ganga en la Tienda ➔</a>
                    </div>
                """, unsafe_allow_html=True)

    # OPCIÓN B: TABLA TÉCNICA CON ENLACES CLIQUEABLES
    else:
        st.subheader("📊 Tabla Interna de Control")
        df = pd.DataFrame(st.session_state["ofertas"])
        
        st.dataframe(
            df,
            column_config={
                "Enlace Directo": st.column_config.LinkColumn(
                    "Enlace de Compra",
                    help="Haga clic para ir directamente al producto",
                    validate="^https://.*",
                    display_text="Abrir Oferta 🔗"
                )
            },
            use_container_width=True
        )

else:
    st.info("👈 Seleccione el almacén en la barra lateral y presione 'Rastrear Gangas' para cargar la vitrina.")
