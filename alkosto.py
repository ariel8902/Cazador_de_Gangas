import requests
import re

def extraer_alkosto(page=None):
    ofertas = []
    
    # Endpoint oficial del buscador de la API de VTEX de Alkosto
    url_api = "https://www.alkosto.com/api/catalog_system/pub/products/search?_from=0&_to=49"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        print(f"\n--- [API VTEX ALKOSTO] Consultando base de datos de productos ---")
        response = requests.get(url_api, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"    ❌ Error en la API: Código HTTP {response.status_code}")
            return ofertas

        productos = response.json()
        print(f"    📊 Productos recibidos desde la API: {len(productos)}")

        for prod in productos:
            try:
                nombre = prod.get('productName', 'Producto Desconocido')
                link = prod.get('link', '')
                
                # Obtener la primera variante (items[0]) que contiene los precios reales
                items = prod.get('items', [])
                if not items:
                    continue
                
                sellers = items[0].get('sellers', [])
                if not sellers:
                    continue
                
                # Extraer oferta comercial del primer vendedor
                commestibles = sellers[0].get('commertialOffer', {})
                precio_lista = commestibles.get('ListPrice', 0)
                precio_oferta = commestibles.get('Price', 0)
                
                if precio_lista <= 0 or precio_oferta <= 0 or precio_lista <= precio_oferta:
                    continue

                # Calcular el porcentaje real de descuento
                descuento_pct = int(round((1 - (precio_oferta / precio_lista)) * 100))

                # FILTRO INGLESIBLE: Exigir estrictamente -50% o más
                if descuento_pct < 50:
                    continue

                descuento_txt = f"-{descuento_pct}%"
                
                # Extraer imagen principal
                images = items[0].get('images', [])
                img_url = images[0].get('imageUrl', 'https://via.placeholder.com/200?text=Alkosto') if images else ''

                str_precio_normal = f"${precio_lista:,.0f}".replace(",", ".")
                str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")

                print(f"    🔥 [GANGÓN API CAPTURADO {descuento_txt}] {nombre[:35]} | Oferta: {str_precio_oferta}")

                ofertas.append({
                    "Nombre": nombre,
                    "Precio Normal": str_precio_normal,
                    "Precio Oferta": str_precio_oferta,
                    "Descuento": descuento_txt,
                    "Enlace Directo": link,
                    "Imagen": img_url,
                    "Almacen": "Alkosto",
                    "Categoria": "API VTEX Masiva"
                })

            except Exception:
                continue

    except Exception as e:
        print(f"--- [API VTEX ALKOSTO] Error general de conexión: {str(e)} ---")

    print(f"\n--- [API VTEX ALKOSTO] TOTAL GANGAS REALES >=50%: {len(ofertas)} ---\n")
    return ofertas
