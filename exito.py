import time
import random
import re
import config
from notificador import enviar_alerta_telegram

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_exito(page, categoria, url_busqueda):
    print(f"\n[+] 🐝 Doña Abeja rastreando Éxito (Barrido Completo - Umbral Estricto 50%) - Categoría: {categoria}")
    lista_ofertas = []
    
    try:
        page.goto(url_busqueda, timeout=60000, wait_until="networkidle")
    except Exception as e:
        print(f"    ⚠️ Advertencia en carga de página: {e}")
        return lista_ofertas
    
    time.sleep(random.uniform(4.0, 6.0))
    page.mouse.wheel(0, 1000)
    time.sleep(2.0)
    
    productos = page.query_selector_all("article, [data-render-result='true'], div[class*='productCard']")
    print(f"    📊 Tarjetas totales detectadas en Éxito: {len(productos)}")
    
    # BARRIDO COMPLETO DE TODAS LAS TARJETAS (Sin recortar a 12)
    for card in productos:
        enlace_element = card.query_selector("a[href*='/p'], a[data-testid='product-link']")
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
                    enlace_producto = f"https://www.exito.com{href_limpio}"
        
        if not enlace_producto:
            continue
            
        texto = card.inner_text().split('\n')
        lineas = [l.strip() for l in texto if l.strip()]
        
        nombre = None
        for linea in lineas:
            if not '$' in linea and len(linea) > 12 and not any(k in linea.lower() for k in ['envío', 'agregar', 'vendido', 'descuento', 'oferta']):
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
                
                # APLICACIÓN ESTRICTA DEL UMBRAL CONFIGURADO EN CONFIG.PY (50.0%)
                if descuento_general >= config.UMBRAL_DESCUENTO_MINIMO:
                    print(f"    🔥 ¡GANGA REAL ÉXITO ({descuento_general:.1f}%)! {nombre[:45]}")
                    lista_ofertas.append({
                        "Almacén": "Éxito",
                        "Categoría": categoria,
                        "Producto": f"{nombre} (💳 Con Tarjeta Tienda: ${precio_tarjeta:,})",
                        "Precio Normal": f"$ {precio_alto:,.0f}",
                        "Precio Oferta": f"$ {precio_oferta_general:,.0f}",
                        "Descuento": f"{descuento_general:.1f}%",
                        "Enlace Directo": enlace_producto
                    })
            else:
                precio_bajo = min(precios_validos)
                descuento = ((precio_alto - precio_bajo) / precio_alto) * 100
                
                if descuento >= config.UMBRAL_DESCUENTO_MINIMO:
                    print(f"    🔥 ¡GANGA REAL ÉXITO ({descuento:.1f}%)! {nombre[:45]}")
                    lista_ofertas.append({
                        "Almacén": "Éxito",
                        "Categoría": categoria,
                        "Producto": nombre,
                        "Precio Normal": f"$ {precio_alto:,.0f}",
                        "Precio Oferta": f"$ {precio_bajo:,.0f}",
                        "Descuento": f"{descuento:.1f}%",
                        "Enlace Directo": enlace_producto
                    })
        time.sleep(random.uniform(0.1, 0.3))
        
    return lista_ofertas