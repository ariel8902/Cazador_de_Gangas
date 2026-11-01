import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor definitivo de Alkosto basado en la lógica funcional comprobada.
    Extrae ofertas reales mediante Playwright directo y filtrado por cuotas mayores a $150.000.
    """
    ofertas = []
    categorias_urls = [
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101"),
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            print(f"\n--- [EXTRACTOR ALKOSTO] Rastreando categoría: {cat_nombre} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"    ⚠️ Advertencia en carga de página: {e}")
                continue

            time.sleep(random.uniform(4.0, 5.0))
            page.mouse.wheel(0, 1000)
            time.sleep(2.0)

            # Selectores de grilla nativa probados
            productos = page.query_selector_all("div.product__item, div.ais-Hits-item, li.ais-Hits-item, div[class*='productGrid']")
            if len(productos) == 0:
                productos = page.query_selector_all("div[class*='product']")

            print(f"    📊 Tarjetas totales detectadas en Alkosto ({cat_nombre}): {len(productos)}")

            muestras = 0

            for card in productos:
                try:
                    texto_tarjeta = card.inner_text()
                    if "Mostrando" in texto_tarjeta or "resultados" in texto_tarjeta:
                        continue

                    # 1. Enlace directo al producto (Debe incluir /p/)
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

                    # 2. Extracción de Nombre desde el texto interno de la tarjeta
                    lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    nombre = None
                    palabras_omitir = ['envío', 'garantía', 'seguro', 'cuota', 'opiniones', 'agotado', 'mostrando', 'paga a cuotas']
                    for linea in lineas:
                        if '$' not in linea and len(linea) > 10 and not any(k in linea.lower() for k in palabras_omitir):
                            nombre = linea
                            break

                    if not nombre:
                        continue

                    # 3. Filtrar precios reales (descartando cuotas menores a $150.000)
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 150000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    precio_alto = 0
                    precio_oferta = 0

                    if len(precios_unicos) >= 2:
                        precio_alto = precios_unicos[0]
                        precio_oferta = precios_unicos[-1]
                    elif len(precios_unicos) == 1:
                        precio_oferta = precios_unicos[0]
                        precio_alto = precio_oferta

                    # 4. Cálculo de descuento o etiqueta de oferta
                    descuento_txt = "Oferta"
                    if precio_alto > precio_oferta and precio_alto > 0:
                        pct = ((precio_alto - precio_oferta) / precio_alto) * 100
                        descuento_txt = f"-{pct:.0f}%"

                    # Formateo de precios para la vitrina
                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".") if precio_alto > 0 else "N/A"
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".") if precio_oferta > 0 else "N/A"

                    # 5. Intentar capturar la imagen real del producto
                    img_elem = card.query_selector("img")
                    imagen_url = "https://via.placeholder.com/200?text=Alkosto+Oferta"
                    if img_elem:
                        src = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                        if src and not any(b in src.lower() for b in ["logo", "banner", "svg", "icon"]):
                            imagen_url = src if src.startswith("http") else f"https:{src}"

                    # Impresión en log de los 3 primeros productos limpios
                    if muestras < 3:
                        print(f"\n    🔥 [GANGA REAL ALKOSTO] {nombre[:45]}")
                        print(f"       -> Oferta: {str_precio_oferta} | Normal: {str_precio_normal} ({descuento_txt})")
                        print(f"       -> Enlace: {enlace_producto[:60]}...")
                        muestras += 1

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": imagen_url,
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

            time.sleep(random.uniform(1.0, 2.0))

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error general en categoría {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS REALES VALIDADAS: {len(ofertas)} ---\n")
    return ofertas
