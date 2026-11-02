import streamlit as st
import pandas as pd
from alkosto import extraer_alkosto
from exito import extraer_exito

# Configuración inicial de la página
st.set_page_config(
    page_title="Cazador de Gangas - Panel de Control",
    page_icon="🎯",
    layout="wide"
)

# Estilos CSS personalizados para mejorar el diseño
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #FF4B4B; margin-bottom: 5px; }
    .sub-title { font-size: 1rem; color: #FAFAFA; margin-bottom: 25px; }
    .stButton>button { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Inicializar estados de la sesión
if 'vistas' not in st.session_state:
    st.session_state.vistas = 150
if 'clics' not in st.session_state:
    st.session_state.clics = 38
if 'gangas_guardadas' not in st.session_state:
    st.session_state.gangas_guardadas = []
if 'bot_token' not in st.session_state:
    st.session_state.bot_token = ""
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = "@CazadorGangasBot"

# --- BARRA LATERAL (GESTIÓN Y OPCIONES) ---
st.sidebar.markdown("## ⚙️ **Gestión de Aplicación**")

st.sidebar.markdown("### 📊 **Métricas en Tiempo Real**")
col_m1, col_m2 = st.sidebar.columns(2)
col_m1.metric("👁️ Vistas", st.session_state.vistas, delta="+1")
col_m2.metric("🖱️ Clics", st.session_state.clics, delta="+3")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ **Control de Extractores**")
almacen = st.sidebar.selectbox("Elija el almacén a rastrear:", ["Alkosto", "Éxito", "Falabella", "Ktronix"])

limite_ofertas = st.sidebar.slider("Número máximo de ofertas:", min_value=5, max_value=50, value=20)

btn_ejecutar = st.sidebar.button("🚀 Ejecutar Extracción", use_container_width=True)
btn_limpiar = st.sidebar.button("🗑️ Limpiar Historial", use_container_width=True)

if btn_limpiar:
    st.session_state.gangas_guardadas = []
    st.rerun()

# --- PANEL PRINCIPAL ---
st.markdown("<div class='main-title'>🎯 Panel de Control: Cazador de Gangas (En Vivo)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Gestiona la plataforma, analiza clics e interacciones y ejecuta la extracción masiva de ofertas.</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔥 **Ofertas Extraídas**", "📈 **Gestión y Analítica**", "🤖 **Bot de Telegram**"])

with tab1:
    if btn_ejecutar:
        with st.spinner(f"Rastreando gangas reales en {almacen}... Por favor espere."):
            if almacen == "Alkosto":
                resultados = extraer_alkosto()
            elif almacen == "Éxito":
                resultados = extraer_exito()
            else:
                resultados = []

            if resultados:
                st.session_state.gangas_guardadas.extend(resultados[:limite_ofertas])
                st.success(f"¡Se capturaron {len(resultados)} gangas en {almacen}!")
            else:
                st.warning(f"No se obtuvieron resultados para {almacen} en esta ejecución.")

    if st.session_state.gangas_guardadas:
        st.markdown("### 🛒 **Catálogo de Ofertas Capturadas**")
        
        # Galería visual organizada por columnas
        cols = st.columns(3)
        for idx, item in enumerate(st.session_state.gangas_guardadas):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.image(item.get("Imagen", "https://via.placeholder.com/200"), use_container_width=True)
                    st.subheader(item.get("Nombre", "Producto"))
                    st.markdown(f"**Precio Normal:** ~{item.get('Precio Normal')}~")
                    st.markdown(f"**Precio Oferta:** `{item.get('Precio Oferta')}`")
                    st.markdown(f"**Descuento:** `{item.get('Descuento')}`")
                    if st.link_button(f"🔗 Ver Oferta #{idx+1}", item.get("Enlace Directo", "#")):
                        st.session_state.clics += 1
    else:
        st.info("👈 Seleccione el almacén en la barra lateral y presione 'Ejecutar Extracción' para cargar datos.")

with tab2:
    st.markdown("### 📊 **Rendimiento y Métricas de Uso**")
    st.write("Estadísticas consolidadas sobre el comportamiento de los usuarios.")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Visitas Registradas", st.session_state.vistas)
    col_b.metric("Total Clics Convertidos", st.session_state.clics)
    
    ctr = (st.session_state.clics / st.session_state.vistas * 100) if st.session_state.vistas > 0 else 0
    col_c.metric("Ratio de Clics (CTR)", f"{ctr:.1f}%")

with tab3:
    st.markdown("### 🤖 **Configuración de Alertas por Telegram**")
    st.write("Ajuste las credenciales del bot encargado de notificar las ofertas capturadas.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        token_input = st.text_input("Bot Token:", value=st.session_state.bot_token, type="password", placeholder="Ej: 123456789:ABCdef...")
    with col_t2:
        chat_input = st.text_input("Chat ID / Canal:", value=st.session_state.chat_id, placeholder="Ej: @CazadorGangasBot")
        
    if st.button("💾 Guardar Configuración de Telegram", type="primary"):
        st.session_state.bot_token = token_input
        st.session_state.chat_id = chat_input
        st.success("✅ Configuración guardada correctamente.")
