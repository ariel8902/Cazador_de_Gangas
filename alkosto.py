import re
import concurrent.futures
from playwright.sync_api import sync_playwright

def _ejecutar_en_hilo():
    ofertas = []
    with sync_playwright() as p:
        try:
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
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768}
            )
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            url = "https://www.alkosto.com/ofertas/c/ofertas-alkosto"
            print(f"    Navegando a: {url}")
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            page.wait_for_timeout(6000)

            for _ in range(6):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2500)
            
            # Selector enfocado estrictamente en la cuadrícula de productos de la vitrina (excluyendo filtros)
            tarjetas = page.locator("li.product-item, div.product__item, div.search-result-product, div[class*='product-card']").all()
            if not tarjetas:
                tarjetas = page.locator("article[class*='product'], div[class*='cluster']").all()
                
            print(f"    📊 Tarjetas reales de vitrina detectadas: {len(tarjetas)}")
            
            for index, tarjeta in enumerate(tarjetas):
                try:
                    texto_tarjeta = tarjeta.inner_text()
                    if not texto_tarjeta or len(texto_tarjeta) < 20:
                        continue
                    
                    # Buscar explícitamente el porcentaje de descuento (ej. 50%, -50%, etc.)
                    match_pct = re.search(r'(?:-\s*)?([4-9][0-9]|100)\s*%', texto_tarjeta)
                    if not match_pct:
                        continue
                    
                    descuento_num = int(match_pct.group(1))
                    if descuento_num < 40:
                        continue
                        
                    descuento_txt = f"-{descuento_num}%"
                    
                    link_elem = tarjeta.locator("a[href*='/p/']").first
                    href = link_elem.get_attribute("href") if link_elem.count() > 0 else ""
                    if not href:
                        link_elem = tarjeta.locator("a").first
                        href = link_elem.get_attribute("href") if link_elem.count() > 0 else ""
                    
                    if not href or '/p/' not in href:
                        continue
                        
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"
                    
                    img_elem = tarjeta.locator("img").first
                    img_url = ""
                    if img_elem.count() > 0:
                        img_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src") or ""
                    
                    lineas = [l.strip() for l in texto_tarjeta.split('\n') if l.strip()]
                    nombre = next((l for l in lineas if len(l) > 10 and '$' not in l and '%' not in l), "Producto en Descuento Masivo")
                    
                    precios = [l for l in lineas if '$' in l]
                    precios_num = []
                    for pr in precios:
                        num = re.sub(r'[^\d]', '', pr)
                        if num and int(num) > 50000:
                            precios_num.append(int(num))
                    
                    precios_num = sorted(list(set(precios_num)), reverse=True)
                    if not precios_num:
                        continue
                        
                    precio_alto = precios_num[0]
                    precio_oferta = precios_num[-1] if len(precios_num) >= 2 else precio_alto
                    
                    print(f"    🔥 [GANGÓN CAPTURADO {descuento_txt}] {nombre[:30]} | Precio: ${precio_oferta:,.0f}")

                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": f"${precio_alto:,.0f}".replace(",", "."),
                        "Precio Oferta": f"${precio_oferta:,.0f}".replace(",", "."),
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": img_url if img_url.startswith("http") else "https://via.placeholder.com/200?text=Alkosto",
                        "Almacen": "Alkosto",
                        "Categoria": "Navegador Hilo Aislado"
                    })
                except Exception:
                    continue
                    
            browser.close()
        except Exception as e:
            print(f"--- [Error crítico en Alkosto] {str(e)} ---")
            
    unicas = {o['Enlace Directo']: o for o in ofertas}.values()
    return list(unicas)

def extraer_alkosto(page_param=None):
    print("\n--- [ALKOSTO] Iniciando extractor en hilo aislado ---")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_ejecutar_en_hilo)
        try:
            return future.result(timeout=60)
        except Exception as e:
            print(f"--- [Error de Timeout/Hilo Alkosto] {str(e)} ---")
            return []
