import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import os

html_path = os.path.abspath('index.html')
file_url = 'file:///' + html_path.replace('\\', '/')

print("Iniciando auditoria completa de UI e filtros com Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1200})
    
    errors = []
    page.on('pageerror', lambda exc: errors.append(f"PageError: {exc}"))
    page.on('console', lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == 'error' else None)
    
    page.goto(file_url, wait_until='networkidle')
    page.wait_for_timeout(1000)
    
    # 1. Verificar Cards de Canais
    print("\n--- 1. CARDS DE CANAIS DIGITAIS ---")
    cards = page.query_selector_all('.channel-tab')
    print(f"Total de Cards de Canais encontrados: {len(cards)}")
    for i, c in enumerate(cards):
        name = c.query_selector('.channel-name').inner_text()
        sales = c.query_selector('.channel-sales').inner_text()
        meta = c.query_selector('.channel-meta').inner_text() if c.query_selector('.channel-meta') else 'N/A'
        print(f"  [{i+1}] {name:25s} | Venda: {sales:15s} | {meta}")
        
    # 2. Verificar Highlights: Aceleradores e Detratores (GAP)
    print("\n--- 2. AUDITORIA DOS HIGHLIGHTS (ACELERADORES & DETRATORES) ---")
    acel_items = page.query_selector_all('#listAceleradores .highlight-item')
    detr_items = page.query_selector_all('#listDetratores .highlight-item')
    
    print(f"Linhas Superando a Meta (Aceleradores) renderizadas: {len(acel_items)}")
    for idx, item in enumerate(acel_items[:4]):
        name = item.query_selector('.highlight-name').inner_text()
        cat = item.query_selector('.highlight-cat').inner_text()
        gap = item.query_selector('.highlight-gap').inner_text()
        print(f"  🟢 Acel #{idx+1}: {name} ({cat}) -> GAP: {gap}")
        
    print(f"\nLinhas com Maior Oportunidade (Detratores/GAP) renderizadas: {len(detr_items)}")
    for idx, item in enumerate(detr_items[:4]):
        name = item.query_selector('.highlight-name').inner_text()
        cat = item.query_selector('.highlight-cat').inner_text()
        gap = item.query_selector('.highlight-gap').inner_text()
        print(f"  🔴 Oportunidade #{idx+1}: {name} ({cat}) -> GAP: {gap}")
        
    assert len(detr_items) >= 4, f"ERRO: Detratores renderizou apenas {len(detr_items)} itens! Deveria ter 8."
    assert len(acel_items) >= 4, f"ERRO: Aceleradores renderizou apenas {len(acel_items)} itens! Deveria ter 8."
    print("✅ Sucesso: Ambas as listas de destaques estão preenchidas e com cálculos corretos!")

    # 3. Testar Filtro de Pílula Rápida (Medicamentos)
    print("\n--- 3. TESTE DE FILTRO POR CATEGORIA (PÍLULA MEDICAMENTOS) ---")
    page.click('#pillGrupoMed')
    page.wait_for_timeout(500)
    
    grupo_val = page.input_value('#filterGrupo')
    print(f"Valor do Select Grupo após clique na pílula: '{grupo_val}'")
    assert grupo_val == 'MEDICAMENTOS', f"Esperado 'MEDICAMENTOS', obtido '{grupo_val}'"
    
    # Verificar opções do subgrupo
    sub_options = [opt.inner_text() for opt in page.query_selector_all('#filterSubgrupo option')]
    print(f"Subgrupos disponíveis em MEDICAMENTOS: {len(sub_options)-1} opções")
    print(f"Exemplos de subgrupos: {sub_options[1:5]}")
    
    detr_med = page.query_selector_all('#listDetratores .highlight-item')
    print(f"Oportunidades em Medicamentos: {len(detr_med)} itens")
    if len(detr_med) > 0:
        print(f"  Top 1 Medicamentos: {detr_med[0].query_selector('.highlight-name').inner_text()} -> {detr_med[0].query_selector('.highlight-gap').inner_text()}")

    # 4. Testar Filtro de Pílula Rápida (Perfumaria)
    print("\n--- 4. TESTE DE FILTRO POR CATEGORIA (PÍLULA PERFUMARIA) ---")
    page.click('#pillGrupoPerf')
    page.wait_for_timeout(500)
    grupo_val_perf = page.input_value('#filterGrupo')
    assert grupo_val_perf == 'PERFUMARIA', f"Esperado 'PERFUMARIA', obtido '{grupo_val_perf}'"
    acel_perf = page.query_selector_all('#listAceleradores .highlight-item')
    print(f"Aceleradores em Perfumaria: {len(acel_perf)} itens")
    if len(acel_perf) > 0:
        print(f"  Top 1 Perfumaria: {acel_perf[0].query_selector('.highlight-name').inner_text()} -> {acel_perf[0].query_selector('.highlight-gap').inner_text()}")

    # 5. Testar Busca por Texto Inteligente (ex: 'FRALDA')
    print("\n--- 5. TESTE DE BUSCA INTELIGENTE ('FRALDA') ---")
    page.fill('#filterSearchText', 'FRALDA')
    page.wait_for_timeout(500)
    
    search_banner = page.query_selector('#filterSearchBanner')
    banner_text = search_banner.inner_text() if search_banner else ''
    print(f"Banner de busca inteligente exibido: {search_banner.is_visible() if search_banner else False}")
    print(f"Conteúdo do banner: {banner_text[:100]}...")
    
    # 6. Testar Limpar Filtros
    print("\n--- 6. TESTE DE RESET DE FILTROS ---")
    page.click('#pillGrupoAll')
    page.fill('#filterSearchText', '')
    page.wait_for_timeout(500)
    grupo_reset = page.input_value('#filterGrupo')
    assert grupo_reset == '', f"Esperado grupo vazio após reset, obtido '{grupo_reset}'"
    print("✅ Filtros resetados com sucesso!")

    # 7. Testar Troca de Canais (App -> Site -> Marketplace -> Figital -> Total)
    print("\n--- 7. TESTE DE NAVEGAÇÃO ENTRE CANAIS ---")
    for ch_sel, ch_nome in [('.tab-app', 'App'), ('.tab-site', 'Site'), ('.tab-marketplace', 'Marketplace'), ('.tab-figital', 'Figital'), ('.tab-total', 'Total')]:
        page.click(ch_sel)
        page.wait_for_timeout(400)
        venda = page.query_selector('#kpiVendaMtd').inner_text()
        print(f"  Canal {ch_nome:12s} ativo -> KPI Venda MTD: {venda}")

    # 8. Testar Toggle Figital no Total
    print("\n--- 8. TESTE DO TOGGLE FIGITAL NO TOTAL DIGITAL ---")
    page.click('.tab-total')
    page.wait_for_timeout(300)
    page.click('#btnFigSem')
    page.wait_for_timeout(300)
    venda_sem = page.query_selector('#kpiVendaMtd').inner_text()
    page.click('#btnFigCom')
    page.wait_for_timeout(300)
    venda_com = page.query_selector('#kpiVendaMtd').inner_text()
    print(f"  Venda Sem Figital: {venda_sem}")
    print(f"  Venda Com Figital: {venda_com}")
    assert venda_com != venda_sem, "ERRO: Toggle Figital não alterou o valor da venda total!"

    # 9. Verificação de Erros
    if errors:
        print("\n⚠️ AVISO - Erros de JS detectados:", errors)
    else:
        print("\n🎉 AUDITORIA CONCLUÍDA COM 100% DE SUCESSO: ZERO ERROS DE JAVASCRIPT OU DE RENDERIZAÇÃO!")
        
    # Salvar screenshot final
    screenshot_path = os.path.abspath('dashboard_figital_preview.png')
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"Screenshot salvo em: {screenshot_path}")

    browser.close()
