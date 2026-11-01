import time
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Script de diagnóstico quirúrgico para Alkosto.
    Imprime en consola los elementos detectados antes de procesar la lista.
    """
    ofertas = []
    url_prueba = "https://www.alkosto.com/celulares/c/BI_FE_101"
    
    try:
        print(f"\n--- [DIAGNÓSTICO ALKOSTO] Conectando a: {url_prueba} ---")
        page.goto(url_prueba, wait_until="domcontentloaded", timeout=60000)
        
        # Scroll gradual para asegurar renderizado de grilla
        for i in range(3):
            page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
            time.sleep(1.5)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Búsqueda de contenedores nativos de productos en Alkosto
        items = soup.select("li.product__item, form.product-item, div.product__item")
        print(f"--- [DIAGNÓSTICO ALKOSTO] Contenedores de grilla encontrados: {len(items)} ---")
        
        muestras = 0
        for item in items:
            # 1. Extracción de Nombre
            nombre_elem = item.select_one(".product__name, .name, h2, h3, a.js-product-click-name")
            nombre = nombre_elem.get_text(strip=True) if nombre_elem else "SIN NOMBRE"

            # 2. Extracción de Enlace
            link_elem = item.find("a", href=True)
            enlace = link_elem['href'] if link_elem else "SIN ENLACE"
            if enlace.startswith("/"):
                enlace = "https://www.alkosto.com" + enlace

            # 3. Extracción de Precios
            precios = [p.get_text(strip=True) for p in item.find_all(text=lambda t: t and "$" in t)]
            
            # Imprimir los primeros 3 hallazgos en el log para auditoría
            if muestras < 3:
                print(f"\n[MUESTRA {muestras + 1}]")
                print(f" -> Nombre: {nombre}")
                print(f" -> Precios en HTML: {precios}")
                print(f" -> Enlace: {enlace[:60]}...")
                muestras += 1

            # Si el elemento tiene nombre válido de producto y precio con $
            if nombre != "SIN NOMBRE" and len(nombre) > 8 and precios:
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

    print(f"\n--- [DIAGNÓSTICO ALKOSTO] Ofertas válidas filtradas: {len(ofertas)} ---\n")
    return ofertas
