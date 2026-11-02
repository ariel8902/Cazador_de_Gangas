import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Diagnóstico con trazas activas para Alkosto.
    Imprime la razón exacta por la que se descarta cada tarjeta.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [DIAGNÓSTICO AUDITORIA] Rastreando Alkosto Celulares ---")
        page.goto(url_prueba, timeout=60000, wait_until="domcontentloaded")
        
        time.sleep(4.0)
        page.mouse.wheel(0, 1200)
        time.sleep(2.0)

        productos = page.query_selector_all("div.product__item, div.ais-Hits-item, li.ais-Hits-item, div[class*='productGrid']")
        if len(productos) == 0:
            productos = page.query_selector_all("div[class*='product']")

        print(f"    📊 Tarjetas totales detectadas: {len(productos)}")

        for idx, card in enumerate(productos):
            print(f"\n--- [AUDITANDO TARJETA {idx + 1}] ---")
            texto_tarjeta = card.inner_text()
            
            # Buscar cualquier enlace interno en la tarjeta
            enlaces = card.query_selector_all("a")
            hrefs = [e.get_attribute("href") for e in enlaces if e.get_attribute("href")]
            print(f"  -> URLs encontradas en la tarjeta: {hrefs}")

            # Precios en la tarjeta
            lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
            precios_raw = [l for l in lineas if '$' in l]
            print(f"  -> Precios brutos en texto: {precios_raw}")

            # Intentar extracción directa sin filtros estrictos para ver si la tarjeta es válida
            enlace_valido = None
            for h in hrefs:
                if "/p/" in h or "/celulares/" in h:
                    enlace_valido = f"https://www.alkosto.com{h}" if h.startswith("/") else h
                    break
            
            if not enlace_valido and hrefs:
                enlace_valido = f"https://www.alkosto.com{hrefs[0]}" if hrefs[0].startswith("/") else hrefs[0]

            # Nombre
            nombre = lineas[0] if lineas else "Producto sin nombre"

            # Precios
            precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 50000]
            
            if enlace_valido and precios_num:
                precio_oferta = f"${min(precios_num):,.0f}".replace(",", ".")
                precio_normal = f"${max(precios_num):,.0f}".replace(",", ".")
                
                print(f"  ✅ ¡TARJETA APROBADA! -> {nombre[:40]} | Precio: {precio_oferta}")
                
                ofertas.append({
                    "Nombre": nombre,
                    "Precio Normal": precio_normal,
                    "Precio Oferta": precio_oferta,
                    "Descuento": "Oferta",
                    "Enlace Directo": enlace_valido,
                    "Imagen": "https://via.placeholder.com/200?text=Alkosto",
                    "Almacen": "Alkosto",
                    "Categoria": "Celulares"
                })
            else:
                print(f"  ❌ DESCHAZADA -> Motivo: Enlace válido={bool(enlace_valido)}, Precios numéricos={precios_num}")

    except Exception as e:
        print(f"--- [DIAGNÓSTICO AUDITORIA] Error: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO AUDITORIA] TOTAL OFERTAS REALES CAPTURADAS: {len(ofertas)} ---\n")
    return ofertas
