import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extracción limpia y estricta en Alkosto.
    Exige precio real en pesos ($) y enlace de producto válido descartando servicios o menús.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [DIAGNÓSTICO ALKOSTO] Conectando a: {url_prueba} ---")
        page.goto(url_prueba, wait_until="domcontentloaded", timeout=60000)
        
        for i in range(4):
            page.evaluate(f"window.scrollTo(0, {i * 700});")
            time.sleep(1)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Búsqueda directa sobre artículos de la grilla principal
        productos = soup.select("li.product__item, div.product__item, form.product-item")

        print(f"--- [DIAGNÓSTICO ALKOSTO] Tarjetas de grilla encontradas: {len(productos)} ---")

        muestras = 0
        palabras_basura = [
            "instalaciones", "servicio", "métodos de pago", "sigue tu pedido", 
            "factura", "mi cuenta", "mi perfil", "direcciones", "mis pedidos"
        ]

        for prod in productos:
            try:
                # 1. Extracción de Precios reales en $ (Obligatorio)
                textos_precio = [elem.get_text(strip=True) for elem in prod.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                if not textos_precio:
                    continue  # Si no tiene precio real con $, se omite

                precio_normal = textos_precio[0] if len(textos_precio) >= 2 else "N/A"
                precio_oferta = textos_precio[1] if len(textos_precio) >= 2 else textos_precio[0]

                # 2. Extracción de enlace
                link_elem = prod.find("a", href=True)
                if not link_elem:
                    continue
                
                href = link_elem['href']
                enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                # 3. Extracción de título
                nombre = None
                for tag in prod.find_all(["h2", "h3", "h4", "a", "span"]):
                    txt = tag.get_text(strip=True)
                    if txt and len(txt) > 8 and not any(bad in txt.lower() for bad in palabras_basura):
                        nombre = txt
                        break

                if not nombre:
                    continue

                if muestras < 3:
                    print(f"\n[PRODUCTO FÍSICO REAL {muestras + 1}]")
                    print(f" -> Nombre: {nombre}")
                    print(f" -> Precio Oferta: {precio_oferta}")
                    print(f" -> Enlace: {enlace[:60]}...")
                    muestras += 1

                ofertas.append({
                    "Nombre": nombre,
                    "Precio Normal": precio_normal,
                    "Precio Oferta": precio_oferta,
                    "Descuento": "Oferta",
                    "Enlace Directo": enlace,
                    "Imagen": "https://via.placeholder.com/200?text=Alkosto",
                    "Almacen": "Alkosto",
                    "Categoria": "Celulares"
                })

            except Exception:
                continue

    except Exception as e:
        print(f"--- [DIAGNÓSTICO ALKOSTO] Error: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO ALKOSTO] Total Productos Físicos Válidos: {len(ofertas)} ---\n")
    return ofertas
