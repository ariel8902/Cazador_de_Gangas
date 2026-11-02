import time
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    ofertas = []
    categorias_urls = [
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101"),
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            print(f"\n--- [EXTRACTOR ALKOSTO] Rastreando ofertas en: {cat_nombre} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass

            time.sleep(3.0)
            page.mouse.wheel(0, 1000)
            time.sleep(2.0)

            productos_links = page.query_selector_all("a[href*='/p/']")
            print(f"    📊 Enlaces reales con /p/ encontrados: {len(productos_links)}")

            enlaces_procesados = set()

            for link in productos_links:
                try:
                    href = link.get_attribute("href")
                    if not href or href in enlaces_procesados:
                        continue
                    
                    enlaces_procesados.add(href)
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"

                    # Capturar imagen real del producto
                    img_url = "https://via.placeholder.com/200?text=Alkosto+Oferta"
                    try:
                        card_element = link.evaluate_handle("el => el.closest('li, div.product__item, div.grid-item') || el")
                        img_tag = card_element.as_element().query_selector("img")
                        if img_tag:
                            src = img_tag.get_attribute("src") or img_tag.get_attribute("data-src")
                            if src and src.startswith("http"):
                                img_url = src
                    except Exception:
                        pass

                    # Obtener texto del bloque del producto
                    texto = link.evaluate("el => { let p = el.closest('div, li'); return p ? p.innerText : el.innerText; }") or ""
                    
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    nombre = next((l for l in lineas if len(l) > 8 and '$' not in l), lineas[0])

                    # Buscar porcentaje de descuento
                    descuento_txt = "Oferta"
                    porcentaje_val = 0
                    for linea in lineas:
                        if '%' in linea:
                            match_pct = re.search(r'(\d+)\s*%', linea)
                            if match_pct:
                                val = int(match_pct.group(1))
                                if val > porcentaje_val:
                                    porcentaje_val = val
                                    descuento_txt = f"-{val}%"

                    # Extraer precios limpios
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 10000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    precio_alto = precios_unicos[0]
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto

                    if porcentaje_val == 0 and precio_alto > precio_oferta and precio_alto > 0:
                        porcentaje_val = int(((precio_alto - precio_oferta) / precio_alto) * 100)
                        if porcentaje_val > 0:
                            descuento_txt = f"-{porcentaje_val}%"

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")

                    print(f"    🔥 [OFERTA CAPTURADA] {nombre[:30]} | {descuento_txt} | Oferta: {str_precio_oferta}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": img_url,
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS EXTRAÍDAS: {len(ofertas)} ---\n")
    return ofertas
