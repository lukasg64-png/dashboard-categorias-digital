import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

url = 'https://lukasg64-png.github.io/dashboard-categorias-digital/'
print(f"Testando live URL: {url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(2500)
    
    print("\n--- 1. CARDS DE CANAIS NO AR ---")
    cards = page.query_selector_all('.channel-tab')
    print(f"Total cards: {len(cards)}")
    for c in cards:
        name = c.query_selector('.channel-name').inner_text()
        sales = c.query_selector('.channel-sales').inner_text()
        print(f"  {name} -> {sales}")
        
    print("\n--- 2. HIGHLIGHTS NO AR ---")
    detr = page.query_selector_all('#listDetratores .highlight-item')
    acel = page.query_selector_all('#listAceleradores .highlight-item')
    print(f"Detratores (Maior Oportunidade) no ar: {len(detr)} itens")
    for i, d in enumerate(detr[:3]):
        h_name = d.query_selector('.highlight-name').inner_text()
        h_gap = d.query_selector('.highlight-gap').inner_text()
        print(f"  Detr #{i+1}: {h_name} -> {h_gap}")
        
    print(f"Aceleradores no ar: {len(acel)} itens")
    for i, a in enumerate(acel[:3]):
        h_name = a.query_selector('.highlight-name').inner_text()
        h_gap = a.query_selector('.highlight-gap').inner_text()
        print(f"  Acel #{i+1}: {h_name} -> {h_gap}")
        
    print(f"\nErros de console no ar: {len(errors)}")
    if errors:
        print("Erros:", errors)
    else:
        print("✅ ZERO erros de console no site em produção!")
        
    browser.close()
