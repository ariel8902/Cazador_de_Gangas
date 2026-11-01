import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extractor definitivo para Alkosto basado en detección directa de Precios ($).
    Evita depender de clases CSS dinámicas o selectores de grilla fallidos.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [EXTRACTOR ALKOSTO] Conectando a: {url_prueba} ---")
        page.goto(url_prueba, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll para garantizar la carga de precios
        for i in range(4):
            page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
            time.sleep(1)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # 1. Buscar todos los enlaces que tengan un precio en $ dentro o en su contenedor
        candidatos = soup.find_all(["li", "article", "div", "form"])
        
        muestras = 0
        palabras_basura = [
            "instalaciones", "servicio", "métodos de pago", "sigue tu pedido", 
            "factura", "mi cuenta", "mi perfil", "direcciones", "mis pedidos", 
            "atención al cliente", "carro de compras", "términos y condiciones",
            "envío gratis", "ver más", "comprar"
        ]

        enlaces_procesados = set()

        for block in candidatos:
            try:
                # Buscar precios con signo $ dentro del bloque
                textos_precio = [elem.get_text(strip=True) for elem in block.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                if not textos_precio:
                    continue

                # Buscar el enlace del producto
                link_elem = block.find("a", href=True)
                if not link_elem:
                    continue

                href = link_elem['href']
                if href in enlaces_procesados:
                    continue
                
                enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                # Buscar el nombre del producto
                nombre = None
                for tag in block.find_all(["h2", "h3", "h4", "a", "span"]):
                    txt = tag.get_text(strip=True)
                    if txt and len(txt) > 12 and not any(bad in txt.lower() for bad in palabras_basura):
                        nombre = txt
                        break

                if not nombre:
                    continue

                # Evitar duplicados
                enlaces_procesados.add(href)

                precio_normal = textos_precio[0] if len(textos_precio) >= 2 else "N/A"
                precio_oferta = textos_precio[1] if len(textos_precio) >= 2 else textos_precio[0]

                if muestras < 3:
                    print(f"\n[PRODUCTO REAL EXTRAÍDO {muestras + 1}]")
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
        print(f"--- [EXTRACTOR ALKOSTO] Error: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] Total Productos Limpios: {len(ofertas)} ---\n")
    return ofertas
