import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor de Alkosto con auditoría interna línea por línea
    para identificar qué filtro está descartando las tarjetas capturadas.
    """
    ofertas = []
    categorias_urls = [
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101"),
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            print(f"\n--- [AUDITORÍA ALKOSTO] Rastreando categoría: {cat_nombre} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"    ⚠️ Advertencia en carga de página: {e}")
                continue

            time.sleep(random.uniform(4.0, 5.0))
            page.mouse.wheel(0, 1200)
            time.sleep(2.0)

            productos = page.query_selector_all("div.product__item, div.ais-Hits-item, li.ais-Hits-item, div[class*='productGrid']")
            if len(productos) == 0:
                productos = page.query_selector_all("div[class*='product']")

            print(f"    📊 Tarjetas detectadas: {len(productos)}")

            for idx, card in enumerate(productos):
                try:
                    texto_tarjeta = card.inner_text()
                    if not texto_tarjeta or "Mostrando" in texto_tarjeta:
                        continue

                    # 1. Probar enlace
                    enlace_element = card.query_selector("a[href]")
                    href = enlace_element.get_attribute("href") if enlace_element else "Sin href"
                    
                    # 2. Probar precios
                    lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
                    precios_raw = [l for l in lineas if '$' in l]
                    precios_num = [limpiar_precio(p) for p in precios_raw if limpiar_precio(p) > 50000]

                    print(f"    [Tarjeta {idx+1}] Href: {href[:40]} | Precios encontrados: {precios_num}")

                    if not precios_num:
                        continue

                    # Asignar valores por defecto para asegurar captura inmediata en prueba
                    precio_alto = max(precios_num)
                    precio_oferta = min(precios_num)
                    nombre = lineas[0] if lineas else "Producto Alkosto"

                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href if href.startswith('/') else '/' + href}"

                    print(f"    ✅ ¡CAPTURADO CON ÉXITO! -> {nombre[:35]} | Oferta: ${precio_oferta:,.0f}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": f"${precio_alto:,.0f}".replace(",", "."),
                        "Precio Oferta": f"${precio_oferta:,.0f}".replace(",", "."),
                        "Descuento": "Oferta",
                        "Enlace Directo": enlace_producto,
                        "Imagen": "https://via.placeholder.com/200?text=Alkosto",
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception as ex:
                    print(f"    ❌ Error interno en tarjeta {idx+1}: {str(ex)}")
                    continue

            time.sleep(1.0)

        except Exception as e:
            print(f"--- [AUDITORÍA ALKOSTO] Error general en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [AUDITORÍA ALKOSTO] TOTAL OFERTAS CAPTURADAS: {len(ofertas)} ---\n")
    return ofertas
