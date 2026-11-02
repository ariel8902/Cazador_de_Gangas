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
            print(f"\n--- [EXTRACTOR ALKOSTO] Analizando vitrina en: {cat_nombre} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass

            time.sleep(5.0)
            page.mouse.wheel(0, 2500)
            time.sleep(3.0)

            # Enfoque blindado: capturar todos los enlaces de productos directamente
            links_productos = page.query_selector_all("a[href*='/p/']")
            print(f"    📊 Enlaces de producto encontrados: {len(links_productos)}")

            enlaces_procesados = set()

            for link in links_productos:
                try:
                    href = link.get_attribute("href")
                    if not href or href in enlaces_procesados:
                        continue
                    
                    enlaces_procesados.add(href)
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"

                    # Subir dinámicamente al contenedor de la tarjeta para extraer texto e HTML completo
                    datos = link.evaluate("""el => {
                        let card = el.closest('li, div[class*="product"], div[class*="summary"], div[class*="item"], article') || el.parentElement;
                        let text = card ? (card.innerText || '') : el.innerText;
                        let html = card ? (card.innerHTML || '') : el.innerHTML;
                        let img = card ? card.querySelector('img') : null;
                        let imgSrc = img ? (img.src || img.getAttribute('data-src') || '') : '';
                        return { text: text, html: html, img: imgSrc };
                    }""")

                    contenido_total = datos['text'] + " " + datos['html']

                    # FILTRO LÁSER OBLIGATORIO: Exigir el signo menos (-) seguido de 50 a 100 y el símbolo %
                    match_pct = re.search(r'-\s*(5[0-9]|[6-9]\d|100)\s*%', contenido_total)
                    if not match_pct:
                        continue
                    
                    match_num = re.search(r'-\s*(\d+)\s*%', match_pct.group(0))
                    descuento_val = int(match_num.group(1)) if match_num else 50
                    descuento_txt = f"-{descuento_val}%"

                    # Extraer nombre del producto limpio
                    lineas = [l.strip() for l in datos['text'].split('\n') if l.strip()]
                    nombre = next((l for l in lineas if len(l) > 10 and '$' not in l and '%' not in l), "Equipo en Oferta Masiva")

                    # Extraer precios limpios (filtrando cuotas menores a 100k)
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 100000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    precio_alto = precios_unicos[0]
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")
                    img_final = datos['img'] if datos['img'].startswith("http") else "https://via.placeholder.com/200?text=Alkosto"

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

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL GANGAS REALES CAPTURADAS: {len(ofertas)} ---\n")
    return ofertas
