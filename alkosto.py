import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Prueba de diagnóstico aislada para Alkosto.
    Espera el renderizado dinámico del DOM para capturar únicamente productos reales.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [DIAGNÓSTICO ALKOSTO] Conectando a: {url_prueba} ---")
        page.goto(url_prueba, wait_until="networkidle", timeout=60000)
        
        # 1. Espera activa a que aparezca al menos un contenedor de producto
        try:
            page.wait_for_selector("li.product__item, form.product-item, div.product-item", timeout=15000)
            print("--- [DIAGNÓSTICO ALKOSTO] ¡Grilla de productos detectada en el DOM! ---")
        except Exception:
            print("--- [DIAGNÓSTICO ALKOSTO] Tiempo de espera agotado buscando grilla... ---")

        # 2. Scroll gradual para forzar renderizado de precios e imágenes
        for i in range(3):
            page.evaluate(f"window.scrollTo(0, {(i + 1) * 600});")
            time.sleep(1.5)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # 3. Captura amplia de tarjetas
        items = (
            soup.find_all("li", class_=lambda x: x and "product" in x.lower()) or
            soup.find_all("form", class_=lambda x: x and "product" in x.lower()) or
            soup.find_all("div", class_=lambda x: x and "product-item" in x.lower())
        )
        
        print(f"--- [DIAGNÓSTICO ALKOSTO] Tarjetas capturadas: {len(items)} ---")
        
        muestras = 0
        palabras_basura = ["mi cuenta", "mi perfil", "direcciones", "mis pedidos", "paga a cuotas", "0% interés", "favoritos", "servicio al cliente"]

        for item in items:
            nombre_elem = item.find(["h2", "h3", "h4", "a"], class_=lambda x: x and ("name" in x.lower() or "title" in x.lower()))
            if not nombre_elem:
                nombre_elem = item.find("a", href=True)
            
            nombre = nombre_elem.get_text(strip=True) if nombre_elem else None

            # Descarte de menús de navegación
            if not nombre or len(nombre) < 8 or any(bad in nombre.lower() for bad in palabras_basura):
                continue

            link_elem = item.find("a", href=True)
            enlace = link_elem['href'] if link_elem else None
            if enlace and enlace.startswith("/"):
                enlace = "https://www.alkosto.com" + enlace

            precios = [p.get_text(strip=True) for p in item.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
            
            if muestras < 3:
                print(f"\n[MUESTRA {muestras + 1}]")
                print(f" -> Producto: {nombre}")
                print(f" -> Precios: {precios}")
                print(f" -> Enlace: {enlace[:60] if enlace else 'N/A'}...")
                muestras += 1

            if nombre and enlace and precios:
                ofertas.append({
                    "Nombre": nombre,
                    "Precio Normal": precios[0] if len(precios) > 1 else "N/A",
                    "Precio Oferta": precios[-1] if precios else "N/A",
                    "Descuento": "Oferta",
                    "Enlace Directo": enlace,
                    "Imagen": "https://via.placeholder.com/200?text=Alkosto",
                    "Almacen": "Alkosto",
                    "Categoria": "Celulares"
                })

    except Exception as e:
        print(f"--- [DIAGNÓSTICO ALKOSTO] Error: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO ALKOSTO] Ofertas reales validadas: {len(ofertas)} ---\n")
    return ofertas
