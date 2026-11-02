import time
import random
import re
import concurrent.futures
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def _ejecutar_en_hilo_exito(pagina_num, categoria_nombre, url_objetivo):
    ofertas = []
    
    # Determinar si se usa URL personalizada o el catálogo por defecto
    if url_objetivo and isinstance(url_objetivo, str) and url_objetivo.startswith("http"):
        categorias_urls = [(categoria_nombre or "Ofertas", url_objetivo)]
    else:
        categorias_urls = [
            ("Tecnología", "https://www.exito.com/tecnologia"),
            ("Electrodomésticos", "https://www.exito.com/electrodomesticos"),
            ("Celulares", "https://www.exito.com/celulares")
        ]

    with sync_playwright() as p:
        try:
            # Ventana visible (headless=False) para evitar bloqueos automáticos
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768}
            )
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            for cat_nombre, url in categorias_urls:
                try:
                    print(f"    [ÉXITO] Rastreando categoría: {cat_nombre} -> {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    # Desplazamiento progresivo para renderizado reactivo VTEX
                    for i in range(5):
                        page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
                        page.wait_for_timeout(1500)

                    content = page.content()
                    soup = BeautifulSoup(content, "html.parser")

                    # Captura de tarjetas de productos
                    productos = soup.find_all("article") or soup.find_all("div", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower()))
                    print(f"    📊 [{cat_nombre}] Tarjetas detectadas en pantalla: {len(productos)}")

                    for prod in productos:
                        try:
                            # Nombre del producto
                            nombre_elem = prod.find(["h3", "h2", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower() or "brand" in x.lower()))
                            nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                            # Enlace directo
                            link_elem = prod.find("a", href=True)
                            if not link_elem:
                                continue
                            enlace_raw = link_elem['href']
                            enlace = f"https://www.exito.com{enlace_raw}" if enlace_raw.startswith("/") else enlace_raw

                            # Imagen
                            img_elem = prod.find("img")
                            imagen_url = None
                            if img_elem:
                                imagen_url = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("srcset")
                                if imagen_url and imagen_url.startswith("//"):
                                    imagen_url = "https:" + imagen_url

                            # Parseo numérico por Regex
                            texto_tarjeta = prod.get_text(separator=" ", strip=True)
                            precios_raw = re.findall(r'\$\s*[\d\.\,]+', texto_tarjeta)
                            precios_num = []
                            for pr in precios_raw:
                                num = int(re.sub(r'[^\d]', '', pr))
                                if num > 10000:
                                    precios_num.append(num)

                            precios_num = sorted(list(set(precios_num)), reverse=True)
                            if not precios_num:
                                continue

                            precio_alto = precios_num[0]
                            precio_oferta = precios_num[-1] if len(precios_num) >= 2 else precio_alto

                            # Descuento
                            desc_elem = prod.find(["span", "div"], class_=lambda x: x and "discount" in x.lower())
                            if desc_elem:
                                descuento = desc_elem.get_text(strip=True)
                            else:
                                match_pct = re.search(r'([1-9][0-9])\s*%', texto_tarjeta)
                                descuento = f"-{match_pct.group(1)}%" if match_pct else "Oferta"

                            if nombre and enlace:
                                ofertas.append({
                                    "Nombre": nombre,
                                    "Precio Normal": f"${precio_alto:,.0f}".replace(",", "."),
                                    "Precio Oferta": f"${precio_oferta:,.0f}".replace(",", "."),
                                    "Descuento": descuento,
                                    "Enlace Directo": enlace,
                                    "Imagen": imagen_url or "https://via.placeholder.com/200?text=Exito+Oferta",
                                    "Almacen": "Éxito",
                                    "Categoria": cat_nombre
                                })
                        except Exception:
                            continue

                    time.sleep(random.uniform(2.0, 4.0))
                except Exception as e:
                    print(f"Error extrayendo {cat_nombre} en Éxito: {str(e)}")

            browser.close()
        except Exception as e:
            print(f"--- [Error crítico en Playwright Éxito] {str(e)} ---")

    unicas = {o['Enlace Directo']: o for o in ofertas}.values()
    return list(unicas)

def extraer_exito(pagina=1, categoria="Ofertas", url_busqueda="https://www.exito.com/ofertas"):
    print("\n--- [ÉXITO] Iniciando extractor en hilo aislado ---")
    
    # Manejo de tipos para evitar que un entero rompa la invocación de la página
    if isinstance(pagina, int):
        pag_num = pagina
        cat_str = categoria if isinstance(categoria, str) else "Ofertas"
        url_str = url_busqueda if isinstance(url_busqueda, str) and url_busqueda.startswith("http") else "https://www.exito.com/ofertas"
    else:
        pag_num = 1
        cat_str = "Ofertas"
        url_str = "https://www.exito.com/ofertas"

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_ejecutar_en_hilo_exito, pag_num, cat_str, url_str)
        try:
            return future.result(timeout=90)
        except Exception as e:
            print(f"--- [Error de Timeout/Hilo Éxito] {str(e)} ---")
            return []
