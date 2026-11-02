import asyncio
import re
from playwright.async_api import async_playwright

async def _ejecutar_extractor():
    ofertas = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            url = "https://www.alkosto.com/ofertas/c/ofertas-alkosto"
            print(f"\n--- [NAVEGADOR ALKOSTO] Conectando a: {url} ---")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            for _ in range(5):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(2000)
            
            tarjetas = await page.locator("li.product-item, div.product__item, div[class*='product-card'], article").all()
            print(f"    📊 Tarjetas detectadas: {len(tarjetas)}")
            
            for tarjeta in tarjetas:
                try:
                    texto_tarjeta = await tarjeta.inner_text()
                    match_pct = re.search(r'-\s*(5[0-9]|[6-9]\d|100)\s*%', texto_tarjeta)
                    if not match_pct:
                        continue
                    
                    descuento_txt = match_pct.group(0).replace(" ", "")
                    
                    link_elem = tarjeta.locator("a[href*='/p/']").first
                    href = await link_elem.get_attribute("href") if await link_elem.count() > 0 else ""
                    if not href:
                        continue
                    enlace_producto = href if href.startswith("http") else f"https://www.alkosto.com{href}"
                    
                    img_elem = tarjeta.locator("img").first
                    img_url = ""
                    if await img_elem.count() > 0:
                        img_url = await img_elem.get_attribute("src") or await img_elem.get_attribute("data-src") or ""
                    
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
                    
                    ofertas.append({
                        "Nombre": nombre,
                        "Precio Normal": f"${precio_alto:,.0f}".replace(",", "."),
                        "Precio Oferta": f"${precio_oferta:,.0f}".replace(",", "."),
                        "Descuento": descuento_txt,
                        "Enlace Directo": enlace_producto,
                        "Imagen": img_url if img_url.startswith("http") else "https://via.placeholder.com/200?text=Alkosto",
                        "Almacen": "Alkosto",
                        "Categoria": "Navegador Blindado"
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"--- [Error Alkosto] {str(e)} ---")
        finally:
            await browser.close()
            
    print(f"\n--- [ALKOSTO] Total gangas capturadas: {len(ofertas)} ---\n")
    return ofertas

def extraer_alkosto(page_param=None):
    """Función puente síncrona compatible con el orquestador principal"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Si ya hay un loop corriendo, creamos la tarea de forma segura
            future = asyncio.run_coroutine_threadsafe(_ejecutar_extractor(), loop)
            return future.result()
        else:
            return asyncio.run(_ejecutar_extractor())
    except Exception as e:
        print(f"Error ejecutando extractor de Alkosto: {str(e)}")
        return []
