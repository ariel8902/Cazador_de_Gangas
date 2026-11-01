import time
import random
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extrae ofertas reales de Alkosto capturando la grilla de productos
    y omitiendo enlaces de navegación.
    """
    ofertas = []
    categorias_urls = [
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105"),
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Scroll para forzar la carga de la grilla
            for i in range(4):
                page.evaluate(f"window.scrollTo(0, {i * 800});")
                time.sleep(1)

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Selectores reales de tarjetas en la grilla de Alkosto
            productos = (
                soup.find_all("form", class_=lambda x: x and "product-item" in x.lower()) or
                soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
                soup.find_all("div", class_=lambda x: x and "product-item" in x.lower())
            )

            for prod in productos:
                try:
                    # Título
                    nombre_elem = prod.find(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                    nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                    # Filtro anti-basura de menú
                    if not nombre or len(nombre) < 6 or any(bad in nombre.lower() for bad in ["mi cuenta", "mi perfil", "direcciones", "paga a cuotas", "0% interés"]):
                        continue

                    # Enlace
                    link_elem = prod.find("a", href=True)
                    if not link_elem:
                        continue
                    href = link_elem['href']
                    enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                    # Precios (Extracción flexible)
                    precios = prod.find_all(["span", "div", "p"], class_=lambda x: x and "price" in x.lower())
                    textos_precio = [p.get_text(strip=True) for p in precios if "$" in p.get_text()]
                    
                    precio_normal = "Consultar tienda"
                    precio_oferta = "Ver Oferta"
                    if len(textos_precio) >= 2:
                        precio_normal = textos_precio[0]
                        precio_oferta = textos_precio[1]
                    elif len(textos_precio) == 1:
                        precio_oferta = textos_precio[0]

                    # Imagen
                    imagen_url = None
                    imgs = prod.find_all("img")
                    for img in imgs:
                        src = img.get("src") or img.get("data-src") or img.get("srcset")
                        if src and not any(bad in src.lower() for bad in ["banner", "logo", "svg", "icon", "header"]):
                            imagen_url = src.split(",")[0].split()[0]
                            break
                    
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                    # Descuento
                    descuento = "Oferta"
                    desc_match = prod.find(text=re.compile(r'-\d+%|\d+%\s*OFF|\d+%', re.IGNORECASE))
                    if desc_match:
                        match = re.search(r'(\d+%)', desc_match)
                        if match:
                            descuento = f"-{match.group(1)}"

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

            time.sleep(random.uniform(2.0, 3.0))

        except Exception as e:
            print(f"Error extrayendo {cat_nombre} en Alkosto: {str(e)}")

    return ofertas
