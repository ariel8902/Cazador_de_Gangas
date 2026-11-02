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
            print(f"\n--- [EXTRACTOR ALKOSTO] Cazando ofertas reales en: {cat_nombre} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass

            time.sleep(4.0)
            page.mouse.wheel(0, 1200)
            time.sleep(2.0)

            # Buscar contenedores de productos de Alkosto
            productos = page.query_selector_all("div.product__item, li.product-item, div.grid-item, .vtex-product-summary-2-x-element")
            if not productos:
                # Plan de respaldo: buscar por enlaces si la clase cambia
                productos = [link.evaluate_handle("el => el.closest('li, div') || el") for link in page.query_selector_all("a[href*='/p/']")]

            print(f"    📊 Tarjetas de producto encontradas: {len(productos)}")

            enlaces_procesados = set()

            for item in productos:
                try:
                    # Extraer enlace y nombre
                    link_elem = item.query_selector("a[href*='/p/']") if hasattr(item, 'query_selector') else item
                    if not link_elem:
                        continue
                    
                    href = link_elem.get_attribute("href")
                    if not href or href in enlaces_procesados:
                        continue
                    
                    enlaces_procesados.add(href)
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"

                    # Extraer texto de la tarjeta y buscar insignias de descuento (-54%)
                    info_tarjeta = item.evaluate("""el => {
                        let text = el.innerText || '';
                        let badge = el.querySelector('.vtex-product-highlights-2-x-productHighlightText, [class*="discount"], [class*="badge"], span');
                        let badgeText = badge ? badge.innerText : '';
                        
                        let img = el.querySelector('img');
                        let imgSrc = img ? (img.src || img.getAttribute('data-src')) : '';
                        
                        return { text: text, badge: badgeText, img: imgSrc };
                    }""")

                    texto_total = info_tarjeta['text'] + " " + info_tarjeta['badge']
                    lineas = [l.strip() for l in texto_total.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    # Nombre limpio del producto
                    nombre = next((l for l in lineas if len(l) > 10 and '$' not in l and '%' not in l), lineas[0])

                    # Detectar porcentaje de descuento explícito (ej: -54%)
                    descuento_val = 0
                    match_pct = re.search(r'-?(\d+)\s*%', texto_total)
                    if match_pct:
                        descuento_val = int(match_pct.group(1))

                    descuento_txt = f"-{descuento_val}%" if descuento_val > 0 else "Oferta"

                    # Extraer precios limpios (excluyendo cuotas menores a 100k)
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 100000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    precio_alto = precios_unicos[0]
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto

                    # Si no hay porcentaje por texto pero hay diferencia de precios
                    if descuento_val == 0 and precio_alto > precio_oferta and precio_alto > 0:
                        descuento_val = int(((precio_alto - precio_oferta) / precio_alto) * 100)
                        if descuento_val > 0:
                            descuento_txt = f"-{descuento_val}%"

                    # REGLA DE ORO: Solo dejar pasar ofertas reales con descuento >= 50%
                    if descuento_val < 50:
                        continue

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")
                    img_final = info_tarjeta['img'] if info_tarjeta['img'].startswith("http") else "https://via.placeholder.com/200?text=Alkosto"

                    print(f"    🔥 [GANGÓN CAPTURADO {descuento_txt}] {nombre[:30]} | Oferta: {str_precio_oferta}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": img_final,
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL GANGAS REALES >=50%: {len(ofertas)} ---\n")
    return ofertas
