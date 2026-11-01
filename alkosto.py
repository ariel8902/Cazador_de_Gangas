import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Prueba directa en Alkosto mediante Playwright.
    Filtra estrictamente productos descartando menús o enlaces inválidos.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [DIAGNÓSTICO ALKOSTO NAV] Conectando a: {url_prueba} ---")
        page.goto(url_prueba, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll escalonado idéntico al de Éxito
        for i in range(4):
            page.evaluate(f"window.scrollTo(0, {i * 700});")
            time.sleep(1)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Recorrido de contenedores generales
        productos = (
            soup.find_all("form", class_=lambda x: x and "product" in x.lower()) or
            soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
            soup.find_all("div", class_=lambda x: x and "product" in x.lower())
        )

        print(f"--- [DIAGNÓSTICO ALKOSTO NAV] Elementos extraídos del HTML: {len(productos)} ---")

        muestras = 0
        palabras_invalidas = [
            "mi cuenta", "mi perfil", "direcciones", "mis pedidos", 
            "paga a cuotas", "0% interés", "favoritos", "servicio al cliente", "carro de compras"
        ]

        for prod in productos:
            try:
                # Extracción de título
                nombre_elem = prod.find(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                # Filtro de seguridad contra menús
                if not nombre or len(nombre) < 6 or any(bad in nombre.lower() for bad in palabras_invalidas):
                    continue

                # Extracción de enlace de producto (debe terminar en /p/ o contener producto)
                link_elem = prod.find("a", href=True)
                if not link_elem:
                    continue
                
                href = link_elem['href']
                enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                # Precios
                precios = prod.find_all(["span", "div", "p"], class_=lambda x: x and "price" in x.lower())
                textos_precio = [p.get_text(strip=True) for p in precios if "$" in p.get_text()]

                precio_normal = "N/A"
                precio_oferta = "N/A"
                if len(textos_precio) >= 2:
                    precio_normal = textos_precio[0]
                    precio_oferta = textos_precio[1]
                elif len(textos_precio) == 1:
                    precio_oferta = textos_precio[0]

                # Imprimir los 3 primeros en la consola para validar
                if muestras < 3:
                    print(f"\n[HALLAZGO NAV {muestras + 1}]")
                    print(f" -> Nombre: {nombre}")
                    print(f" -> Precio Oferta: {precio_oferta}")
                    print(f" -> Enlace: {enlace[:60]}...")
                    muestras += 1

                if nombre and enlace:
                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": precio_normal,
                        "Precio Oferta": precio_oferta,
                        "Descuento": "Oferta",
                        "Enlace Directo": enlace,
                        "Imagen": "https://via.placeholder.com/200?text=Alkosto",
                        "Almacen": "Alkosto",
                        "Categoria": "Celulares"
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"--- [DIAGNÓSTICO ALKOSTO NAV] Error: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO ALKOSTO NAV] Total validados: {len(ofertas)} ---\n")
    return ofertas
