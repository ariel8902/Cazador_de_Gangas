import time
import random
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extractor de prueba para Alkosto usando exactamente la misma estructura de Éxito.
    """
    ofertas = []
    url_alkosto = "https://www.alkosto.com/tecnologia/c/BI_FE_104"
    
    try:
        print(f"--- Probando conexión a Alkosto: {url_alkosto} ---")
        page.goto(url_alkosto, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll calcado de Éxito
        for i in range(4):
            page.evaluate(f"window.scrollTo(0, {i * 800});")
            time.sleep(1)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Imprimir longitud del HTML para verificar si carga o si viene vacío por bloqueo
        print(f"Tamaño del HTML recibido en Alkosto: {len(content)} caracteres")
        
        # Búsqueda amplia de contenedores
        productos = (
            soup.find_all("form", class_=lambda x: x and "product" in x.lower()) or
            soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
            soup.find_all("div", class_=lambda x: x and "product" in x.lower())
        )
        
        print(f"Elementos candidatos encontrados en Alkosto: {len(productos)}")

        for prod in productos:
            try:
                nombre_elem = prod.find(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                if not nombre or len(nombre) < 5 or "paga a cuotas" in nombre.lower():
                    continue

                link_elem = prod.find("a", href=True)
                enlace = f"https://www.alkosto.com{link_elem['href']}" if link_elem and link_elem['href'].startswith("/") else (link_elem['href'] if link_elem else None)

                img_elem = prod.find("img")
                imagen_url = None
                if img_elem:
                    imagen_url = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("srcset")
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                precios = prod.find_all(["span", "div", "p"], class_=lambda x: x and "price" in x.lower())
                precio_normal = "N/A"
                precio_oferta = "N/A"
                
                if len(precios) >= 2:
                    precio_normal = precios[0].get_text(strip=True)
                    precio_oferta = precios[1].get_text(strip=True)
                elif len(precios) == 1:
                    precio_oferta = precios[0].get_text(strip=True)

                descuento = "Oferta"
                desc_elem = prod.find(["span", "div"], class_=lambda x: x and "discount" in x.lower())
                if desc_elem:
                    descuento = desc_elem.get_text(strip=True)

                if nombre and enlace:
                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": precio_normal,
                        "Precio Oferta": precio_oferta,
                        "Descuento": descuento,
                        "Enlace Directo": enlace,
                        "Imagen": imagen_url or "https://via.placeholder.com/200?text=Alkosto+Oferta",
                        "Almacen": "Alkosto",
                        "Categoria": "Tecnología"
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"Error crítico en prueba Alkosto: {str(e)}")

    return ofertas
