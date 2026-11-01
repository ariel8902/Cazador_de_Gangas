import time
import random
import re
from bs4 import BeautifulSoup

def extraer_ktronix(page):
    """
    Extrae ofertas reales de Ktronix capturando la grilla validada de productos.
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
            
            productos = (
                soup.find_all("form", class_=lambda x: x and "product" in x.lower()) or
                soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
                soup.find_all("div", class_=lambda x: x and "product" in x.lower())
            )

            for prod in productos:
                try:
                    nombre = None
                    for tag in prod.find_all(["h2", "h3", "a", "span"]):
                        txt = tag.get_text(strip=True)
                        if txt and len(txt) > 8 and not any(bad in txt.lower() for bad in ["cuotas", "interés", "envío gratis"]):
                            nombre = txt
                            break

                    if not nombre:
                        continue

                    link_elem = prod.find("a", href=True)
                    if not link_elem:
                        continue
                    href = link_elem['href']
                    enlace = f"https://www.ktronix.com{href}" if href.startswith("/") else href

                    imagen_url = None
                    imgs = prod.find_all("img")
                    for img in imgs:
                        src = img.get("src") or img.get("data-src") or img.get("srcset")
                        if src and not any(bad in src.lower() for bad in ["banner", "logo", "svg", "icon"]):
                            imagen_url = src.split(",")[0].split()[0]
                            break
                    
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                    textos = [elem.get_text(strip=True) for elem in prod.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                    precio_normal = textos[0] if len(textos) >= 2 else "N/A"
                    precio_oferta = textos[1] if len(textos) >= 2 else (textos[0] if len(textos) == 1 else "N/A")

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
                        "Imagen": imagen_url or "https://via.placeholder.com/200?text=Ktronix+Oferta",
                        "Almacen": "Ktronix",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

            time.sleep(random.uniform(2.0, 4.0))

        except Exception as e:
            print(f"Error extrayendo {cat_nombre} en Ktronix: {str(e)}")

    return ofertas
