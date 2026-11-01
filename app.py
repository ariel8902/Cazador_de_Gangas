import os
import json
import re
import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Cazador de Gangas > 50%",
    page_icon="🔥",
    layout="wide"
)

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

stats = cargar_metricas()
if "visita_registrada" not in st.session_state:
    stats["visitas"] += 1
    guardar_metricas(stats)
    st.session_state["visita_registrada"] = True

# Estilos CSS de alto impacto comercial
st.markdown("""
    <style>
    .card-producto {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        color: #333333;
        text-align: center;
        transition: transform 0.2s;
    }
    .badge-descuento {
        background-color: #d32f2f;
        color: white;
        padding: 5px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 15px;
    }
    .precio-normal {
        text-decoration: line-through;
        color: #888888;
        font-size: 13px;
    }
    .precio-oferta {
        color: #2e7d32;
        font-size: 19px;
        font-weight: bold;
    }
    .btn-comprar {
        display: inline-block;
        background-color: #d32f2f;
        color: white !important;
        padding: 9px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
        width: 100%;
    }
    .banner-publicidad {
        border: 2px dashed #bbbbbb;
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        color: #555555;
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

def obtener_porcentaje_num(texto_descuento):
    numeros = re.findall(r'\d+', str(texto_descuento))
    if numeros:
        return int(numeros[0])
    return 0

# ==========================================
# BARRA LATERAL (CONTROLES Y AUDITORÍA)
# ==========================================
st.sidebar.title("🔥 Cazador de Gangas")
st.sidebar.caption("Descuentos reales superiores al 50%")

modo_vista = st.sidebar.radio("Vista de navegación:", ["Catálogo Comercial 🛍️", "Tabla de Control 📊"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Filtros de Búsqueda")

# Filtro de Porcentaje Mínimo (Fijado por defecto en 50%)
desc_minimo = st.sidebar.slider("Descuento Mínimo (%):", min_value=30, max_value=80, value=50, step=5)

# Listas fijas de almacenes y categorías para asegurar que siempre aparezcan todos las opciones
lista_almacenes = ["Todos los Almacenes", "Éxito", "Alkosto", "Ktronix"]
lista_categorias = ["Todas las Categorías", "Tecnología", "Electrodomésticos", "Celulares"]

# Menús desplegables directos
cat_seleccionada = st.sidebar.selectbox("Seleccionar Categoría:", lista_categorias)
alm_seleccionado = st.sidebar.selectbox("Seleccionar Almacén:", lista_almacenes)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Auditoría de Tráfico")
st.sidebar.metric("Visitas Totales", stats["visitas"])
st.sidebar.metric("Clics en Ofertas", stats["clics_ofertas"])

# ==========================================
# PANEL PRINCIPAL (VITRINA COMERCIAL)
# ==========================================
st.title("🔥 Las Mejores Gangas de Colombia (≥ 50% DCTO)")
st.write("Verificamos y filtramos únicamente las rebajas más drásticas del mercado.")

# Banner Publicitario Superior
st.markdown("""
    <div class="banner-publicidad">
        📢 <b>Espacio Publicitario Destacado</b> (Banner AdSense / Impresiones Monetizadas)
    </div>
""", unsafe_allow_html=True)

todas_ofertas = cargar_ofertas_guardadas()

# Filtrar ofertas cruzadas (Porcentaje >= 50% + Categoría + Almacén)
ofertas_filtradas = []
for prod in todas_ofertas:
    pct = obtener_porcentaje_num(prod.get("Descuento", "0"))
    cat_prod = prod.get("Categoria", "General")
    alm_prod = prod.get("Almacen", "General")
    
    cumple_descuento = pct >= desc_minimo
    cumple_categoria = (cat_seleccionada == "Todas las Categorías") or (cat_prod.lower() == cat_seleccionada.lower())
    cumple_almacen = (alm_seleccionado == "Todos los Almacenes") or (alm_prod.lower() == alm_seleccionado.lower())
    
    if cumple_descuento and cumple_categoria and cumple_almacen:
        ofertas_filtradas.append(prod)

if ofertas_filtradas:
    if modo_vista == "Catálogo Comercial 🛍️":
        st.subheader(f"🛍️ Vitrina de Gangas ({len(ofertas_filtradas)} productos encontrados)")
        
        cols = st.columns(3)
        for idx, prod in enumerate(ofertas_filtradas):
            col = cols[idx % 3]
            with col:
                titulo = prod.get("Nombre", "Producto en oferta")
                precio_norm = prod.get("Precio Normal", "N/A")
                precio_ofe = prod.get("Precio Oferta", "N/A")
                descuento = prod.get("Descuento", "Oferta")
                enlace = prod.get("Enlace Directo", "#")
                imagen = prod.get("Imagen", "https://via.placeholder.com/200?text=Sin+Imagen")
                almacen_nombre = prod.get("Almacen", "Tienda")

                st.markdown(f"""
                    <div class="card-producto">
                        <img src="{imagen}" style="max-width: 100%; height: 180px; object-fit: contain; margin-bottom: 10px;">
                        <span class="badge-descuento">-{descuento}</span>
                        <h4 style="font-size: 14px; margin: 10px 0; height: 38px; overflow: hidden;">{titulo}</h4>
                        <p style="font-size: 11px; color: #666; margin-bottom: 5px;">📍 {almacen_nombre}</p>
                        <p class="precio-normal">Antes: {precio_norm}</p>
                        <p class="precio-oferta">Ahora: {precio_ofe}</p>
                        <a href="{enlace}" target="_blank" class="btn-comprar">Ver Ganga en la Tienda ➔</a>
                    </div>
                """, unsafe_allow_html=True)

            # Insertar anuncio publicitario intercalado cada 6 productos
            if (idx + 1) % 6 == 0 and (idx + 1) < len(ofertas_filtradas):
                st.markdown("""
                    <div class="banner-publicidad">
                        💵 <b>Bloque Publicitario Intercalado</b> (Monetización por Clic/Vista)
                    </div>
                """, unsafe_allow_html=True)

    else:
        st.subheader("📊 Tabla Interna de Control")
        df = pd.DataFrame(ofertas_filtradas)
        st.dataframe(
            df,
            column_config={
                "Enlace Directo": st.column_config.LinkColumn("Enlace de Compra", display_text="Abrir Oferta 🔗")
            },
            use_container_width=True
        )
else:
    st.info(f"No hay productos cargados que cumplan con los filtros seleccionados (≥ {desc_minimo}% descuento en {alm_seleccionado}). Pruebe cambiando los filtros del menú lateral.")
