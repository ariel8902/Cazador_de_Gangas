import time
import re
from bs4 import BeautifulSoup

def extraer_alkosto(page):
    """
    Extractor definitivo para Alkosto.
    Aísla el cuerpo principal (<main>), omite el precio falso de cabecera ($30.000)
    y descarta estrictamente menús o categorías.
    """
    ofertas = []
    categorias_urls = [
        ("Celulares", "https://www.alkosto.com/celulares/c/BI_FE_101"),
        ("Tecnología", "https://www.alkosto.com/tecnologia/c/BI_FE_104"),
        ("Electrodomésticos", "https://www.alkosto.com/electrodomesticos/c/BI_FE_105")
    ]

    for cat_nombre, url in categorias_urls:
        try:
            print(f"\n--- [EXTRACTOR ALKOSTO] Extrayendo categoría: {cat_nombre} ---")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Scroll escalonado para forzar la carga de la grilla
            for i in range(4):
                page.evaluate(f"window.scrollTo(0, {(i + 1) * 700});")
                time.sleep(1.2)

            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # 1. Aislar únicamente el contenedor principal (Ignora Header y Footer)
            cuerpo = soup.find("main") or soup.find("div", id=lambda x: x and "content" in x.lower())
            if not cuerpo:
                cuerpo = soup

            # 2. Buscar bloques de productos en la grilla
            bloques = cuerpo.find_all(["li", "div", "form"], class_=lambda x: x and ("product" in x.lower() or "item" in x.lower()))

            palabras_basura = [
                "venta:", "electrodomésticos", "ver todo", "televisores", "instalaciones", 
                "servicio", "métodos de pago", "sigue tu pedido", "factura", "mi cuenta", 
                "mi perfil", "direcciones", "mis pedidos", "atención al cliente", 
                "carro de compras", "términos y condiciones", "envío gratis"
            ]

            enlaces_procesados = set()

            for b in bloques:
                try:
                    # Extracción de enlace
                    link_elem = b.find("a", href=True)
                    if not link_elem:
                        continue

                    href = link_elem['href']
                    if href in enlaces_procesados or "/c/" in href.lower() or "venta" in href.lower():
                        continue  # Si es categoría (/c/) o venta telefónica, se descarta

                    enlace = f"https://www.alkosto.com{href}" if href.startswith("/") else href

                    # Extracción de precios reales en $ (Descarte del $30.000 promocional del header)
                    textos_precio = [elem.get_text(strip=True) for elem in b.find_all(text=re.compile(r'\$\s*[\d\.\,]+'))]
                    textos_precio_limpios = [p for p in textos_precio if "30.000" not in p]
                    
                    if not textos_precio_limpios:
                        continue  # Si no tiene un precio de producto real, se ignora

                    precio_normal = textos_precio_limpios[0] if len(textos_precio_limpios) >= 2 else "N/A"
                    precio_oferta = textos_precio_limpios[1] if len(textos_precio_limpios) >= 2 else textos_precio_limpios[0]

                    # Extracción de título del producto
                    nombre = None
                    for tag in b.find_all(["h2", "h3", "h4", "a", "span"]):
                        txt = tag.get_text(strip=True)
                        if txt and len(txt) > 12 and not any(bad in txt.lower() for bad in palabras_basura):
                            nombre = txt
                            break

                    if not nombre:
                        continue

                    enlaces_procesados.add(href)

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": precio_normal,
                        "Precio Oferta": precio_oferta,
                        "Descuento": "Oferta",
                        "Enlace Directo": enlace,
                        "Imagen": "https://via.placeholder.com/200?text=Alkosto+Oferta",
                        "Almacen": "Alkosto",
                        "Categoria": cat_nombre
                    })

                except Exception:
                    continue

        except Exception as e:
            print(f"--- [EXTRACTOR ALKOSTO] Error en {cat_nombre}: {str(e)} ---")

    print(f"\n--- [EXTRACTOR ALKOSTO] TOTAL PRODUCTOS REALES FILTRADOS: {len(ofertas)} ---\n")
    return ofertas
