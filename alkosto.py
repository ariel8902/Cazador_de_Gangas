import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor definitivo de Alkosto.
    Extrae nombre, precios y enlaces directamente desde los elementos encontrados.
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

            try:
                page.wait_for_selector("a[href*='/p/']", timeout=15000)
            except Exception:
                pass

            for i in range(3):
                page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
                time.sleep(1.2)

            productos_links = page.query_selector_all("a[href*='/p/']")
            print(f"    📊 Enlaces reales con /p/ encontrados: {len(productos_links)}")

            muestras = 0
            enlaces_procesados = set()

            for link in productos_links:
                try:
                    href = link.get_attribute("href")
                    if not href or href in enlaces_procesados:
                        continue
                    
                    enlaces_procesados.add(href)
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"

                    # Obtener el texto completo del bloque que envuelve al enlace de forma segura
                    texto_bloque = link.evaluate("el => { let p = el.closest('div, li'); return p ? p.innerText : el.innerText; }") or ""
                    
                    if not texto_bloque.strip():
                        continue

                    lineas = [l.strip() for l in texto_bloque.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    # Extraer nombre (primera línea larga que no sea precio ni basura)
                    nombre = None
                    palabras_omitir = ['envío', 'garantía', 'seguro', 'cuota', 'opiniones', 'agotado', '$']
                    for linea in lineas:
                        if len(linea) > 8 and not any(k in linea.lower() for k in palabras_omitir):
                            nombre = linea
                            break

                    if not nombre and lineas:
                        nombre = lineas[0]

                    # Extraer precios
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 50000]
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

                    if muestras < 3:
                        print(f"\n    🔥 [OFERTA CAPTURADA] {nombre[:40]}")
                        print(f"       -> Oferta: {str_precio_oferta} | Normal: {str_precio_normal}")
                        print(f"       -> Enlace: {enlace_producto[:60]}...")
                        muestras += 1

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": "https://via.placeholder.com/200?text=Alkosto+Oferta",
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception as ex:
                    # Imprimir error exacto si un producto falla, para no dejarlo a ciegas
                    # print(f"    ⚠️ Error en producto: {ex}")
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error general en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS REALES VALIDADAS: {len(ofertas)} ---\n")
    return ofertas
