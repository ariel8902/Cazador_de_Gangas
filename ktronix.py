import time
from bs4 import BeautifulSoup

def extraer_ktronix(page):
    """
    Extrae ofertas del almacén Ktronix incluyendo la captura de la imagen original.
    """
    ofertas = []
    url_ktronix = "https://www.ktronix.com/ofertas"
    
    try:
        page.goto(url_ktronix, wait_until="networkidle", timeout=60000)
        
        # Desplazamiento forzado para activar la carga perezosa de imágenes (lazy loading)
        for i in range(5):
            page.evaluate(f"window.scrollTo(0, {i * 800});")
            time.sleep(1)

0        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Buscar contenedores de productos en Ktronix
        productos = soup.find_all("li", class_=lambda x: x and "product" in x.lower()) or soup.find_all("div", class_=lambda x: x and "item" in x.lower())

        for prod in productos:
            try:
                # 1. Nombre
                nombre_elem = prod.find(["h2", "h3", "a"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                # 2. Enlace
                link_elem = prod.find("a", href=True)
                enlace = f"https://www.ktronix.com{link_elem['href']}" if link_elem and link_elem['href'].startswith("/") else (link_elem['href'] if link_elem else None)

                # 3. Imagen Real
                img_elem = prod.find("img")
                imagen_url = None
                if img_elem:
                    imagen_url = (
                        img_elem.get("src") or 
                        img_elem.get("data-src") or 
                        img_elem.get("srcset")
                    )
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                # 4. Precios
                precios = prod.find_all(["span", "div"], class_=lambda x: x and "price" in x.lower())
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
                        "Imagen": imagen_url or "https://via.placeholder.com/200?text=Ktronix+Oferta",
                        "Almacen": "Ktronix",
                        "Categoria": "Ofertas Generales"
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"Error en extracción de Ktronix: {str(e)}")

    return ofertas
