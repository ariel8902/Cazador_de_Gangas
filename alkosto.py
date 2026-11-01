import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Diagnóstico quirúrgico en Alkosto.
    Captura contenedores generales y valida obligatoriamente la presencia de precio en $.
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
        
        # Captura sobre el contenedor principal evitando cabecera y pie de página
        cuerpo = soup.find("main") or soup.find("body")
        productos = []
        if cuerpo:
            productos = (
                cuerpo.find_all("form", class_=lambda x: x and "product" in x.lower()) or
                cuerpo.find_all("div", class_=lambda x: x and "product" in x.lower()) or
                cuerpo.find_all("li")
            )

        print(f"--- [DIAGNÓSTICO ALKOSTO] Elementos analizados en cuerpo: {len(productos)} ---")

        muestras = 0
        palabras_basura = [
            "instalaciones", "servicio", "métodos de pago", "sigue tu pedido", 
            "factura", "mi cuenta", "mi perfil", "direcciones", "mis pedidos", 
            "atención al cliente", "carro de compras", "términos y condiciones"
        ]

        for prod in productos:
            try:
                # 1. Extracción de Precios reales en $ (REQUISITO INDISPENSABLE)
                textos_precio = [elem.get_text(strip=True) for elem in prod.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                if not textos_precio:
                    continue  # Si no tiene precio real con $, se descarta (elimina menús y textos informativos)

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
                    if txt and len(txt) > 10 and not any(bad in txt.lower() for bad in palabras_basura):
                        nombre = txt
                        break

                if not nombre:
                    continue

                if muestras < 3:
                    print(f"\n[PRODUCTO CAPTURADO {muestras + 1}]")
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

    print(f"\n--- [DIAGNÓSTICO ALKOSTO] Total Productos Reales: {len(ofertas)} ---\n")
    return ofertas
