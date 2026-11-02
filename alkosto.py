import re

async def extraer_alkosto(page):
    ofertas = []
    
    try:
        url = "https://www.alkosto.com/ofertas/c/ofertas-alkosto"
        print(f"\n--- [NAVEGADOR ALKOSTO] Navegando en página activa: {url} ---")
        
        # Usar la página que ya viene abierta del orquestador con timeout de seguridad de 25s
        await page.goto(url, timeout=25000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        
        # Hacer scroll moderado para cargar elementos
        for _ in range(4):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1500)
        
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
                    "Categoria": "Navegador Integrado"
                })
            except Exception:
                continue
                
    except Exception as e:
        print(f"--- [Error Alkosto] Timeout o fallo de red: {str(e)} ---")
        
    print(f"\n--- [ALKOSTO] Total gangas capturadas: {len(ofertas)} ---\n")
    return ofertas
