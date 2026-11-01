import time
from bs4 import BeautifulSoup

def extraer_exito(page, categoria, url_busqueda):
    ofertas = []
    
    try:
        page.goto(url_busqueda, wait_until="networkidle", timeout=60000)
        
        # Desplazamiento forzado para activar la carga de imágenes dinámicas
        for i in range(5):
            page.evaluate(f"window.scrollTo(0, {i * 800});")
            time.sleep(1)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        productos = soup.find_all("article") or soup.find_all("div", class_=lambda x: x and "product" in x.lower())

        for prod in productos:
            try:
                nombre_elem = prod.find(["h3", "h2", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                link_elem = prod.find("a", href=True)
                enlace = f"https://www.exito.com{link_elem['href']}" if link_elem and link_elem['href'].startswith("/") else (link_elem['href'] if link_elem else None)

                # Captura exhaustiva de etiquetas de imagen
                img_elem = prod.find("img")
                imagen_url = None
                if img_elem:
                    imagen_url = (
                        img_elem.get("src") or 
                        img_elem.get("data-src") or 
                        img_elem.get("data-srcset") or 
                        img_elem.get("srcset")
                    )
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

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
                        "Imagen": imagen_url or "https://vtex.vtexassets.com/assets/portal/src/img/empty.png",
                        "Almacen": "Éxito",
                        "Categoria": categoria
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"Error en extracción de Éxito: {str(e)}")

    return ofertas
