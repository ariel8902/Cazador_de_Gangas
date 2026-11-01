from bs4 import BeautifulSoup
import time

def extraer_exito(page, categoria, url_busqueda):
    """
    Extrae ofertas del almacén Éxito utilizando la instancia activa de Playwright.
    Incluye la captura de la imagen original del producto.
    """
    ofertas = []
    
    try:
        page.goto(url_busqueda, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)  # Tiempo para renderizado de imágenes dinámicas
        
        # Desplazamiento suave para cargar imágenes en perezoso (lazy loading)
        page.evaluate("window.scrollBy(0, 1500);")
        time.sleep(2)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Buscar contenedores de productos en el HTML de Éxito
        productos = soup.find_all("article") or soup.find_all("div", class_=lambda x: x and "product" in x.lower())

        for prod in productos:
            try:
                # 1. Nombre del Producto
                nombre_elem = prod.find(["h3", "h2", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                # 2. Enlace Directo
                link_elem = prod.find("a", href=True)
                enlace = f"https://www.exito.com{link_elem['href']}" if link_elem and link_elem['href'].startswith("/") else (link_elem['href'] if link_elem else None)

                # 3. Imagen del Producto (Captura URL de foto real)
                img_elem = prod.find("img")
                imagen_url = None
                if img_elem:
                    imagen_url = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("srcset")
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                # 4. Precios y Descuentos
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

                # Si se obtuvo al menos el nombre y el enlace, se añade la oferta
                if nombre and enlace:
                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": precio_normal,
                        "Precio Oferta": precio_oferta,
                        "Descuento": descuento,
                        "Enlace Directo": enlace,
                        "Imagen": imagen_url or "https://via.placeholder.com/200?text=Exito+Oferta",
                        "Almacen": "Éxito",
                        "Categoria": categoria
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"Error en extracción de Éxito: {str(e)}")

    return ofertas
