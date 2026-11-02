from playwright.sync_api import sync_playwright
import re

def extraer_alkosto(page_param=None):
    ofertas = []
    
    with sync_playwright() as p:
        # Lanzar navegador con argumentos tácticos anti-detección
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        
        # Crear contexto con apariencia 100% real de Windows y Chrome
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            extra_http_headers={
                "Accept-Language": "es-ES,es;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="8", "Google Chrome";v="122"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"'
            }
        )
        
        page = context.new_page()
        
        # Ocultar la propiedad de automatización para evitar bloqueos
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            url = "https://www.alkosto.com/ofertas/c/ofertas-alkosto"
            print(f"\n--- [NAVEGADOR REAL ALKOSTO] Desplegando en: {url} ---")
            
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(6000)
            
            # Hacer scroll gradual para forzar la carga asíncrona de la vitrina completa
            for _ in range(6):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)
            
            # Capturar todas las tarjetas de productos posibles
            tarjetas = page.locator("li.product-item, div.product__item, div[class*='product-card'], article").all()
            print(f"    📊 Tarjetas detectadas en pantalla: {len(tarjetas)}")
            
            for tarjeta in tarjetas:
                try:
                    texto_tarjeta = tarjeta.inner_text()
                    
                    # FILTRO LÁSER ESTRICTO: Exigir el signo menos y un descuento de -50% o más
                    match_pct = re.search(r'-\s*(5[0-9]|[6-9]\d|100)\s*%', texto_tarjeta)
                    if not match_pct:
                        continue
                    
                    descuento_txt = match_pct.group(0).replace(" ", "")
                    
                    # Extraer enlace directo del producto
                    link_elem = tarjeta.locator("a[href*='/p/']").first
                    href = link_elem.get_attribute("href") if link_elem.count() > 0 else ""
                    if not href:
                        continue
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"
                    
                    # Extraer imagen principal
                    img_elem = tarjeta.locator("img").first
                    img_url = ""
                    if img_elem.count() > 0:
                        img_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or ""
                    
                    # Limpiar nombre y precios del bloque de texto
                    lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
                    nombre = next((l for l in lineas if len(l) > 10 and '$' not in l and '%' not in l), "Producto en Descuento Masivo")
                    
                    precios = [l for l in lineas if '$' in l]
                    precios_num = []
                    for p in precios:
                        num = re.sub(r'[^\d]', '', p)
                        if num and int(num) > 100000:
                            precios_num.append(int(num))
                    
                    precios_num = sorted(list(set(precios_num)), reverse=True)
                    if not precios_num:
                        continue
                        
                    precio_alto = precios_num[0]
                    precio_oferta = precios_num[-1] if len(precios_num) >= 2 else precio_alto
                    
                    str_precio_normal = f"${precio_alto:,.0f}".replace(",", ".")
                    str_precio_oferta = f"${precio_oferta:,.0f}".replace(",", ".")
                    img_final = img_url if img_url.startswith("http") else "https://via.placeholder.com/200?text=Alkosto"
                    
                    print(f"    🔥 [GANGÓN NAVEGADOR REAL {descuento_txt}] {nombre[:35]} | Oferta: {str_precio_oferta}")
                    
                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": str_precio_normal,
                        "Precio Oferta": str_precio_oferta,
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": img_final,
                        "Almacen": "Alkosto",
                        "Categoria": "Navegador Blindado"
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"--- [NAVEGADOR REAL ALKOSTO] Error en la ejecución: {str(e)} ---")
        finally:
            browser.close()
            
    print(f"\n--- [NAVEGADOR REAL ALKOSTO] TOTAL GANGAS REALES CAPTURADAS: {len(ofertas)} ---\n")
    return ofertas
