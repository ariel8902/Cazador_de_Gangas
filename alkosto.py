import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor de Alkosto enfocado en datos reales y descuentos reales.
    Filtra cuotas y exige que exista una diferencia real entre precio normal y oferta.
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

                    # Filtrar líneas que sean basura o cuotas de financiación
                    lineas_validas = []
                    palabras_basura = ['cuota', 'meses', 'tasas', 'intereses', 'opiniones', 'agotado']
                    for l in lineas:
                        if not any(b in l.lower() for b in palabras_basura):
                            lineas_validas.append(l)

                    # Nombre del producto
                    nombre = next((l for l in lineas_validas if len(l) > 6 and '$' not in l), lineas_validas[0] if lineas_validas else "Producto Alkosto")

                    # Extraer precios limpios (mayores a $50.000 para evitar valores residuales)
                    precios_raw = [l for l in lineas_validas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 50000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    # REGLA DE ORO: Necesitamos al menos dos precios distintos (Precio Anterior y Precio Oferta)
                    if len(precios_unicos) < 2:
                        continue

                    precio_alto = precios_unicos[0]   # Precio de lista / tachado
                    precio_oferta = precios_unicos[-1] # Precio real de venta en rebaja

                    # Verificar que el descuento sea real (el precio alto debe superar al de oferta)
                    if precio_alto <= precio_oferta:
                        continue

                    descuento_pct = ((precio_alto - precio_oferta) / precio_alto) * 100
                    descuento_txt = f"-{int(descuento_pct)}%"

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")

                    print(f"    🔥 [OFERTA REAL {descuento_txt}] {nombre[:30]} | Normal: {str_precio_normal} -> Oferta: {str_precio_oferta}")

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

                except Exception:
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS REALES VALIDADAS: {len(ofertas)} ---\n")
    return ofertas
