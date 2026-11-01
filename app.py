import os
import json
import re
import streamlit as st

# ==========================================
# CONFIGURACIÓN PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Cazador de Gangas",
    page_icon="🔥",
    layout="wide"
)

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
    </style>
""", unsafe_allow_html=True)

# LECTURA DE DATOS DIRECTA SIN CACHÉ
def cargar_ofertas():
    archivo = "ofertas.json"
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def obtener_porcentaje_num(texto_descuento):
    if not texto_descuento:
        return 0
    numeros = re.findall(r'\d+', str(texto_descuento))
    if numeros:
        return int(numeros[0])
    return 0

todas_ofertas = cargar_ofertas()

# ==========================================
# MÉTRICAS Y SESIÓN
# ==========================================
if "visitas" not in st.session_state:
    st.session_state["visitas"] = 1
else:
    st.session_state["visitas"] += 1

if "clics" not in st.session_state:
    st.session_state["clics"] = 0

# Conteo por almacén normalizando tildes y minúsculas
conteo_exito = 0
conteo_alkosto = 0
conteo_ktronix = 0

for p in todas_ofertas:
    alm = str(p.get("Almacen", "")).lower()
    if "exito" in alm or "éxito" in alm:
        conteo_exito += 1
    elif "alkosto" in alm:
        conteo_alkosto += 1
    elif "ktronix" in alm:
        conteo_ktronix += 1

# ==========================================
# BARRA LATERAL
# ==========================================
st.sidebar.title("🔥 Cazador de Gangas")

# Visualización de métricas
col_v, col_c = st.sidebar.columns(2)
col_v.metric("👁️ Visitas", st.session_state["visitas"])
col_c.metric("🖱️ Clics", st.session_state["clics"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estado de Base de Datos")
st.sidebar.info(f"**Total en JSON:** {len(todas_ofertas)}\n- **Éxito:** {conteo_exito}\n- **Alkosto:** {conteo_alkosto}\n- **Ktronix:** {conteo_ktronix}")

st.sidebar.markdown("---")
desc_minimo = st.sidebar.slider("Descuento Mínimo (%):", min_value=0, max_value=80, value=0, step=5)

lista_almacenes = ["Todos los Almacenes", "Éxito", "Alkosto", "Ktronix"]
alm_seleccionado = st.sidebar.selectbox("Seleccionar Almacén:", lista_almacenes)

# ==========================================
# VITRINA PRINCIPAL
# ==========================================
st.title("🔥 Vitrina Multitienda de Gangas")

ofertas_filtradas = []
for prod in todas_ofertas:
    pct = obtener_porcentaje_num(prod.get("Descuento", "0"))
    alm_prod = str(prod.get("Almacen", "")).strip().lower()
    
    cumple_descuento = (pct >= desc_minimo) if pct > 0 else (desc_minimo == 0)
    
    if alm_seleccionado == "Todos los Almacenes":
        cumple_almacen = True
    else:
        target = alm_seleccionado.strip().lower()
        if target == "éxito":
            cumple_almacen = "exito" in alm_prod or "éxito" in alm_prod
        else:
            cumple_almacen = target in alm_prod

    if cumple_descuento and cumple_almacen:
        ofertas_filtradas.append(prod)

if ofertas_filtradas:
    st.subheader(f"Mostrando {len(ofertas_filtradas)} ofertas")
    cols = st.columns(3)
    for idx, prod in enumerate(ofertas_filtradas):
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
                <div class="card-producto">
                    <img src="{prod.get('Imagen', '')}" style="max-width: 100%; height: 160px; object-fit: contain;">
                    <span class="badge-descuento">{prod.get('Descuento', 'Oferta')}</span>
                    <h4 style="font-size: 13px; margin: 10px 0; height: 36px; overflow: hidden;">{prod.get('Nombre', '')}</h4>
                    <p style="font-size: 11px; color: #666;">📍 {prod.get('Almacen', '')}</p>
                    <p class="precio-normal">Antes: {prod.get('Precio Normal', 'N/A')}</p>
                    <p class="precio-oferta">Ahora: {prod.get('Precio Oferta', 'N/A')}</p>
                    <a href="{prod.get('Enlace Directo', '#')}" target="_blank" class="btn-comprar">Ver Ganga ➔</a>
                </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No hay productos que coincidan con el filtro seleccionado.")
