import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extrae ofertas reales de Alkosto capturando correctamente el porcentaje
    de descuento y evitando descartes por etiquetas financieras.
    """
    ofertas = []
    url_alkosto = "https://www.alkosto.com/ofertas"
    
    try:
        page.goto(url_alkosto, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll dinámico para forzar la carga completa de productos e imágenes
        for i in range(5):
            page.evaluate(f"window.scrollTo(0, {i * 900});")
            time.sleep(1)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Búsqueda amplia de tarjetas de producto en el maquetado de Alkosto
        productos = (
            soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
            soup.find_all("div", class_=lambda x: x and ("product-item" in x.lower() or "item" in x.lower()))
        )

        for prod in productos:
            try:
                # 1. Nombre del Producto (Filtra textos publicitarios de tarjetas)
                nombre = None
                titulos_posibles = prod.find_all(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                
                for t in titulos_posibles:
                    texto = t.get_text(strip=True)
                    if texto and len(texto) > 10 and not any(term in texto.lower() for term in ["paga a cuotas", "0% interés", "cuotas sin interés", "envío gratis"]):
                        nombre = texto
                        break

                if not nombre:
                    continue

                # 2. Enlace Directo
                link_elem = prod.find("a", href=True)
                enlace = None
                if link_elem:
                    href = link_elem['href']
                    enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                # 3. Imagen Real del Producto (evita banners de marcas/tarjetas)
                imagen_url = None
                imgs = prod.find_all("img")
                for img in imgs:
                    src = img.get("src") or img.get("data-src") or img.get("srcset")
                    if src and not any(bad in src.lower() for bad in ["banner", "cuotas", "logo", "flag", "svg"]):
                        imagen_url = src.split()[0] # En caso de srcset toma la primera URL
                        break
                
                if imagen_url and imagen_url.startswith("//"):
                    imagen_url = "https:" + imagen_url

                # 4. Precios (Normal y Oferta)
                precios = prod.find_all(["span", "p", "div"], class_=lambda x: x and "price" in x.lower())
                precio_normal = "N/A"
                precio_oferta = "N/A"
                
                textos_precio = [p.get_text(strip=True) for p in precios if "$" in p.get_text()]
                if len(textos_precio) >= 2:
                    precio_normal = textos_precio[0]
                    precio_oferta = textos_precio[1]
                elif len(textos_precio) == 1:
                    precio_oferta = textos_precio[0]

                # 5. Descuento Real (Búsqueda de patrón de porcentaje ej: "-50%" o "50% OFF")
                descuento = "Oferta"
                # Busca elementos visuales de rebaja o analiza el texto en todo el producto
                desc_elem = prod.find(text=re.compile(r'-\d+%|\d+%\s*OFF|\d+%', re.IGNORECASE))
                if desc_elem:
                    match = re.search(r'(\d+%)', desc_elem)
                    if match:
                        descuento = f"-{match.group(1)}"
                else:
                    # Intento secundario por clase contenedora
                    tag_desc = prod.find(["span", "div"], class_=lambda x: x and ("discount" in x.lower() or "badge" in x.lower() or "flag" in x.lower()))
                    if tag_desc:
                        descuento = tag_desc.get_text(strip=True)

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
        print(f"Error en extracción de Alkosto: {str(e)}")

    return ofertas
