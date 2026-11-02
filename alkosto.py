# Esperar a que carguen los enlaces de productos de VTEX
            try:
                page.wait_for_selector("a[href*='/p/']", timeout=12000)
            except Exception:
                print("    ⚠️ Advertencia: Timeout esperando enlaces de productos...")

            # Hacer scroll gradual para activar el lazy load
            for _ in range(5):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(2000)
            
            # Apuntar directamente a los contenedores que posean enlaces de productos de Alkosto
            tarjetas = page.locator("div.product-item, li.product-item, div[class*='product-card'], article, div[class*='product-summary']").all()
            if not tarjetas or len(tarjetas) <= 1:
                # Si el contenedor general es muy amplio, capturamos los bloques 'article' o elementos de lista
                tarjetas = page.locator("article, li, div[class*='item']").all()
                
            print(f"    📊 Elementos de productos detectados: {len(tarjetas)}")
