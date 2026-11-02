import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor definitivo de Alkosto.
    Fuerza la espera del renderizado dinámico para evitar capturar cascarones vacíos en GitHub Actions.
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
                page.goto(url, timeout=60000, wait_until="networkidle")
            except Exception:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # Espera explícita a que los enlaces de producto reales existan en el DOM
            try:
                page.wait_for_selector("a[href*='/p/']", timeout=15000)
            except Exception:
                pass

            # Scroll escalonado para disparar el lazy-loading de precios e imágenes
            for i in range(4):
                page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
                time.sleep(1.0)

            # Búsqueda directa sobre tarjetas que tengan enlace /p/ real
            tarjetas = page.query_selector_all("li.product__item, div.product__item, form.product-item")
            if not tarjetas:
                tarjetas = page.query_selector_all("li.ais-Hits-item, div.ais-Hits-item")

            print(f"    📊 Tarjetas reales detectadas en Alkosto ({cat_nombre}): {len(tarjetas)}")

            muestras = 0

            for card in tarjetas:
                try:
                    texto_tarjeta = card.inner_text()
                    if not texto_tarjeta or "Mostrando" in texto_tarjeta:
                        continue

                    # Enlace directo
                    enlace_elem = card.query_selector("a[href*='/p/']")
                    if not enlace_elem:
                        continue

                    href = enlace_elem.get_attribute("href")
                    if not href:
                        continue
                    
                    enlace_producto = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                    # Nombre
                    lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
                    nombre = None
                    palabras_omitir = ['envío', 'garantía', 'seguro', 'cuota', 'opiniones', 'agotado', 'mostrando', 'paga a cuotas']
                    
                    for linea in lineas:
                        if '$' not in linea and len(linea) > 8 and not any(k in linea.lower() for k in palabras_omitir):
                            nombre = linea
                            break

                    if not nombre:
                        continue

                    # Precios
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 100000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    precio_alto = precios_unicos[0]
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto

                    descuento_txt = "Oferta"
                    if precio_alto > precio_oferta:
                        pct = ((precio_alto - precio_oferta) / precio_alto) * 100
                        descuento_txt = f"-{pct:.0f}%"

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")

                    # Imagen
                    img_elem = card.query_selector("img")
                    imagen_url = "https://via.placeholder.com/200?text=Alkosto+Oferta"
                    if img_elem:
                        src = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                        if src and not any(b in src.lower() for b in ["logo", "banner", "svg", "icon"]):
                            imagen_url = src if src.startswith("http") else f"https:{src}"

                    if muestras < 3:
                        print(f"\n    🔥 [PRODUCTO POBLADO REAL] {nombre[:45]}")
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

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error general en categoría {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS REALES VALIDADAS: {len(ofertas)} ---\n")
    return ofertas
