import time
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    ofertas = []
    
    # URL directa de ofertas masivas de Alkosto
    urls_objetivo = [
        "https://www.alkosto.com/ofertas/c/ofertas-alkosto"
    ]

    enlaces_procesados = set()

    for url in urls_objetivo:
        try:
            print(f"\n--- [EXTRACTOR ALKOSTO] Analizando sección de ofertas: {url} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass

            time.sleep(5.0)
            
            # Forzar scroll para cargar toda la vitrina de la página
            for _ in range(6):
                page.mouse.wheel(0, 4000)
                time.sleep(2.5)

            # Buscar todos los contenedores posibles de productos en la vitrina de VTEX
            tarjetas = page.query_selector_all("div.product__item, li.product-item, div.grid-item, div[class*='summary'], article, div[class*='product']")
            print(f"    📊 Tarjetas evaluadas en la vitrina: {len(tarjetas)}")

            for tarjeta in tarjetas:
                try:
                    # Extraer texto, HTML, enlace e imagen directamente del contenedor de la tarjeta
                    datos = tarjeta.evaluate("""el => {
                        let text = el.innerText || '';
                        let html = el.innerHTML || '';
                        let img = el.querySelector('img');
                        let imgSrc = img ? (img.src || img.getAttribute('data-src') || '') : '';
                        let a = el.querySelector('a[href*="/p/"]');
                        let href = a ? a.getAttribute('href') : '';
                        return { text: text, html: html, img: imgSrc, href: href };
                    }""")

                    if not datos['href'] or datos['href'] in enlaces_procesados:
                        continue
                    
                    enlaces_procesados.add(datos['href'])
                    enlace_producto = datos['href'] if datos['href'].startswith("http") else f"https://www.alkosto.com{datos['href']}"

                    contenido_total = datos['text'] + " " + datos['html']

                    # EXIGENCIA ESTRICTA: Buscar explícitamente el signo menos (-) seguido del número y el símbolo %
                    match_pct = re.search(r'-\s*(\d+)\s*%', contenido_total)
                    if not match_pct:
                        continue
                    
                    descuento_val = int(match_pct.group(1))
                    
                    # Filtro inflexible: El descuento debe ser estrictamente del 50% o más
                    if descuento_val < 50:
                        continue
                    
                    descuento_txt = f"-{descuento_val}%"

                    # Extraer el nombre del producto limpiando líneas vacías y basura
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

                    print(f"    🔥 [GANGÓN REAL CAPTURADO {descuento_txt}] {nombre[:35]} | Oferta: {str_precio_oferta}")

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
            print(f"--- [EXTRACTOR ALKOSTO] Error general en sección: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL GANGAS REALES con -50% o más: {len(ofertas)} ---\n")
    return ofertas
