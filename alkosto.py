import time

def extraer_alkosto(page):
    ofertas = []
    categorias_urls = [
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            print(f"\n--- [DIAGNÓSTICO ALKOSTO] Entrando a: {cat_nombre} ---")
            
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass

            time.sleep(4.0)
            page.mouse.wheel(0, 1500)
            time.sleep(2.0)

            # Buscar cualquier elemento que parezca una tarjeta de producto o contenedor VTEX
            tarjetas = page.query_selector_all("div.product__item, li.product-item, div.grid-item, [class*='summary'], [class*='product'], a[href*='/p/']")
            print(f"    📊 Total elementos encontrados en la página: {len(tarjetas)}")

            # Vamos a inspeccionar las primeras 3 tarjetas en detalle para ver su HTML real
            for i, item in enumerate(tarjetas[:3]):
                try:
                    html_tarjeta = item.evaluate("el => el.outerHTML")
                    print(f"\n--- HTML DE LA TARJETA #{i+1} ---")
                    print(html_tarjeta[:1500]) # Imprime los primeros 1500 caracteres del HTML de la tarjeta
                    print("-" * 50)
                except Exception as e:
                    print(f"Error leyendo tarjeta {i+1}: {str(e)}")

        except Exception as e:
            print(f"--- [DIAGNÓSTICO ALKOSTO] Error general: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO ALKOSTO] FIN DE LA PRUEBA ---")
    return ofertas
