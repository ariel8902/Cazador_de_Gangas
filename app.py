import streamlit as st
import pandas as pd
from alkosto import extraer_alkosto
from exito import extraer_exito

# Configuración inicial de la página
st.set_page_config(
    page_title="Cazador de Gangas - Panel de Gestión",
    page_icon="🎯",
    layout="wide"
)

# Inicializar estados de la sesión para métricas y gestión
if 'vistas' not in st.session_state:
    st.session_state.vistas = 142
if 'clics' not in st.session_state:
    st.session_state.clics = 38
if 'gangas_guardadas' not in st.session_state:
    st.session_state.gangas_guardadas = []

# Incremento automático de vistas al cargar
st.session_state.vistas += 1

# --- BARRA LATERAL (GESTIÓN Y OPCIONES) ---
st.sidebar.title("⚙️ Gestión de Aplicación")

st.sidebar.markdown("### 📊 Métricas en Tiempo Real")
col_m1, col_m2 = st.sidebar.columns(2)
col_m1.metric("Vistas totales", st.session_state.vistas)
col_m2.metric("Clics en Ofertas", st.session_state.clics)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Control de Extractores")
almacen = st.sidebar.selectbox("Elija el almacén a rastrear:", ["Alkosto", "Éxito", "Falabella", "Ktronix"])

limite_ofertas = st.sidebar.slider("Número máximo de ofertas:", min_value=5, max_value=50, value=20)

btn_ejecutar = st.sidebar.button("🚀 Ejecutar Extracción")
btn_limpiar = st.sidebar.button("🗑️ Limpiar Historial")

if btn_limpiar:
    st.session_state.gangas_guardadas = []
    st.rerun()

# --- PANEL PRINCIPAL ---
st.title("🎯 Panel de Control: Cazador de Gangas (En Vivo)")
st.write("Gestiona la plataforma, analiza clics e interacciones y ejecuta la extracción masiva de ofertas.")

tab1, tab2, tab3 = st.tabs(["🔥 Ofertas Extraídas", "📈 Gestión y Analítica", "🤖 Bot de Telegram"])

with tab1:
    if btn_ejecutar:
        with st.spinner(f"Buscando gangas reales en {almacen}... Por favor espere."):
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
        df_gangas = pd.DataFrame(st.session_state.gangas_guardadas)
        st.dataframe(df_gangas, use_container_width=True)
        
        # Vista en tarjetas
        st.markdown("### Vista de Tarjetas")
        cols = st.columns(3)
        for idx, item in enumerate(st.session_state.gangas_guardadas):
            with cols[idx % 3]:
                st.image(item.get("Imagen", "https://via.placeholder.com/200"), width=180)
                st.subheader(item.get("Nombre", "Producto"))
                st.markdown(f"**Precio Oferta:** {item.get('Precio Oferta')}")
                st.markdown(f"**Descuento:** `{item.get('Descuento')}`")
                if st.button(f"Ver Oferta #{idx+1}", key=f"btn_{idx}"):
                    st.session_state.clics += 1
                    st.markdown(f"[Ir al producto]({item.get('Enlace Directo')})")
    else:
        st.info("👈 Seleccione el almacén en la barra lateral y presione 'Ejecutar Extracción' para cargar datos.")

with tab2:
    st.subheader("📊 Análisis de Rendimiento de la App")
    st.write("Estadísticas de uso y clics registrados en las campañas de ofertas.")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Visitas", st.session_state.vistas, "+12% hoy")
    col_b.metric("Total Clics Convertidos", st.session_state.clics, "+5 hoy")
    col_c.metric("CTR Promedio", f"{(st.session_state.clics / st.session_state.vistas * 100):.1f}%")

with tab3:
    st.subheader("🤖 Estado de Alertas por Telegram")
    st.write("Configuración del bot de envío automático a canales.")
    st.text_input("Bot Token:", value="123456789:ABCdefGHI...", type="password")
    st.text_input("Chat ID / Canal:", value="@CazadorGangasBot")
    st.button("Guardar Configuración de Telegram")
