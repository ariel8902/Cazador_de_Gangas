import time
import random
import re
import config
from notificador import enviar_alerta_telegram

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_falabella(page, categoria, url_busqueda):
    print(f"\n[+] 🐝 Doña Abeja rastreando Falabella - Categoría: {categoria}")
    try:
        page.goto(url_busqueda, timeout=60000, wait_until="domcontentloaded")
    except Exception as e:
        print(f"    ⚠️ Advertencia en carga Falabella: {e}")
        
    time.sleep(random.uniform(3.5, 5.0))
    page.mouse.wheel(0, 600)
    time.sleep(1.5)
    
    productos = page.query_selector_all("div[id*='testId-pod'], div[class*='pod-item'], div.search-results-4-grid")
    print(f"    📊 Tarjetas detectadas en Falabella: {len(productos)}")
    
    for card in productos[:12]:
        enlace_element = card.query_selector("a[href*='/product/']")
        if not enlace_element:
            continue
            
        href = enlace_element.get_attribute("href")
        if not href:
            continue
            
        # Saneamiento quirúrgico definitivo: Extraer hasta el primer bloque limpio del producto (/falabella-co/product/ID/nombre)
        href_limpio = href.strip().split('?')[0]
        match = re.search(r'(/falabella-co/product/\d+/[^/?]+)', href_limpio)
        if match:
            enlace_producto = f"https://www.falabella.com.co{match.group(1)}"
        else:
            match_base = re.search(r'(/falabella-co/product/\d+)', href_limpio)
            if match_base:
                enlace_producto = f"https://www.falabella.com.co{match_base.group(1)}"
            else:
                enlace_producto = f"https://www.falabella.com.co{href_limpio}"
            
        texto = card.inner_text().split('\n')
        lineas = [l.strip() for l in texto if l.strip()]
        
        nombre = None
        for linea in lineas:
            if not '$' in linea and len(linea) > 12 and not any(k in linea.lower() for k in ['envío', 'agregar', 'patrocinado', 'por ']):
                nombre = linea
                break
                
        if not nombre:
            continue
            
        precios_raw = [l for l in lineas if '$' in l]
        precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 0]
        precios_unicos = list(dict.fromkeys(precios_num))
        
        if len(precios_unicos) < 2:
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
                    print(f"    🔥 ¡DESFASE FALABELLA! {nombre[:45]} -> URL LIMPIA: {enlace_producto}")
                    enviar_alerta_telegram(
                        config.TELEGRAM_BOT_TOKEN,
                        config.TELEGRAM_CHAT_ID,
                        "Falabella",
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
                    print(f"    🔥 ¡DESFASE FALABELLA! {nombre[:45]} -> URL LIMPIA: {enlace_producto}")
                    enviar_alerta_telegram(
                        config.TELEGRAM_BOT_TOKEN,
                        config.TELEGRAM_CHAT_ID,
                        "Falabella",
                        categoria,
                        nombre,
                        precio_alto,
                        precio_bajo,
                        descuento,
                        enlace_producto
                    )
        time.sleep(random.uniform(0.3, 0.6))