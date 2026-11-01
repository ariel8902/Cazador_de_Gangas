import time
import random
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extrae ofertas de Alkosto buscando contenedores reales de productos
    y manejando la estructura nativa del comercio.
    """
    ofertas = []
    
    categorias_urls = [
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105"),
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            # Ir a la página y esperar la carga de la grilla
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Scroll dinámico profundo para activar productos
            for i in range(4):
                page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
                time.sleep(1.5)

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Selectores reales de productos en Alkosto
            productos = (
                soup.find_all("form", class_=lambda x: x and "product-item" in x.lower()) or
                soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
                soup.find_all("div", class_=lambda x: x and "product-item" in x.lower())
            )

            for prod in productos:
                try:
                    # 1. Nombre
                    nombre_elem = prod.find(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                    if not nombre_elem:
                        nombre_elem = prod.find("a", class_=lambda x: x and "product" in x.lower())
                    
                    nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                    if not nombre or len(nombre) < 6 or any(term in nombre.lower() for term in ["paga a cuotas", "0% interés", "cuotas sin interés"]):
                        continue

                    # 2. Enlace
                    link_elem = prod.find("a", href=True)
                    enlace = None
                    if link_elem:
                        href = link_elem['href']
                        enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                    # 3. Imagen
                    imagen_url = None
                    imgs = prod.find_all("img")
                    for img in imgs:
                        src = img.get("src") or img.get("data-src") or img.get("srcset")
                        if src and not any(bad in src.lower() for bad in ["banner", "cuotas", "logo", "flag", "svg", "icon"]):
                            imagen_url = src.split(",")[0].split()[0]
                            break
                    
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                    # 4. Precios
                    precios = prod.find_all(["span", "p", "div"], class_=lambda x: x and "price" in x.lower())
                    precio_normal = "N/A"
                    precio_oferta = "N/A"
                    
                    textos_precio = [p.get_text(strip=True) for p in precios if "$" in p.get_text()]
                    if len(textos_precio) >= 2:
                        precio_normal = textos_precio[0]
                        precio_oferta = textos_precio[1]
                    elif len(textos_precio) == 1:
                        precio_oferta = textos_precio[0]

                    # 5. Descuento
                    descuento = "Oferta"
                    desc_match = prod.find(text=re.compile(r'-\d+%|\d+%\s*OFF|\d+%', re.IGNORECASE))
                    if desc_match:
                        match = re.search(r'(\d+%)', desc_match)
                        if match:
                            descuento = f"-{match.group(1)}"
                    else:
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
                            "Categoria": cat_nombre
                        })

                except Exception:
                    continue
            
            time.sleep(2)

        except Exception as e:
            print(f"Error en {cat_nombre} (Alkosto): {str(e)}")

    return ofertas
