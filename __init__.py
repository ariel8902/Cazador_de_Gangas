import time
import random
import re
import config
from notificador import enviar_alerta_telegram

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_ktronix(page, categoria, url_busqueda):
    print(f"\n[+] 🐝 Doña Abeja rastreando Ktronix - Categoría: {categoria}")
    page.goto(url_busqueda, timeout=60000, wait_until="domcontentloaded")
    
    time.sleep(random.uniform(2.5, 4.0))
    page.mouse.wheel(0, 500)
    time.sleep(1.5)
    
    productos = page.query_selector_all(".product__item, [class*='product-item']")
    print(f"    📊 Tarjetas detectadas en Ktronix: {len(productos)}")
    
    for card in productos[:10]:
        enlace_element = card.query_selector("a.product__item__top__link, a[href*='/p/']")
        enlace_producto = None
        
        if enlace_element:
            href = enlace_element.get_attribute("href")
            if href:
                href_limpio = href.strip()
                if href_limpio.startswith("http"):
                    enlace_producto = href_limpio
                else:
                    if not href_limpio.startswith("/"):
                        href_limpio = "/" + href_limpio
                    enlace_producto = f"https://www.ktronix.com{href_limpio}"

        if not enlace_producto or "/p/" not in enlace_producto:
            continue

        texto = card.inner_text().split('\n')
        lineas = [l.strip() for l in texto if l.strip()]
        
        nombre = None
        for linea in lineas:
            if not '$' in linea and len(linea) > 15 and not any(k in linea.lower() for k in ['envío', 'garantía', 'seguro', 'cuota']):
                nombre = linea
                break
        
        if not nombre:
            continue
        
        precios_raw = [l for l in lineas if '$' in l]
        precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 0]
        precios_unicos = list(dict.fromkeys(precios_num))
        
        if not precios_unicos:
            continue
            
        precio_max = max(precios_unicos)
        precios_validos = [p for p in precios_unicos if p >= (precio_max * 0.25)]
        
        if len(precios_validos) >= 2:
            precio_alto = max(precios_validos)
            
            if len(precios_validos) >= 3:
                precio_oferta_general = sorted(precios_validos)[1]
                precio_tarjeta = min(precios_validos)
                descuento_general = ((precio_alto - precio_oferta_general) / precio_alto) * 100
                
                if descuento_general >= config.UMBRAL_DESCUENTO_MINIMO:
                    print(f"    🔥 ¡DESFASE KTRONIX! {nombre[:45]}")
                    enviar_alerta_telegram(
                        config.TELEGRAM_BOT_TOKEN,
                        config.TELEGRAM_CHAT_ID,
                        "Ktronix",
                        categoria,
                        f"{nombre} (💳 Con Tarjeta Tienda: ${precio_tarjeta:,})",
                        precio_alto,
                        precio_oferta_general,
                        descuento_general,
                        enlace_producto
                    )
            else:
                precio_bajo = min(precios_validos)
                descuento = ((precio_alto - precio_bajo) / precio_alto) * 100
                
                if descuento >= config.UMBRAL_DESCUENTO_MINIMO:
                    print(f"    🔥 ¡DESFASE KTRONIX! {nombre[:45]}")
                    enviar_alerta_telegram(
                        config.TELEGRAM_BOT_TOKEN,
                        config.TELEGRAM_CHAT_ID,
                        "Ktronix",
                        categoria,
                        nombre,
                        precio_alto,
                        precio_bajo,
                        descuento,
                        enlace_producto
                    )
        time.sleep(random.uniform(0.3, 0.6))