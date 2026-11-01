import os
import json
import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Cazador de Gangas",
    page_icon="🎯",
    layout="wide"
)

# Estilos visuales
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
    </style>
""", unsafe_allow_html=True)

# Función para cargar ofertas guardadas
def cargar_ofertas_guardadas():
    if os.path.exists("ofertas.json"):
        with open("ofertas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ==========================================
# BARRA LATERAL (ADMINISTRACIÓN)
# ==========================================
st.sidebar.title("🎯 Control de Administración")
modo_vista = st.sidebar.radio("Modo de visualización:", ["Catálogo Comercial 🛍️", "Tabla de Control 📊"])

st.sidebar.markdown("---")
st.sidebar.info("🤖 El bot actualiza automáticamente las gangas todas las noches a las 12:00 AM.")

# ==========================================
# VISTAS PRINCIPALES
# ==========================================
st.title("🎯 Las Mejores Ofertas en Tiempo Real")
st.write("Catálogo actualizado de las grandes superficies de Colombia.")

ofertas = cargar_ofertas_guardadas()

if ofertas:
    if modo_vista == "Catálogo Comercial 🛍️":
        st.subheader(f"🛍️ Vitrina de Ofertas ({len(ofertas)} gangas activas)")
        
        cols = st.columns(3)
        for idx, prod in enumerate(ofertas):
            col = cols[idx % 3]
            with col:
                titulo = prod.get("Nombre", "Producto en oferta")
                precio_norm = prod.get("Precio Normal", "N/A")
                precio_ofe = prod.get("Precio Oferta", "N/A")
                descuento = prod.get("Descuento", "Oferta")
                enlace = prod.get("Enlace Directo", "#")
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
    else:
        st.subheader("📊 Tabla Interna de Control")
        df = pd.DataFrame(ofertas)
        st.dataframe(
            df,
            column_config={
                "Enlace Directo": st.column_config.LinkColumn("Enlace de Compra", display_text="Abrir Oferta 🔗")
            },
            use_container_width=True
        )
else:
    st.warning("Aún no hay ofertas recopiladas. La primera actualización automática se ejecutará esta noche a las 12:00 AM.")
