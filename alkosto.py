for tarjeta in tarjetas:
                try:
                    texto_tarjeta = tarjeta.inner_text()
                    
                    # Búsqueda flexible: acepta números de 50 a 100 seguidos de % (con o sin signo menos)
                    match_pct = re.search(r'(?:-\s*)?([5-9][0-9]|100)\s*%', texto_tarjeta)
                    if not match_pct:
                        continue
                    
                    descuento_num = int(match_pct.group(1))
                    if descuento_num < 50:
                        continue
                        
                    descuento_txt = f"-{descuento_num}%"
                    
                    link_elem = tarjeta.locator("a[href*='/p/']").first
                    href = link_elem.get_attribute("href") if link_elem.count() > 0 else ""
                    if not href:
                        # Intentar buscar cualquier enlace dentro de la tarjeta
                        link_elem = tarjeta.locator("a").first
                        href = link_elem.get_attribute("href") if link_elem.count() > 0 else ""
                    
                    if not href:
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
                        if num and int(num) > 50000: # Umbral de precio mínimo para evitar falsos positivos
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
