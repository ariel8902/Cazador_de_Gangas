import time
import random
import re
import config
from notificador import enviar_alerta_telegram

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page, categoria, url_busqueda):
    print(f"\n[+] 🐝 Doña Abeja rastreando Alkosto (Precios Reales - Umbral Estricto 50%) - Categoría: {categoria}")
    lista_ofertas = []
    
    try:
        page.goto(url_busqueda, timeout=60000, wait_until="domcontentloaded")
    except Exception as e:
        print(f"    ⚠️ Advertencia en carga de página: {e}")
        return lista_ofertas
    
    time.sleep(random.uniform(4.0, 6.0))
    page.mouse.wheel(0, 1000)
    time.sleep(2.0)
    
    productos = page.query_selector_all("div.product__item, div.ais-Hits-item, li.ais-Hits-item, div[class*='productGrid']")
    if len(productos) == 0:
        productos = page.query_selector_all("div[class*='product']")
        
    print(f"    📊 Tarjetas totales detectadas en Alkosto: {len(productos)}")
    
    for card in productos:
        texto_tarjeta = card.inner_text()
        if "Mostrando" in texto_tarjeta or "resultados" in texto_tarjeta:
            continue
            
        enlace_element = card.query_selector("a[href*='/p/'], a.product__item__top__link")
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
                    enlace_producto = f"https://www.alkosto.com{href_limpio}"

        if not enlace_producto or "/p/" not in enlace_producto:
            continue

        lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
        if not lineas:
            continue
            
        nombre = None
        for linea in lineas:
            if not '$' in linea and len(linea) > 10 and not any(k in linea.lower() for k in ['envío', 'garantía', 'seguro', 'cuota', 'opiniones', 'agotado', 'mostrando']):
                nombre = linea
                break
        
        if not nombre:
            continue
        
        # Filtrar únicamente precios reales de productos (descartando cuotas menores a 100 mil)
        precios_raw = [l for l in lineas if '$' in l]
        precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 150000]
        precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)
        
        if len(precios_unicos) < 2:
            continue
            
        # El precio mayor es el normal y el menor válido es la oferta real
        precio_alto = precios_unicos[0]
        precio_oferta = precios_unicos[-1]
        
        if precio_oferta >= precio_alto:
            continue
            
        descuento = ((precio_alto - precio_oferta) / precio_alto) * 100
        
        # Filtro estricto: Descuento real entre el umbral y un límite lógico menor al 85% para evitar basura
        if config.UMBRAL_DESCUENTO_MINIMO <= descuento <= 85.0:
            print(f"    🔥 ¡GANGA REAL ALKOSTO ({descuento:.1f}%)! {nombre[:45]} | Normal: ${precio_alto:,} | Oferta: ${precio_oferta:,}")
            lista_ofertas.append({
                "Almacén": "Alkosto",
                "Categoría": categoria,
                "Producto": nombre,
                "Precio Normal": f"$ {precio_alto:,.0f}",
                "Precio Oferta": f"$ {precio_oferta:,.0f}",
                "Descuento": f"{descuento:.1f}%",
                "Enlace Directo": enlace_producto
            })
            
        time.sleep(random.uniform(0.1, 0.3))
        
    return lista_ofertas