import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor dinámico de Alkosto.
    Filtra estrictamente por porcentaje de descuento (>= 50%), sin importar el precio base.
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

                    # Obtener texto del bloque del producto
                    texto = link.evaluate("el => { let p = el.closest('div, li'); return p ? p.innerText : el.innerText; }") or ""
                    
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    nombre = next((l for l in lineas if len(l) > 6 and '$' not in l), lineas[0])

                    # Extraer precios
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 1000]
                    precios_unicos = sorted(list(dict.fromkeys(precios_num)), reverse=True)

                    if not precios_unicos:
                        continue

                    # Cálculo dinámico del descuento
                    precio_alto = precios_unicos[0]
                    precio_oferta = precios_unicos[-1] if len(precios_unicos) >= 2 else precio_alto
                    
                    descuento_pct = 0
                    if precio_alto > precio_oferta and precio_alto > 0:
                        descuento_pct = ((precio_alto - precio_oferta) / precio_alto) * 100
                    else:
                        # Buscar si hay texto con porcentaje explícito
                        for linea in lineas:
                            if '%' in linea:
                                match_pct = re.search(r'(\d+)%', linea)
                                if match_pct:
                                    val = float(match_pct.group(1))
                                    if val > descuento_pct:
                                    	descuento_pct = val

                    # REGLA DE ORO: Exigir al menos 50% de descuento real
                    if descuento_pct < 50:
                        continue

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")
                    descuento_txt = f"-{int(descuento_pct)}%"

                    print(f"    🔥 [OFERTA Válida {descuento_txt}] {nombre[:35]} -> Oferta: {str_precio_oferta}")

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

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS CON >=50% DESC: {len(ofertas)} ---\n")
    return ofertas
