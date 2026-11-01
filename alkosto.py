import time
import random
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extrae ofertas de Alkosto con protección anti-bloqueo (User-Agent real,
    encabezados de navegador y pausas aleatorias humanas).
    """
    ofertas = []
    
    categorias_urls = [
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105"),
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101")
    ]

    # 1. Inyección de encabezados de navegador real (Anti-Bloqueo)
    try:
        page.set_extra_http_headers({
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    except Exception:
        pass

    for cat_nombre, url in categorias_urls:
        try:
            # Pausa aleatoria antes de entrar a cada categoría
            time.sleep(random.uniform(2.0, 4.0))
            
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Scroll humano desigual
            for i in range(4):
                posicion = (i + 1) * random.randint(650, 850)
                page.evaluate(f"window.scrollTo({{top: {posicion}, behavior: 'smooth'}});")
                time.sleep(random.uniform(1.2, 2.2))

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            productos = (
                soup.find_all("form", class_=lambda x: x and "product-item" in x.lower()) or
                soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
                soup.find_all("div", class_=lambda x: x and "product-item" in x.lower())
            )

            for prod in productos:
                try:
                    nombre_elem = prod.find(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                    if not nombre_elem:
                        nombre_elem = prod.find("a", class_=lambda x: x and "product" in x.lower())
                    
                    nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

                    if not nombre or len(nombre) < 6 or any(term in nombre.lower() for term in ["paga a cuotas", "0% interés", "cuotas sin interés"]):
                        continue

                    link_elem = prod.find("a", href=True)
                    enlace = None
                    if link_elem:
                        href = link_elem['href']
                        enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                    imagen_url = None
                    imgs = prod.find_all("img")
                    for img in imgs:
                        src = img.get("src") or img.get("data-src") or img.get("srcset")
                        if src and not any(bad in src.lower() for bad in ["banner", "cuotas", "logo", "flag", "svg", "icon"]):
                            imagen_url = src.split(",")[0].split()[0]
                            break
                    
                    if imagen_url and imagen_url.startswith("//"):
                        imagen_url = "https:" + imagen_url

                    precios = prod.find_all(["span", "p", "div"], class_=lambda x: x and "price" in x.lower())
                    precio_normal = "N/A"
                    precio_oferta = "N/A"
                    
                    textos_precio = [p.get_text(strip=True) for p in precios if "$" in p.get_text()]
                    if len(textos_precio) >= 2:
                        precio_normal = textos_precio[0]
                        precio_oferta = textos_precio[1]
                    elif len(textos_precio) == 1:
                        precio_oferta = textos_precio[0]

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

        except Exception as e:
            print(f"Error en {cat_nombre} (Alkosto): {str(e)}")

    return ofertas
