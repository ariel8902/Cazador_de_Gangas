import streamlit as st
import pandas as pd
import config
from notificador import enviar_alerta_telegram

# Importar los extractores
from exito import extraer_exito
from ktronix import extraer_ktronix
from alkosto import extraer_alkosto

# Configuración inicial de la página
st.set_page_config(
    page_title="Cazador de Gangas (En Vivo)",
    page_icon="🎯",
    layout="wide"
)

# Inicializar el acumulador global en la sesión si no existe
if "historial_ofertas" not in st.session_state:
    st.session_state["historial_ofertas"] = []

st.markdown("""
    <h1 style='color: #FF4B4B;'>🎯 Panel de Control: Cazador de Gangas (En Vivo)</h1>
    <p style='font-size: 16px; color: #CCCCCC;'>Seleccione el almacén que desea rastrear, pulse el botón y Doña Abeja traerá las ofertas reales directamente a su pantalla.</p>
""", unsafe_allow_html=True)

# Barra lateral de control
st.sidebar.markdown("## Control de Extractores")
almacen_seleccionado = st.sidebar.selectbox(
    "Elija el almacén a rastrear:",
    ["Éxito", "Ktronix", "Alkosto", "Todos"]
)

# Botones de control en la barra lateral
col_btn1, col_btn2 = st.sidebar.columns(2)
ejecutar = col_btn1.button("🚀 Ejecutar Extracción")
limpiar = col_btn2.button("🗑️ Limpiar Historial")

if limpiar:
    st.session_state["historial_ofertas"] = []
    st.sidebar.success("¡Historial limpiado con éxito!")
    st.rerun()

# Lógica de ejecución de extracción
if ejecutar:
    with st.spinner("Conectando con los servidores y rastreando ofertas..."):
        nuevas_ofertas = []
        
        # Simulación de navegador Playwright (importar Playwright síncrono según su implementación)
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Recorrer el catálogo de objetivos según la selección
            for objetivo in config.CATALOGO_OBJETIVOS:
                tienda = objetivo["tienda"]
                if almacen_seleccionado != "Todos" and tienda != almacen_seleccionado:
                    continue
                
                categoria = objetivo["categoria"]
                url = objetivo["url"]
                
                try:
                    if tienda == "Éxito":
                        resultados = extraer_exito(page, categoria, url)
                    elif tienda == "Ktronix":
                        resultados = extraer_ktronix(page, categoria, url)
                    elif tienda == "Alkosto":
                        resultados = extraer_alkosto(page, categoria, url)
                    else:
                        resultados = []
                        
                    if resultados:
                        nuevas_ofertas.extend(resultados)
                except Exception as e:
                    print(f"Error procesando {tienda} - {categoria}: {e}")
                    
            browser.close()
            
        # Acumular las nuevas ofertas al historial existente sin borrar lo anterior
        if nuevas_ofertas:
            st.session_state["historial_ofertas"].extend(nuevas_ofertas)
            st.success(f"¡Extracción finalizada! Se añadieron {len(nuevas_ofertas)} nuevas ofertas al historial.")
        else:
            st.warning("¡Extracción finalizada! No se encontraron ofertas nuevas que cumplan el umbral estricto en esta pasada.")

# Área Principal: Visualización Acumulada de Ofertas
if st.session_state["historial_ofertas"]:
    df = pd.DataFrame(st.session_state["historial_ofertas"])
    # Eliminar duplicados exactos si los hubiera
    df = df.drop_duplicates(subset=["Producto", "Precio Oferta", "Almacén"])
    
    st.markdown(f"### 📊 Historial Consolidado de Ofertas Detectadas (Total acumulado: {len(df)})")
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 Acceso Rápido para Copiar al WhatsApp")
    for idx, row in df.iterrows():
        texto_whatsapp = f"🔥 *[{row['Almacén']}] {row['Producto']}* \n💰 Precio Normal: *{row['Precio Normal']}* \n⚡ Precio Oferta: *{row['Precio Oferta']}* \n📉 Descuento: *{row['Descuento']}* \n🔗 Enlace: {row['Enlace Directo']}"
        with st.expander(f"[{row['Almacén']}] {row['Producto'][:60]}... - Descuento: {row['Descuento']}"):
            st.code(texto_whatsapp, language="markdown")
else:
    st.info("👈 Seleccione el almacén en la barra lateral y presione 'Ejecutar Extracción' para comenzar a acumular gangas.")