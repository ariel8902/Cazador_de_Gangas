import time
import random
import re
from bs4 import BeautifulSoup

def extraer_ktronix(page):
    """
    Extrae ofertas reales de Ktronix capturando correctamente el porcentaje de descuento
    y aplicando técnicas anti-bloqueo con cabeceras reales y scroll gradual.
    """
    ofertas = []
    url_ktronix = "https://www.ktronix.com/ofertas"
    
    try:
        # Cabeceras reales para evitar bloqueos por cortafuegos en GitHub Actions
        page.set_extra_http_headers({
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        time.sleep(random.uniform(1.0, 2.5))
        page.goto(url_ktronix, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll dinámico para forzar la carga de productos e imágenes
        for i in range(5):
            posicion = (i + 1) * random.randint(700, 900)
            page.evaluate(f"window.scrollTo({{top: {posicion}, behavior: 'smooth'}});")
            time.sleep(random.uniform(1.0, 1.8))

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Búsqueda amplia de contenedores de productos en Ktronix
        productos = (
            soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
            soup.find_all("div", class_=lambda x: x and ("product-item" in x.lower() or "item" in x.lower()))
        )

        for prod in productos:
            try:
                # 1. Nombre del producto (descarte de anuncios publicitarios)
                nombre = None
                titulos_posibles = prod.find_all(["h2", "h3", "a", "span"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
                
                for t in titulos_posibles:
                    texto = t.get_text(strip=True)
                    if texto and len(texto) > 10 and not any(term in texto.lower() for term in ["paga a cuotas", "0% interés", "cuotas sin interés", "envío gratis"]):
                        nombre = texto
                        break

                if not nombre:
                    continue

                # 2. Enlace directo
                link_elem = prod.find("a", href=True)
                enlace = None
                if link_elem:
                    href = link_elem['href']
                    enlace = f"https://www.ktronix.com{href}" if href.startswith("/") else href

                # 3. Imagen real del producto (limpieza de srcset y descarte de banners)
                imagen_url = None
                imgs = prod.find_all("img")
                for img in imgs:
                    src = img.get("src") or img.get("data-src") or img.get("srcset")
                    if src and not any(bad in src.lower() for bad in ["banner", "cuotas", "logo", "flag", "svg"]):
                        imagen_url = src.split(",")[0].split()[0]  # Obtiene la primera URL válida en srcset
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

                # 5. Captura Real del Descuento (% numerico)
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
                        "Imagen": imagen_url or "https://via.placeholder.com/200?text=Ktronix+Oferta",
                        "Almacen": "Ktronix",
                        "Categoria": "Tecnología"
                    })

            except Exception:
                continue

    except Exception as e:
        print(f"Error en extracción de Ktronix: {str(e)}")

    return ofertas
