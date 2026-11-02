import time
import random
import re

def limpiar_precio(texto_precio):
    numeros = re.sub(r'[^\d]', '', texto_precio)
    return int(numeros) if numeros else 0

def extraer_alkosto(page):
    """
    Extractor de Alkosto de ataque directo.
    Captura cualquier enlace con '/p/' y extrae el primer precio que encuentre.
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

                    # Obtener texto del enlace o de su contenedor inmediato
                    texto = link.evaluate("el => { let p = el.closest('div, li'); return p ? p.innerText : el.innerText; }") or ""
                    
                    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                    if not lineas:
                        continue

                    # Nombre por defecto la primera línea con texto decente
                    nombre = next((l for l in lineas if len(l) > 6 and '$' not in l), lineas[0])

                    # Buscar cualquier precio válido
                    precios = [limpiar_precio(l) for l in lineas if '$' in l and limpiar_precio(l) > 10000]
                    precios = sorted(list(dict.fromkeys(precios)), reverse=True)

                    if not precios:
                        continue

                    precio_alto = precios[0]
                    precio_oferta = precios[-1] if len(precios) >= 2 else precio_alto

                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")

                    print(f"    🔥 [CAPTURADO] {nombre[:35]} -> Oferta: {str_precio_oferta}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
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

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL OFERTAS VALIDADAS: {len(ofertas)} ---\n")
    return ofertas
