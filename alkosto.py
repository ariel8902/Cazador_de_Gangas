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

            time.sleep(3.0)
            page.mouse.wheel(0, 1000)
            time.sleep(2.0)

            productos_links = page.query_selector_all("a[href*='/p/']")
            print(f"    📊 Enlaces encontrados: {len(productos_links)}")

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

                    # Extracción avanzada: Buscar tanto el texto interno como las etiquetas flotantes de descuento (-54%)
                    datos_tarjeta = link.evaluate("""el => {
                        let card = el.closest('li, div.product__item, div.grid-item') || el;
                        let text = card.innerText || '';
                        // Buscar elementos que parezcan etiquetas de descuento o porcentajes
                        let badges = card.querySelectorAll('span, div, p');
                        let badgeTexts = [];
                        badges.forEach(b => {
                            if (b.innerText.includes('%') || b.innerText.includes('-')) {
                                badgeTexts.push(b.innerText.trim());
                            }
                        });
                        return { text: text, badges: badgeTexts.join(' | ') };
                    }""")
                    
                    texto_completo = datos_tarjeta['text'] + " | " + datos_tarjeta['badges']
                    lineas = [l.strip() for l in texto_completo.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    nombre = next((l for l in lineas if len(l) > 8 and '$' not in l and '%' not in l), lineas[0])

                    # Buscar el porcentaje exacto (ej: -54%, 54%)
                    descuento_val = 0
                    match_pct = re.search(r'-?(\d+)\s*%', texto_completo)
                    if match_pct:
                        descuento_val = int(match_pct.group(1))

                    descuento_txt = f"-{descuento_val}%" if descuento_val > 0 else "Oferta"

                    # Extraer precios limpios omitiendo cuotas bajas (mínimo 150k para equipos reales)
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 150000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    precio_alto = precios_unicos[0]
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto

                    # Si no cogió porcentaje por texto pero hay diferencia de precios matemáticos
                    if descuento_val == 0 and precio_alto > precio_oferta and precio_alto > 0:
                        descuento_val = int(((precio_alto - precio_oferta) / precio_alto) * 100)
                        if descuento_val > 0:
                            descuento_txt = f"-{descuento_val}%"

                    # REGLA DE ORO: Exigir que tenga un descuento real del 50% o más (o el que detecte la etiqueta)
                    if descuento_val < 50:
                        continue

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")

                    print(f"    🔥 [OFERTA REAL {descuento_txt}] {nombre[:30]} | Oferta: {str_precio_oferta}")

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

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL GANGAS REALES: {len(ofertas)} ---\n")
    return ofertas
