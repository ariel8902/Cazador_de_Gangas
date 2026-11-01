import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extracción limpia en Alkosto.
    Exige la partícula '/p/' en la URL para garantizar que solo sea un producto real.
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
        
        productos = (
            soup.find_all("form", class_=lambda x: x and "product" in x.lower()) or
            soup.find_all("li", class_=lambda x: x and ("product" in x.lower() or "item" in x.lower())) or
            soup.find_all("div", class_=lambda x: x and "product" in x.lower())
        )

        muestras = 0
        palabras_basura = [
            "métodos de pago", "sigue tu pedido", "factura", "mi cuenta", "mi perfil", 
            "direcciones", "mis pedidos", "paga a cuotas", "0% interés", "favoritos", 
            "servicio al cliente", "carro de compras", "atención al cliente"
        ]

        for prod in productos:
            try:
                # 1. Extracción de enlace (Filtro indispensable: debe contener '/p/')
                link_elem = prod.find("a", href=True)
                if not link_elem:
                    continue
                
                href = link_elem['href']
                if "/p/" not in href.lower():
                    continue  # Si no es página de producto, se descarta

                enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                # 2. Extracción de título
                nombre = None
                for tag in prod.find_all(["h2", "h3", "h4", "a", "span"]):
                    txt = tag.get_text(strip=True)
                    if txt and len(txt) > 8 and not any(bad in txt.lower() for bad in palabras_basura):
                        nombre = txt
                        break

                if not nombre:
                    continue

                # 3. Precios
                textos_precio = [elem.get_text(strip=True) for elem in prod.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                precio_normal = textos_precio[0] if len(textos_precio) >= 2 else "N/A"
                precio_oferta = textos_precio[1] if len(textos_precio) >= 2 else (textos_precio[0] if len(textos_precio) == 1 else "N/A")

                # Muestras en log para confirmar que solo salgan celulares
                if muestras < 3:
                    print(f"\n[PRODUCTO REAL CAPTURADO {muestras + 1}]")
                    print(f" -> Nombre: {nombre}")
                    print(f" -> Precio Oferta: {precio_oferta}")
                    print(f" -> Enlace de Producto: {enlace[:60]}...")
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

    print(f"\n--- [DIAGNÓSTICO ALKOSTO] Total Productos Reales: {len(ofertas)} ---\n")
    return ofertas
