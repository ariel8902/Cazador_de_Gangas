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
            print(f"\n--- [EXTRACTOR ALKOSTO] Buscando gangas >=50% en: {cat_nombre} ---")
            
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

                    # Capturar imagen real
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

                    # Obtener texto del bloque
                    texto = link.evaluate("el => { let p = el.closest('div, li'); return p ? p.innerText : el.innerText; }") or ""
                    
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    nombre = next((l for l in lineas if len(l) > 8 and '$' not in l), lineas[0])

                    # REGLA DE ORO: Buscar explícitamente el porcentaje de descuento en el texto
                    descuento_val = 0
                    for linea in lineas:
                        if '%' in linea:
                            match_pct = re.search(r'(\d+)\s*%', linea)
                            if match_pct:
                                val = int(match_pct.group(1))
                                if val > descuento_val:
                                    descuento_val = val

                    # Si no encuentra un porcentaje impreso, calculamos con los precios del bloque
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 100000] # Omitir valores menores a 100k (cuotas)
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if len(precios_unicos) >= 2:
                        p_alto = precios_unicos[0]
                        p_oferta = precios_unicos[-1]
                        if p_alto > p_oferta and p_alto > 0:
                            calc_pct = int(((p_alto - p_oferta) / p_alto) * 100)
                            if calc_pct > descuento_val:
                                descuento_val = calc_pct

                    # FILTRO ESTRICTO: Si el descuento es menor al 50%, SE DESCARTA DE UNA VEZ
                    if descuento_val < 50:
                        continue

                    precio_alto = precios_unicos[0] if precios_unicos else 0
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")
                    descuento_txt = f"-{descuento_val}%"

                    print(f"    🔥 [GANGA REAL {descuento_txt}] {nombre[:30]} | Oferta: {str_precio_oferta}")

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

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL GANGAGAS >=50%: {len(ofertas)} ---\n")
    return ofertas
