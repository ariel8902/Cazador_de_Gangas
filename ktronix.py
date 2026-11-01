import time
import random
import re
from bs4 import BeautifulSoup

def extraer_ktronix(page):
    """
    Extrae ofertas reales de Ktronix descartando estrictamente elementos del menú,
    pie de página e información sin precio ni imagen.
    """
    ofertas = []
    categorias_urls = [
        ("Tecnología", "https://www.ktronix.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.ktronix.com/electrodomesticos/c/BI_FE_105"),
        ("Celulares", "https://www.ktronix.com/celulares/c/BI_FE_101")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            for i in range(4):
                page.evaluate(f"window.scrollTo(0, {i * 800});")
                time.sleep(1)

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Selectores de tarjetas de producto
            productos = (
                soup.find_all("form", class_=lambda x: x and "product-item" in x.lower()) or
                soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
                soup.find_all("div", class_=lambda x: x and "product-item" in x.lower())
            )

            for prod in productos:
                try:
                    # 1. Nombre y descarte de elementos de menú de usuario
                    nombre_elem = prod.find(["h2", "h3", "a"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                    nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                    palabras_basura = ["mi cuenta", "mi perfil", "direcciones", "mis pedidos", "paga a cuotas", "0% interés", "favoritos", "servicio al cliente"]
                    if not nombre or len(nombre) < 6 or any(bad in nombre.lower() for bad in palabras_basura):
                        continue

                    # 2. Enlace directo
                    link_elem = prod.find("a", href=True)
                    if not link_elem:
                        continue
                    href = link_elem['href']
                    enlace = f"https://www.ktronix.com{href}" if href.startswith("/") else href

                    # 3. Precios reales con signo $
                    textos_precio = [elem.get_text(strip=True) for elem in prod.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                    if not textos_precio:
                        continue  # Si no tiene precio con $, no es un producto real

                    precio_normal = "N/A"
                    precio_oferta = "N/A"
                    if len(textos_precio) >= 2:
                        precio_normal = textos_precio[0]
                        precio_oferta = textos_precio[1]
                    elif len(textos_precio) == 1:
                        precio_oferta = textos_precio[0]

                    # 4. Imagen real del producto
                    imagen_url = None
                    imgs = prod.find_all("img")
                    for img in imgs:
                        src = img.get("src") or img.get("data-src") or img.get("srcset")
                        if src and not any(bad in src.lower() for bad in ["banner", "logo", "svg", "icon", "header"]):
                            imagen_url = src.split(",")[0].split()[0]
                            break
                    
                    if not imagen_url:
                        continue

                    if imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                    # 5. Descuento
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
                        "Imagen": imagen_url,
                        "Almacen": "Ktronix",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

            time.sleep(random.uniform(2.0, 3.0))

        except Exception as e:
            print(f"Error extrayendo {cat_nombre} en Ktronix: {str(e)}")

    return ofertas
