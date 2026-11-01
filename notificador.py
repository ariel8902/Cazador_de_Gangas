import requests
import html

# Identificadores visuales por tienda
ICONOS_TIENDA = {
    "Alkosto": "🔴 Alkosto",
    "Ktronix": "🔵 Ktronix",
    "Éxito": "🟡 Éxito",
    "Falabella": "🟢 Falabella"
}

def enviar_alerta_telegram(bot_token, chat_id, tienda, categoria, nombre, precio_base, precio_oferta, descuento, enlace):
    enlace_limpio = enlace.strip()
    
    # Corregir la concatenación si falta la barra diagonal '/' después del dominio
    dominio_tienda = tienda.lower()
    if "exito" in dominio_tienda:
        dominio_tienda = "exito"
        
    if f"{dominio_tienda}.com" in enlace_limpio and f"{dominio_tienda}.com/" not in enlace_limpio:
        enlace_limpio = enlace_limpio.replace(f"{dominio_tienda}.com", f"{dominio_tienda}.com/")
    
    if not enlace_limpio.startswith("http"):
        if not enlace_limpio.startswith("/"):
            enlace_limpio = "/" + enlace_limpio
        enlace_limpio = f"https://www.{dominio_tienda}.com.co{enlace_limpio}" if dominio_tienda == "falabella" else f"https://www.{dominio_tienda}.com{enlace_limpio}"

    es_tarjeta_tienda = False
    precio_tarjeta_str = ""
    
    if "(💳 Con Tarjeta Tienda:" in nombre:
        partes = nombre.split("(💳 Con Tarjeta Tienda:")
        nombre_real = partes[0].strip()
        precio_tarjeta_str = partes[1].replace(")", "").strip()
        es_tarjeta_tienda = True
    else:
        nombre_real = nombre.strip()

    nombre_escapado = html.escape(nombre_real)
    tienda_con_icono = ICONOS_TIENDA.get(tienda, f"🏬 {tienda}")
    
    mensaje = (
        f"🚨 <b>¡ALERTA DE DESFASE DETECTADO!</b> 🚨\n\n"
        f"🏬 <b>Tienda:</b> {tienda_con_icono}\n"
        f"📦 <b>Categoría:</b> {categoria}\n"
        f"💻 <b>Producto:</b> <a href='{enlace_limpio}'><b>{nombre_escapado}</b></a>\n"
    )
    
    if es_tarjeta_tienda:
        mensaje += f"💳 <i>Precio Exclusivo Tarjeta Tienda: {precio_tarjeta_str}</i>\n"
        
    mensaje += (
        f"\n💵 <b>Precio Normal:</b> ${precio_base:,}\n"
        f"🔥 <b>Precio Oferta:</b> ${precio_oferta:,}\n"
        f"💥 <b>Descuento:</b> {descuento:.1f}%"
    )
    
    url_api = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url_api, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        return False