import requests

def extraer_alkosto(page=None):
    """
    Diagnóstico por API REST interna de Alkosto.
    Consume la búsqueda directa de productos para evitar el bloqueo del navegador.
    """
    ofertas = []
    url_api = "https://www.alkosto.com/rest/v2/alkosto/products/search?fields=FULL&query=%3Arelevance%3Acategory%3ABI_FE_101&pageSize=10&currentPage=0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-CO,es;q=0.9"
    }

    try:
        print(f"\n--- [DIAGNÓSTICO API ALKOSTO] Consultando Endpoint público ---")
        respuesta = requests.get(url_api, headers=headers, timeout=15)
        print(f"--- [DIAGNÓSTICO API ALKOSTO] Código de estado HTTP: {respuesta.status_code} ---")
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            productos = datos.get("products", [])
            print(f"--- [DIAGNÓSTICO API ALKOSTO] Productos devueltos por la API: {len(productos)} ---")
            
            for idx, prod in enumerate(productos[:3]):
                nombre = prod.get("name")
                precio_oferta = prod.get("price", {}).get("formattedValue", "N/A")
                precio_normal = prod.get("wasPrice", {}).get("formattedValue", precio_oferta) if prod.get("wasPrice") else precio_oferta
                url_rel = prod.get("url", "")
                enlace = f"https://www.alkosto.com{url_rel}" if url_rel.startswith("/") else url_rel
                
                print(f"\n[MUESTRA API {idx + 1}]")
                print(f" -> Nombre: {nombre}")
                print(f" -> Precio Oferta: {precio_oferta}")
                print(f" -> Precio Normal: {precio_normal}")
                print(f" -> Enlace: {enlace[:60]}...")
                
                if nombre:
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
        else:
            print(f"--- [DIAGNÓSTICO API ALKOSTO] La API respondió con error HTTP {respuesta.status_code} ---")

    except Exception as e:
        print(f"--- [DIAGNÓSTICO API ALKOSTO] Error de conexión: {str(e)} ---")

    print(f"\n--- [DIAGNÓSTICO API ALKOSTO] Ofertas procesadas: {len(ofertas)} ---\n")
    return ofertas
