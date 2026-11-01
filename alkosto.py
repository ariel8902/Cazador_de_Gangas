import time
import random
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extrae ofertas de Alkosto navegando por categorías directas (igual que Éxito),
    filtrando banners publicitarios y capturando productos reales con su descuento.
    """
    ofertas = []
    
    # Categorías directas en Alkosto
    categorias_urls = [
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105"),
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101")
    ]
    
    try:
        page.set_extra_http_headers({
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    except Exception:
        pass

    for cat_nombre, url in categorias_urls:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Scroll gradual para cargar grilla de productos e imágenes
            for i in range(3):
                posicion = (i + 1) * 800
                page.evaluate(f"window.scrollTo({{top: {posicion}, behavior: 'smooth'}});")
                time.sleep(1)

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Grilla real de productos en Alkosto
            productos = soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or soup.find_all("div", class_=lambda x: x and "product-item" in x.lower())

            for prod in productos:
                try:
                    # 1. Nombre del producto
                    nombre_elem = prod.find(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                    nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                    if not nombre or len(nombre) < 8 or any(term in nombre.lower() for term in ["paga a cuotas", "0% interés", "cuotas sin interés", "envío gratis"]):
                        continue

                    # 2. Enlace directo
                    link_elem = prod.find("a", href=True)
                    enlace = None
                    if link_elem:
                        href = link_elem['href']
                        enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                    # 3. Imagen real (descarte de banners e iconos)
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

                    # 5. Descuento (% numérico o etiqueta)
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
            
            time.sleep(random.uniform(1.5, 2.5))

        except Exception as e:
            print(f"Error extrayendo {cat_nombre} en Alkosto: {str(e)}")

    return ofertas
