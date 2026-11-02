import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor flexible y real de Alkosto.
    Captura nombre, el precio encontrado y el enlace directo sin descartes ciegos.
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

                    texto = link.evaluate("el => { let p = el.closest('div, li'); return p ? p.innerText : el.innerText; }") or ""
                    
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    # Extraer nombre válido (ignorando líneas cortas o precios)
                    nombre = next((l for l in lineas if len(l) > 8 and '$' not in l), lineas[0])

                    # Extraer precios limpios mayores a $50.000
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 50000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    # Tomar el precio principal encontrado
                    precio_val = precios_unicos[0]
                    str_precio = f"${precio_val:,.0f}".replace(",", ".")

                    print(f"    🔥 [REGISTRO REAL] {nombre[:35]} | Precio: {str_precio}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio,
                        "Precio Oferta": str_precio,
                        "Descuento": "Oferta",
                        "Enlace Directo": enlace_producto,
                        "Imagen": "https://via.placeholder.com/200?text=Alkosto",
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL REGISTROS VALIDADOS: {len(ofertas)} ---\n")
    return ofertas
