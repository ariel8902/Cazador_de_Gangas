import os
import json
import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Cazador de Gangas",
    page_icon="🎯",
    layout="wide"
)

# Archivo local para almacenar métricas de tráfico
STATS_FILE = "metricas.json"

def cargar_metricas():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"visitas": 0, "clics_ofertas": 0}

def guardar_metricas(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f)

# Registrar visita actual
stats = cargar_metricas()
if "visita_registrada" not in st.session_state:
    stats["visitas"] += 1
    guardar_metricas(stats)
    st.session_state["visita_registrada"] = True

# Estilos CSS con contenedores publicitarios
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
    .banner-publicidad {
        border: 2px dashed #cccccc;
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        color: #666666;
        margin: 15px 0;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

def cargar_ofertas_guardadas():
    if os.path.exists("ofertas.json"):
        with open("ofertas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ==========================================
# BARRA LATERAL (CONTROL Y MÉTRICAS)
# ==========================================
st.sidebar.title("🎯 Control de Administración")
modo_vista = st.sidebar.radio("Modo de visualización:", ["Catálogo Comercial 🛍️", "Tabla de Control 📊"])

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Auditoría de Tráfico")
st.sidebar.metric("Visitas Totales", stats["visitas"])
st.sidebar.metric("Clics en Ofertas", stats["clics_ofertas"])

st.sidebar.markdown("---")
st.sidebar.info("🤖 El bot actualiza automáticamente las gangas todas las noches a las 12:00 AM.")

# ==========================================
# PANEL PRINCIPAL
# ==========================================
st.title("🎯 Las Mejores Ofertas en Tiempo Real")
st.write("Catálogo actualizado de las grandes superficies de Colombia.")

# Espacio para Banner Publicitario Superior
st.markdown("""
    <div class="banner-publicidad">
        📢 <b>Espacio Publicitario Disponible</b> (Aquí se inserta el código de Google AdSense / Banner)
    </div>
""", unsafe_allow_html=True)

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

            # Insertar anuncio intercalado cada 6 productos
            if (idx + 1) % 6 == 0 and (idx + 1) < len(ofertas):
                st.markdown("""
                    <div class="banner-publicidad">
                        💵 <b>Anuncio Intercalado</b> (Bloque publicitario por impresión / clic)
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
    st.warning("Aún no hay ofertas recopiladas. La actualización automática se ejecuta a las 12:00 AM.")
