import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extracción directa en Alkosto enfocada en las tarjetas reales de producto.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [DIAGNÓSTICO DEFINITIVO ALKOSTO] Conectando a: {url_prueba} ---")
        page.goto(url_prueba, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll gradual para cargar imágenes y precios
        for i in range(4):
            page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
            time.sleep(1.5)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Selectores nativos de tarjetas de producto en Alkosto
        tarjetas = (
            soup.find_all("li", class_=lambda x: x and "product" in x.lower()) or
            soup.find_all("div", class_=lambda x: x and "item" in x.lower() and "product" in x.lower()) or
            soup.find_all("form", class_=lambda x: x and "product" in x.lower())
        )

        print(f"--- [DIAGNÓSTICO DEFINITIVO] Tarjetas detectadas: {len(tarjetas)} ---")

        muestras = 0
        palabras_basura = ["métodos de pago", "sigue tu pedido", "factura", "mi cuenta", "mi perfil", "servicio al cliente"]

        for t in tarjetas:
            try:
                # 1. Título
                tit_elem = t.find(["h2", "h3", "h4", "a"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower() or "heading" in x.lower()))
                if not tit_elem:
                    tit_elem = t.find("a", href=True)
                
                nombre = tit_elem.get_text(strip=True) if tit_elem else None
                if not nombre or len(nombre) < 8 or any(b in nombre.lower() for b in palabras_basura):
                    continue

                # 2. Precios
                precios = [p.get_text(strip=True) for p in t.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                if not precios:
                    continue  # Si la tarjeta no tiene precio con $, no es un producto real

                precio_normal = precios[0] if len(precios) >= 2 else "N/A"
                precio_oferta = precios[1] if len(precios) >= 2 else precios[0]

                # 3. Enlace
                link_elem = t.find("a", href=True)
                if not link_elem:
                    continue
                href = link_elem['href']
                enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                # Imprimir muestra limpia
                if muestras < 3:
                    print(f"\n[PRODUCTO EXTRAÍDO {muestras + 1}]")
                    print(f" -> Título: {nombre}")
                    print(f" -> Oferta: {precio_oferta}")
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
        print(f"--- [DIAGNÓSTICO DEFINITIVO] Error: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO DEFINITIVO] Total extraídos limpios: {len(ofertas)} ---\n")
    return ofertas
