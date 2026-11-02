import time
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    ofertas = []
    
    # URL directa de ofertas / liquidación general de Alkosto donde se concentra todo el descuento masivo
    urls_objetivo = [
        "https://www.alkosto.com/ofertas/c/ofertas-alkosto",
        "https://www.alkosto.com/tecnologia/c/BI_FE_104",
        "https://www.alkosto.com/electrodomesticos/c/BI_FE_105"
    ]

    enlaces_procesados = set()

    for url in urls_objetivo:
        try:
            print(f"\n--- [EXTRACTOR ALKOSTO] Barriendo sección de ofertas: {url} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass

            time.sleep(5.0)
            
            # Forzar múltiples scrolls hacia abajo para obligar a VTEX a cargar toda la vitrina completa
            for _ in range(5):
                page.mouse.wheel(0, 3000)
                time.sleep(2.0)

            # Extraer TODOS los enlaces de productos de la página sin importar la categoría
            productos_links = page.query_selector_all("a[href*='/p/']")
            print(f"    📊 Enlaces totales encontrados en esta sección: {len(productos_links)}")

            for link in productos_links:
                try:
                    href = link.get_attribute("href")
                    if not href or href in enlaces_procesados:
                        continue
                    
                    enlaces_procesados.add(href)
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"

                    # Evaluar el contenedor completo de la tarjeta o elemento
                    datos = link.evaluate("""el => {
                        let card = el.closest('div, li, article, section') || el;
                        let text = card.innerText || '';
                        let html = card.innerHTML || '';
                        let img = card.querySelector('img');
                        let imgSrc = img ? (img.src || img.getAttribute('data-src') || '') : '';
                        return { text: text, html: html, img: imgSrc };
                    }""")

                    contenido_total = datos['text'] + " " + datos['html']

                    # FILTRO LÁSER ESTRICTO: Exigir obligatoriamente el signo menos y un descuento >= 50%
                    match_pct = re.search(r'-\s*(5[0-9]|[6-9]\d|100)\s*%', contenido_total)
                    if not match_pct:
                        continue
                    
                    match_num = re.search(r'-\s*(\d+)\s*%', match_pct.group(0))
                    descuento_val = int(match_num.group(1)) if match_num else 50
                    descuento_txt = f"-{descuento_val}%"

                    # Extraer nombre del producto
                    lineas = [l.strip() for l in datos['text'].split('\n') if l.strip()]
                    nombre = next((l for l in lineas if len(l) > 10 and '$' not in l and '%' not in l), "Producto en Descuento Masivo")

                    # Extraer precios limpios
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

                    print(f"    🔥 [GANGÓN CAPTURADO {descuento_txt}] {nombre[:35]} | Oferta: {str_precio_oferta}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": img_final,
                        "Almacen": "Alkosto",
                        "Categoria": "Ofertas Masivas"
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error procesando sección: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL GANGAS REALES >=50%: {len(ofertas)} ---\n")
    return ofertas
