"""
build_dashboard.py — Compila o Dashboard Executivo Apple Design System das Farmácias São João.
Diagnóstico Macro to Micro (Causa-Raiz, Fornecedores, Subgrupos, Linhas e Itens).
Métricas completas: Meta, Realizado, Desvio R$ (GAP), Desvio %, Crescimento MoM (% e R$),
Evolução YoY (% e R$), Share %, Projeção de Fechamento.
Filtros: Canais (Total Digital, App, Site, Marketplace), Grupo, Subgrupo, Fornecedor/Lab e Busca por SKU.
Novo Gráfico Diário: Realizado Diário vs Meta Diária + Desvio % Diário vs Meta com eixo zero.
"""
import os, sys, time, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_JSON_PATH = os.path.join(DATA_DIR, 'dashboard_digital_data.json')
OUTPUT_HTML = os.path.join(BASE_DIR, 'index.html')

def build():
    t0 = time.time()
    print("=" * 70)
    print("  COMPILAÇÃO DO DASHBOARD EXECUTIVO DIGITAL: APPLE DESIGN SYSTEM")
    print("=" * 70)

    if not os.path.exists(DATA_JSON_PATH):
        print("Arquivo dashboard_digital_data.json não encontrado. Rodando process_digital_analytics...")
        import process_digital_analytics
        process_digital_analytics.main()

    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data_content = f.read()

    dash_data = json.loads(data_content)
    kpis_dict = dash_data.get('kpis', {})
    data_corte = kpis_dict.get('data_corte', '01 a 05/09/2026 (D-1)')
    max_dia = kpis_dict.get('max_dia', 5)
    max_dia_str = f"{max_dia:02d}"

    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Acompanhamento Digital — Farmácias São João (App, Site e Marketplace)</title>
  
  <!-- Apple Fonts (Outfit & Inter / SF Pro Stack) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <style>
    /* ==========================================================================
       FARMÁCIAS SÃO JOÃO — APPLE HUMAN INTERFACE GUIDELINES DESIGN SYSTEM
       ========================================================================== */
    
    :root {{
      /* Apple Light Palette */
      --bg-canvas: #F5F5F7;
      --surface: #FFFFFF;
      --surface-translucent: rgba(255, 255, 255, 0.85);
      --surface-hover: #F8F8FA;
      --surface-sunken: #EBEBED;
      --surface-subtle: #FAFAFC;

      --border: rgba(0, 0, 0, 0.08);
      --border-subtle: rgba(0, 0, 0, 0.04);
      --border-hover: rgba(0, 0, 0, 0.16);
      --separator: rgba(60, 60, 67, 0.12);

      --text-primary: #1D1D1F;
      --text-secondary: #6E6E73;
      --text-tertiary: #86868B;
      --text-quaternary: #A1A1A6;

      --apple-blue: #0071E3;
      --apple-blue-hover: #0077ED;
      --apple-blue-soft: rgba(0, 113, 227, 0.08);
      --apple-blue-border: rgba(0, 113, 227, 0.20);
      
      --apple-green: #34C759;
      --apple-green-soft: rgba(52, 199, 89, 0.12);
      --apple-green-text: #248A3D;
      --apple-green-border: rgba(52, 199, 89, 0.25);

      --apple-red: #FF3B30;
      --apple-red-soft: rgba(255, 59, 48, 0.12);
      --apple-red-text: #D70015;
      --apple-red-border: rgba(255, 59, 48, 0.25);

      --apple-orange: #FF9500;
      --apple-orange-soft: rgba(255, 149, 0, 0.12);
      --apple-orange-text: #C93400;
      --apple-orange-border: rgba(255, 149, 0, 0.25);

      --apple-indigo: #5856D6;
      --apple-indigo-soft: rgba(88, 86, 214, 0.12);
      --apple-purple: #AF52DE;
      --apple-purple-soft: rgba(175, 82, 222, 0.12);

      --radius-xs: 6px;
      --radius-sm: 10px;
      --radius-md: 14px;
      --radius-lg: 18px;
      --radius-xl: 24px;
      --radius-pill: 9999px;

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
      --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.06);
      --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.08);

      --chart-grid: rgba(0, 0, 0, 0.05);
      --chart-tooltip-bg: rgba(29, 29, 31, 0.92);
    }}

    [data-theme="dark"] {{
      --bg-canvas: #000000;
      --surface: #1C1C1E;
      --surface-translucent: rgba(28, 28, 30, 0.85);
      --surface-hover: #2C2C2E;
      --surface-sunken: #242426;
      --surface-subtle: #141416;

      --border: rgba(255, 255, 255, 0.12);
      --border-subtle: rgba(255, 255, 255, 0.06);
      --border-hover: rgba(255, 255, 255, 0.24);
      --separator: rgba(84, 84, 88, 0.35);

      --text-primary: #F5F5F7;
      --text-secondary: #98989D;
      --text-tertiary: #636366;
      --text-quaternary: #48484A;

      --apple-blue: #2997FF;
      --apple-blue-hover: #409CFF;
      --apple-blue-soft: rgba(41, 151, 255, 0.15);
      --apple-blue-border: rgba(41, 151, 255, 0.30);
      
      --apple-green: #30D158;
      --apple-green-soft: rgba(48, 209, 88, 0.15);
      --apple-green-text: #30D158;
      --apple-green-border: rgba(48, 209, 88, 0.30);

      --apple-red: #FF453A;
      --apple-red-soft: rgba(255, 69, 58, 0.15);
      --apple-red-text: #FF453A;
      --apple-red-border: rgba(255, 69, 58, 0.30);

      --apple-orange: #FF9F0A;
      --apple-orange-soft: rgba(255, 159, 10, 0.15);
      --apple-orange-text: #FF9F0A;
      --apple-orange-border: rgba(255, 159, 10, 0.30);

      --apple-indigo: #5E5CE6;
      --apple-indigo-soft: rgba(94, 92, 230, 0.15);
      --apple-purple: #BF5AF2;
      --apple-purple-soft: rgba(191, 90, 242, 0.15);

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.5);

      --chart-grid: rgba(255, 255, 255, 0.06);
      --chart-tooltip-bg: rgba(44, 44, 46, 0.95);
    }}

    /* Global Resets */
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.45;
      font-size: 14px;
      transition: background-color 0.3s ease, color 0.3s ease;
    }}

    .app-container {{
      max-width: 1540px;
      margin: 0 auto;
      padding: 24px 28px 60px 28px;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }}

    /* Top Navigation Bar */
    .nav-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 22px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow-sm);
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .brand-logo-mark {{
      width: 40px;
      height: 40px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, #0071E3, #0051A8);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #FFFFFF;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 18px;
      box-shadow: 0 4px 10px rgba(0, 113, 227, 0.35);
    }}

    .brand-text {{
      display: flex;
      flex-direction: column;
    }}

    .brand-title {{
      font-family: 'Outfit', -apple-system, sans-serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.4px;
    }}

    .brand-subtitle {{
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge-status {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: var(--radius-pill);
      font-size: 11.5px;
      font-weight: 600;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      color: var(--text-secondary);
    }}

    .status-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--apple-green);
      box-shadow: 0 0 6px var(--apple-green);
    }}

    .theme-toggle-btn {{
      background: var(--surface-hover);
      border: 1px solid var(--border);
      color: var(--text-primary);
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 16px;
      transition: all 0.2s ease;
    }}

    .theme-toggle-btn:hover {{
      background: var(--surface-sunken);
      border-color: var(--border-hover);
      transform: scale(1.05);
    }}

    /* Channel Selector (Segmented Cards) */
    .channel-nav-container {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
    }}

    .channel-tab {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 16px 18px;
      cursor: pointer;
      position: relative;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: var(--shadow-sm);
    }}

    .channel-tab:hover {{
      border-color: var(--apple-blue);
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }}

    .channel-tab.active {{
      border: 2px solid var(--apple-blue);
      background: var(--surface);
      box-shadow: 0 6px 18px rgba(0, 113, 227, 0.12);
    }}

    .channel-tab-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .channel-name {{
      font-family: 'Outfit', sans-serif;
      font-size: 15px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .channel-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      font-variant-numeric: tabular-nums;
    }}

    .channel-sales {{
      font-size: 20px;
      font-weight: 800;
      font-family: 'Outfit', -apple-system, sans-serif;
      letter-spacing: -0.5px;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
    }}

    .channel-meta-sub {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11.5px;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
    }}

    .channel-deltas-line {{
      display: flex;
      gap: 12px;
      font-size: 11px;
      border-top: 1px solid var(--border-subtle);
      padding-top: 6px;
      color: var(--text-tertiary);
      font-variant-numeric: tabular-nums;
    }}

    /* Global Filter Bar (Macro to Micro) */
    .filter-bar-section {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 18px 22px;
      box-shadow: var(--shadow-sm);
    }}

    .filter-bar-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}

    .filter-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 14px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .filter-chips-info {{
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .filter-inputs-grid {{
      display: grid;
      grid-template-columns: 1.2fr 1.2fr 1.4fr 1.5fr auto;
      gap: 12px;
      align-items: flex-end;
    }}

    .filter-control-group {{
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}

    .filter-control-group label {{
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      color: var(--text-secondary);
    }}

    .apple-select, .apple-input {{
      height: 38px;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 0 12px;
      font-size: 12.5px;
      color: var(--text-primary);
      font-family: inherit;
      outline: none;
      transition: all 0.2s ease;
      width: 100%;
    }}

    .apple-select:focus, .apple-input:focus {{
      border-color: var(--apple-blue);
      background: var(--surface);
      box-shadow: 0 0 0 3px var(--apple-blue-soft);
    }}

    .apple-btn-secondary {{
      height: 38px;
      padding: 0 14px;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .apple-btn-secondary:hover {{
      background: var(--surface-sunken);
      color: var(--apple-red-text);
      border-color: var(--apple-red-border);
    }}

    .filter-search-banner {{
      margin-top: 14px;
      padding: 10px 16px;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 12px;
      color: var(--text-secondary);
      animation: fadeIn 0.25s ease;
    }}

    .filter-badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 9px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      background: rgba(0, 113, 227, 0.1);
      color: var(--apple-blue);
      border: 1px solid rgba(0, 113, 227, 0.2);
    }}

    .filter-badge-pill.clickable {{
      cursor: pointer;
      transition: transform 0.15s ease, background 0.15s ease;
    }}

    .filter-badge-pill.clickable:hover {{
      background: rgba(0, 113, 227, 0.2);
      transform: translateY(-1px);
    }}

    .tab-badge {{
      display: inline-block;
      padding: 1px 6px;
      font-size: 10px;
      font-weight: 700;
      border-radius: 10px;
      background: rgba(0, 113, 227, 0.15);
      color: var(--apple-blue);
      margin-left: 4px;
      vertical-align: middle;
    }}

    /* Pílulas de Acesso Rápido a Categorias Macro */
    .filter-quick-pills {{
      display: flex;
      gap: 8px;
      margin-top: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
      align-items: center;
    }}

    .quick-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 11.5px;
      font-weight: 600;
      background: var(--surface-hover);
      color: var(--text-secondary);
      border: 1px solid var(--border);
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
    }}

    .quick-pill:hover {{
      background: var(--surface-sunken);
      color: var(--text-primary);
      border-color: var(--apple-blue);
      transform: translateY(-1px);
    }}

    .quick-pill.active {{
      background: var(--apple-blue);
      color: #FFFFFF !important;
      border-color: var(--apple-blue);
      box-shadow: 0 2px 8px var(--apple-blue-soft);
    }}

    /* Wrapper de Busca Inteligente com Botão Limpar e Spotlight Dropdown */
    .apple-search-wrapper {{
      position: relative;
      width: 100%;
    }}

    .apple-search-wrapper .apple-input {{
      padding-right: 32px;
    }}

    .search-clear-btn {{
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--surface-sunken);
      border: 1px solid var(--border);
      color: var(--text-tertiary);
      font-size: 11px;
      font-weight: 700;
      display: none;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      z-index: 5;
    }}

    .search-clear-btn:hover {{
      background: var(--apple-red);
      color: #FFFFFF;
      border-color: var(--apple-red);
    }}

    .quick-search-dropdown {{
      position: absolute;
      top: calc(100% + 6px);
      left: 0;
      right: 0;
      min-width: 320px;
      max-height: 400px;
      overflow-y: auto;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.2);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 1000;
      animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      padding: 6px 0;
    }}

    .quick-search-header {{
      padding: 6px 14px;
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-tertiary);
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      background: var(--surface-hover);
    }}

    .quick-search-item {{
      padding: 9px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: background 0.15s ease;
      border-bottom: 1px solid rgba(0, 0, 0, 0.03);
    }}

    .quick-search-item:hover {{
      background: var(--surface-hover);
    }}

    .quick-search-item:last-child {{
      border-bottom: none;
    }}

    .quick-search-info {{
      display: flex;
      flex-direction: column;
      gap: 2px;
      overflow: hidden;
      padding-right: 10px;
    }}

    .quick-search-title {{
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .quick-search-subtitle {{
      font-size: 11px;
      color: var(--text-tertiary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .quick-search-metric {{
      font-size: 11.5px;
      font-weight: 700;
      color: var(--apple-blue);
      white-space: nowrap;
      text-align: right;
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 14px;
    }}

    .kpi-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: var(--shadow-sm);
    }}

    .kpi-title {{
      font-size: 11.5px;
      color: var(--text-secondary);
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .kpi-value {{
      font-family: 'Outfit', -apple-system, sans-serif;
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.6px;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
    }}

    .kpi-subtext {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
      font-size: 10.5px;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}

    .badge-trend {{
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 2px 7px;
      border-radius: var(--radius-pill);
      font-weight: 700;
      font-size: 10.5px;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}

    .trend-pos {{
      background: var(--apple-green-soft);
      color: var(--apple-green-text);
      border: 1px solid var(--apple-green-border);
    }}

    .trend-neg {{
      background: var(--apple-red-soft);
      color: var(--apple-red-text);
      border: 1px solid var(--apple-red-border);
    }}

    .trend-neutral {{
      background: var(--apple-orange-soft);
      color: var(--apple-orange-text);
      border: 1px solid var(--apple-orange-border);
    }}

    .progress-bar-container {{
      width: 100%;
      height: 6px;
      background: var(--surface-sunken);
      border-radius: var(--radius-pill);
      overflow: hidden;
      margin-top: 6px;
    }}

    .progress-bar-fill {{
      height: 100%;
      border-radius: var(--radius-pill);
      transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* Main Chart and Side Insights Section */
    .section-charts {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      width: 100%;
    }}

    .chart-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 22px 24px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-sm);
      width: 100%;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .chart-title {{
      font-family: 'Outfit', -apple-system, sans-serif;
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
      letter-spacing: -0.3px;
    }}

    .chart-legend {{
      display: flex;
      gap: 14px;
      font-size: 11.5px;
      color: var(--text-secondary);
      font-weight: 500;
      flex-wrap: wrap;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-bullet {{
      width: 9px;
      height: 9px;
      border-radius: 3px;
    }}

    .chart-canvas-wrapper {{
      position: relative;
      width: 100%;
      height: 330px;
    }}

    /* Highlights Side-by-Side Panel Below Chart */
    .highlights-container {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      width: 100%;
    }}

    .highlight-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .highlight-card-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 13.5px;
      font-weight: 700;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .highlight-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .highlight-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 8px;
      border-radius: var(--radius-sm);
      background: var(--surface-subtle);
      border: 1px solid var(--border-subtle);
      font-size: 12px;
    }}

    .highlight-info {{
      display: flex;
      flex-direction: column;
      gap: 1px;
      max-width: 65%;
    }}

    .highlight-name {{
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .highlight-cat {{
      font-size: 10.5px;
      color: var(--text-tertiary);
    }}

    .highlight-metric {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}

    .highlight-gap {{
      font-weight: 700;
      font-size: 12px;
    }}

    /* Tables & Abas */
    .table-section {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 20px 24px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .table-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .apple-segmented-control {{
      display: inline-flex;
      background: var(--surface-sunken);
      padding: 3px;
      border-radius: var(--radius-md);
      gap: 2px;
    }}

    .segmented-btn {{
      background: transparent;
      border: none;
      padding: 7px 15px;
      border-radius: calc(var(--radius-md) - 2px);
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.18s ease;
      font-family: inherit;
    }}

    .segmented-btn:hover {{
      color: var(--text-primary);
    }}

    .segmented-btn.active {{
      background: var(--surface);
      color: var(--text-primary);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }}

    .sub-segmented-control {{
      display: inline-flex;
      background: var(--surface-subtle);
      border: 1px solid var(--border);
      padding: 2px;
      border-radius: var(--radius-sm);
      gap: 2px;
      margin-left: 8px;
    }}

    .sub-seg-btn {{
      background: transparent;
      border: none;
      padding: 4px 10px;
      border-radius: calc(var(--radius-sm) - 2px);
      font-size: 11px;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
    }}

    .sub-seg-btn.active {{
      background: var(--apple-blue);
      color: #FFFFFF;
    }}

    .table-tools-right {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .apple-btn-export {{
      height: 36px;
      padding: 0 14px;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .apple-btn-export:hover {{
      background: var(--surface-sunken);
      border-color: var(--border-hover);
    }}

    .table-responsive {{
      overflow-x: auto;
      max-height: 520px;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
    }}

    .data-table thead th {{
      position: sticky;
      top: 0;
      background: var(--surface-hover);
      color: var(--text-secondary);
      font-weight: 600;
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      font-size: 11.5px;
      letter-spacing: 0.3px;
      z-index: 2;
    }}

    .data-table tbody td {{
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
    }}

    .data-table tbody tr:hover {{
      background-color: var(--surface-hover);
    }}

    .num-cell {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}

    /* Raio-X Diagnóstico de Problemas (Aba 4) */
    .diagnostic-summary-card {{
      background: var(--surface-subtle);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 18px 22px;
      display: flex;
      gap: 20px;
      align-items: center;
      margin-bottom: 16px;
    }}

    .diag-icon-box {{
      font-size: 32px;
      line-height: 1;
    }}

    .diag-text {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .diag-text h4 {{
      font-family: 'Outfit', sans-serif;
      font-size: 15px;
      color: var(--text-primary);
    }}

    .diag-text p {{
      font-size: 12.5px;
      color: var(--text-secondary);
      line-height: 1.4;
    }}

    .diagnostic-grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }}

    .diag-col-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .diag-col-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-subtle);
    }}

    .diag-col-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* Footer */
    .footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 18px;
      border-top: 1px solid var(--border);
      font-size: 11.5px;
      color: var(--text-tertiary);
    }}

    @media (max-width: 1200px) {{
      .kpi-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .diagnostic-grid-3 {{ grid-template-columns: 1fr; }}
      .filter-inputs-grid {{ grid-template-columns: 1fr 1fr; }}
    }}

    @media (max-width: 900px) {{
      .highlights-container {{ grid-template-columns: 1fr; }}
      .chart-canvas-wrapper {{ height: 280px; }}
    }}

    @media (max-width: 768px) {{
      .channel-nav-container {{ grid-template-columns: 1fr; }}
      .kpi-grid {{ grid-template-columns: 1fr; }}
      .filter-inputs-grid {{ grid-template-columns: 1fr; }}
      .chart-canvas-wrapper {{ height: 250px; }}
    }}
  </style>
</head>
<body>

  <div class="app-container">
    
    <!-- Barra Superior Apple HIG -->
    <header class="nav-header">
      <div class="brand-group">
        <div class="brand-logo-mark">SJ</div>
        <div class="brand-text">
          <div class="brand-title">Acompanhamento Digital de Categorias</div>
          <div class="brand-subtitle">App São João • Site Oficial • Marketplaces (iFood, Rappi, E-commerce)</div>
        </div>
      </div>

      <div class="header-actions">
        <div class="badge-status">
          <div class="status-dot"></div>
          <span id="headerCutDate">{data_corte}</span>
        </div>
        <button class="theme-toggle-btn" onclick="toggleTheme()" title="Alternar Modo Claro / Escuro">
          🌓
        </button>
      </div>
    </header>

    <!-- Seletor de Canais (Segmented Cards) -->
    <section>
      <nav class="channel-nav-container">
        <!-- 1. Total Digital -->
        <div class="channel-tab tab-total active" onclick="switchChannel('total')">
          <div class="channel-tab-header">
            <span class="channel-name">🌐 Total Digital</span>
            <span class="channel-badge trend-pos" id="badgeAtingTotal">100.4%</span>
          </div>
          <div class="channel-sales" id="tabSalesTotal">R$ 5.897.259</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaTotal">R$ 5.875.260</strong></span>
            <span id="tabGapTotal" class="badge-trend trend-pos">+R$ 21.999</span>
          </div>
          <div class="channel-deltas-line">
            <span>Share: <strong style="color: var(--apple-blue);">100% Digital</strong></span>
            <span>YoY: <strong id="tabYoyTotal" style="color: var(--apple-green-text);">+43.2%</strong></span>
          </div>
        </div>

        <!-- 2. App -->
        <div class="channel-tab tab-app" onclick="switchChannel('app')">
          <div class="channel-tab-header">
            <span class="channel-name">📱 App</span>
            <span class="channel-badge trend-pos" id="badgeAtingApp">115.5% 🚀</span>
          </div>
          <div class="channel-sales" id="tabSalesApp">R$ 3.215.637</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaApp">R$ 2.784.144</strong></span>
            <span id="tabGapApp" class="badge-trend trend-pos">+R$ 431.494</span>
          </div>
          <div class="channel-deltas-line">
            <span>Share: <strong style="color: var(--apple-blue);">54.5%</strong></span>
            <span>YoY: <strong id="tabYoyApp" style="color: var(--apple-green-text);">+53.4%</strong></span>
          </div>
        </div>

        <!-- 3. Marketplace -->
        <div class="channel-tab tab-marketplace" onclick="switchChannel('marketplace')">
          <div class="channel-tab-header">
            <span class="channel-name">🛍️ Marketplace</span>
            <span class="channel-badge trend-pos" id="badgeAtingMkt">106.7% 🚀</span>
          </div>
          <div class="channel-sales" id="tabSalesMkt">R$ 1.638.913</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaMkt">R$ 1.535.631</strong></span>
            <span id="tabGapMkt" class="badge-trend trend-pos">+R$ 103.281</span>
          </div>
          <div class="channel-deltas-line">
            <span>Share: <strong style="color: var(--apple-blue);">27.8%</strong></span>
            <span>YoY: <strong id="tabYoyMkt" style="color: var(--apple-green-text);">+115.5%</strong></span>
          </div>
        </div>

        <!-- 4. Site -->
        <div class="channel-tab tab-site" onclick="switchChannel('site')">
          <div class="channel-tab-header">
            <span class="channel-name">💻 Site</span>
            <span class="channel-badge trend-neg" id="badgeAtingSite">67.0% ⚠️</span>
          </div>
          <div class="channel-sales" id="tabSalesSite">R$ 1.042.709</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaSite">R$ 1.555.484</strong></span>
            <span id="tabGapSite" class="badge-trend trend-neg">-R$ 512.775</span>
          </div>
          <div class="channel-deltas-line">
            <span>Share: <strong style="color: var(--apple-blue);">17.7%</strong></span>
            <span>YoY: <strong id="tabYoySite" style="color: var(--apple-red-text);">-17.4%</strong></span>
          </div>
        </div>
      </nav>
    </section>

    <!-- Barra de Filtros Interativos (Macro to Micro) -->
    <section class="filter-bar-section">
      <div class="filter-bar-header">
        <div class="filter-title">
          <span>🔍 Filtros de Diagnóstico Prático (Macro to Micro):</span>
        </div>
        <div class="filter-chips-info" id="filterActiveStatus">
          Visualizando todos os registros
        </div>
      </div>

      <!-- Pílulas de Acesso Rápido a Categorias Macro -->
      <div class="filter-quick-pills">
        <span class="quick-pill active" id="pillGrupoAll" onclick="selectQuickGrupo('')">⭐ Todos os Grupos</span>
        <span class="quick-pill" id="pillGrupoMed" onclick="selectQuickGrupo('Medicamentos(1)')">💊 Medicamentos (1)</span>
        <span class="quick-pill" id="pillGrupoPerf" onclick="selectQuickGrupo('Perfumaria(2)')">🧴 Perfumaria (2)</span>
        <span class="quick-pill" id="pillGrupoConv" onclick="selectQuickGrupo('Conveniencia(3)')">🍫 Conveniência (3)</span>
        <span class="quick-pill" id="pillGrupoHosp" onclick="selectQuickGrupo('Hospitalar(4)')">🏥 Hospitalar (4)</span>
      </div>

      <div class="filter-inputs-grid">
        <!-- 1. Grupo -->
        <div class="filter-control-group">
          <label for="filterGrupo">🏢 Categoria / Grupo</label>
          <select id="filterGrupo" class="apple-select" onchange="onFilterGrupoChange()">
            <option value="">Todos os Grupos (Macro)</option>
          </select>
        </div>

        <!-- 2. Subgrupo -->
        <div class="filter-control-group">
          <label for="filterSubgrupo">📂 Subgrupo (Intermediário)</label>
          <select id="filterSubgrupo" class="apple-select" onchange="onFilterSubgrupoChange()">
            <option value="">Todos os Subgrupos</option>
          </select>
        </div>

        <!-- 3. Fornecedor / Laboratório -->
        <div class="filter-control-group">
          <label for="filterLab">🏭 Fornecedor / Laboratório</label>
          <select id="filterLab" class="apple-select" onchange="onFilterLabChange()">
            <option value="">Todos os Fornecedores</option>
          </select>
        </div>

        <!-- 4. Busca Textual Universal com Spotlight -->
        <div class="filter-control-group">
          <label for="filterSearchText">🏷️ Busca Inteligente (SKU, Linha, Lab)</label>
          <div class="apple-search-wrapper">
            <input type="text" id="filterSearchText" class="apple-input" placeholder="Ex: Mounjaro, Fralda, Lilly, Ozempic, 10046653..." oninput="onSearchTextInput()" onfocus="onSearchTextInput()" onkeydown="onSearchKeyDown(event)" autocomplete="off">
            <button id="btnSearchClear" class="search-clear-btn" onclick="clearSearchInput()" title="Limpar busca">✕</button>
            <div id="quickSearchDropdown" class="quick-search-dropdown" style="display: none;"></div>
          </div>
        </div>

        <!-- 5. Limpar -->
        <div>
          <button class="apple-btn-secondary" onclick="resetGlobalFilters()" title="Limpar todos os filtros">
            ✕ Limpar Filtros
          </button>
        </div>
      </div>

      <!-- Banner de Feedback da Busca Inteligente -->
      <div id="filterSearchBanner" class="filter-search-banner" style="display: none;"></div>
    </section>

    <!-- Grid de 6 KPIs Estratégicos (100% Exclusivos e Não-Repetitivos) -->
    <section class="kpi-grid">
      <!-- 1. Faturamento Realizado MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Venda Realizada MTD</span>
          <span>💰</span>
        </div>
        <div class="kpi-value" id="kpiVendaMtd" style="color: var(--apple-blue);">R$ 5.897.259</div>
        <div class="kpi-subtext">
          <span>Meta MTD: <strong id="kpiMetaMtdRef" style="color: var(--text-primary);">R$ 5.875.260</strong></span>
          <span style="color: var(--text-tertiary);">• Curva: <strong id="kpiPctCurva">10.73%</strong></span>
        </div>
      </div>

      <!-- 2. Atingimento da Meta & GAP MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Atingimento & GAP MTD</span>
          <span>🎯</span>
        </div>
        <div class="kpi-value" id="kpiAtingMtd" style="color: var(--apple-green);">100.4%</div>
        <div class="kpi-subtext" style="display: flex; justify-content: space-between; align-items: center;">
          <span class="badge-trend trend-pos" id="kpiGapBadge">+R$ 21.999 Superávit</span>
          <span id="kpiDesvioPctRef" style="font-size: 11px; color: var(--text-secondary);">Desvio: +0.4%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" id="kpiProgressBar" style="width: 100%; background: var(--apple-green);"></div>
        </div>
      </div>

      <!-- 3. Diária Necessária (Run Rate) -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Diária Necessária (Run Rate)</span>
          <span>⚡</span>
        </div>
        <div class="kpi-value" id="kpiDiariaNec" style="color: var(--text-primary); font-size: 21px;">R$ 1.809.185 / dia</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiRitmoBadge">+R$ 156.6k/dia Ritmo</span>
          <span id="kpiDiasRestantesRef" style="color: var(--text-tertiary);">27d rest. (R$ 48.8M)</span>
        </div>
      </div>

      <!-- 4. Crescimento MoM (vs Ago/26) -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Crescimento MoM (vs Ago/26)</span>
          <span>📈</span>
        </div>
        <div class="kpi-value" id="kpiMoMValue" style="color: var(--apple-green);">+17.1%</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiMoMBadge">+R$ 861.946</span>
          <span id="kpiMoMPeriodRef" style="color: var(--text-tertiary);">vs 01 a {max_dia_str}/Ago</span>
        </div>
      </div>

      <!-- 5. Evolução YoY (vs Set/25) -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Evolução YoY (vs Set/25)</span>
          <span>🚀</span>
        </div>
        <div class="kpi-value" id="kpiYoYValue" style="color: var(--apple-green);">+43.2%</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiYoYBadge">+R$ 1.778.904</span>
          <span id="kpiYoYPeriodRef" style="color: var(--text-tertiary);">vs 01 a {max_dia_str}/Set/25</span>
        </div>
      </div>

      <!-- 6. Projeção de Fechamento -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Projeção de Fechamento</span>
          <span>🔮</span>
        </div>
        <div class="kpi-value" id="kpiProjecao" style="color: var(--apple-purple);">R$ 54.950.233</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiAtingProj">+R$ 205.0k vs Meta</span>
          <span id="kpiMetaMensalRef" style="color: var(--text-tertiary);">Meta: R$ 54.7M</span>
        </div>
      </div>
    </section>

    <!-- Gráfico Diário de Vendas e Metas com Desvio % -->
    <section class="section-charts">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span id="chartTitleText">📅 Curva Diária [Total Digital]: Realizado vs Meta Diária + Desvio % por Dia</span>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <div class="legend-bullet" style="background: var(--apple-blue);"></div>
              <span>Realizado Diário (R$)</span>
            </div>
            <div class="legend-item">
              <div class="legend-bullet" style="background: var(--surface-hover); border: 1px solid var(--border);"></div>
              <span>Meta Diária Oficial (R$)</span>
            </div>
            <div class="legend-item" style="display: flex; align-items: center; gap: 4px;">
              <span class="badge-trend trend-pos" style="font-size: 10px; padding: 1px 6px;">+8.3%</span>
              <span class="badge-trend trend-neg" style="font-size: 10px; padding: 1px 6px;">-8.3%</span>
              <span>Desvio % no Dia</span>
            </div>
          </div>
        </div>
        <div class="chart-canvas-wrapper">
          <canvas id="chartEvolucaoDiaria"></canvas>
        </div>
      </div>

      <!-- Destaques Rápidos Abaixo do Gráfico (Lado a Lado) -->
      <div class="highlights-container">
        <!-- Aceleradores -->
        <div class="highlight-card" style="border-top: 3px solid var(--apple-green);">
          <div class="highlight-card-title" style="color: var(--apple-green-text);">
            <span>🚀 Top Linhas Superando a Meta</span>
            <span class="badge-trend trend-pos" style="font-size: 11px; font-weight: 600;">Superávit MTD</span>
          </div>
          <div class="highlight-list" id="listAceleradores">
            <!-- Renderizado via JS -->
          </div>
        </div>

        <!-- Detratores -->
        <div class="highlight-card" style="border-top: 3px solid var(--apple-red);">
          <div class="highlight-card-title" style="color: var(--apple-red-text);">
            <span>⚠️ Top Linhas com Maior Oportunidade (GAP)</span>
            <span class="badge-trend trend-neg" style="font-size: 11px; font-weight: 600;">Déficit MTD</span>
          </div>
          <div class="highlight-list" id="listDetratores">
            <!-- Renderizado via JS -->
          </div>
        </div>
      </div>
    </section>

    <!-- Seção de Tabelas Multidimensionais com Abas Dedicadas -->
    <section class="table-section">
      <div class="table-toolbar">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <div class="apple-segmented-control">
            <button class="segmented-btn active" id="tabBtnCanais" onclick="switchTableTab('canais')">
              🌐 Canais (Consolidado)
            </button>
            <button class="segmented-btn" id="tabBtnHierarquia" onclick="switchTableTab('hierarquia')">
              🏢 Hierarquia <span id="badgeCountHierarquia" class="tab-badge" style="display:none;"></span>
            </button>
            <button class="segmented-btn" id="tabBtnLabs" onclick="switchTableTab('laboratorios')">
              🏭 Fornecedores <span id="badgeCountLabs" class="tab-badge" style="display:none;"></span>
            </button>
            <button class="segmented-btn" id="tabBtnDiagnostico" onclick="switchTableTab('diagnostico')">
              ⚠️ Raio-X de Problemas
            </button>
            <button class="segmented-btn" id="tabBtnSkus" onclick="switchTableTab('skus')">
              🏷️ Top SKUs <span id="badgeCountSkus" class="tab-badge" style="display:none;"></span>
            </button>
          </div>

          <!-- Sub-filtro para a Aba de Hierarquia -->
          <div class="sub-segmented-control" id="hierarquiaSubControl" style="display: none;">
            <button class="sub-seg-btn active" id="hierSubLinhas" onclick="switchHierarquiaView('linhas')">Linhas</button>
            <button class="sub-seg-btn" id="hierSubSubgrupos" onclick="switchHierarquiaView('subgrupos')">Subgrupos</button>
            <button class="sub-seg-btn" id="hierSubGrupos" onclick="switchHierarquiaView('grupos')">Grupos</button>
          </div>
        </div>

        <div class="table-tools-right">
          <button class="apple-btn-export" onclick="exportToCSV()" title="Exportar dados da tabela ativa para CSV">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Exportar CSV
          </button>
        </div>
      </div>

      <!-- Container da Tabela Principal -->
      <div id="tableContainerWrapper" class="table-responsive">
        <table class="data-table" id="mainDataTable">
          <thead id="tableHead"></thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>

      <!-- Container do Diagnóstico de Problemas (Aba 4) -->
      <div id="diagnosticoContainerWrapper" style="display: none;">
        <div class="diagnostic-summary-card">
          <div class="diag-icon-box">🎯</div>
          <div class="diag-text">
            <h4 id="diagSummaryTitle">Diagnóstico de Causa-Raiz Digital — Setembro 2026</h4>
            <p id="diagSummaryDesc">
              Identificação prática dos principais fornecedores, subgrupos e linhas que impedem ou aceleram o atingimento da meta no canal selecionado.
            </p>
          </div>
        </div>

        <div class="diagnostic-grid-3">
          <!-- Coluna 1: Fornecedores / Labs -->
          <div class="diag-col-card" style="border-top: 3px solid var(--apple-red);">
            <div class="diag-col-header">
              <span class="diag-col-title">🏭 Fornecedores / Laboratórios</span>
              <span class="badge-trend trend-neg">Detratores de Meta</span>
            </div>
            <div class="highlight-list" id="diagListDetratoresLabs"></div>
            
            <div class="diag-col-header" style="margin-top: 10px;">
              <span class="diag-col-title">🏭 Fornecedores / Laboratórios</span>
              <span class="badge-trend trend-pos">Aceleradores</span>
            </div>
            <div class="highlight-list" id="diagListAceleradoresLabs"></div>
          </div>

          <!-- Coluna 2: Subgrupos -->
          <div class="diag-col-card" style="border-top: 3px solid var(--apple-orange);">
            <div class="diag-col-header">
              <span class="diag-col-title">📂 Subgrupos de Produtos</span>
              <span class="badge-trend trend-neg">Detratores de Meta</span>
            </div>
            <div class="highlight-list" id="diagListDetratoresSubgrupos"></div>

            <div class="diag-col-header" style="margin-top: 10px;">
              <span class="diag-col-title">📂 Subgrupos de Produtos</span>
              <span class="badge-trend trend-pos">Aceleradores</span>
            </div>
            <div class="highlight-list" id="diagListAceleradoresSubgrupos"></div>
          </div>

          <!-- Coluna 3: Linhas -->
          <div class="diag-col-card" style="border-top: 3px solid var(--apple-blue);">
            <div class="diag-col-header">
              <span class="diag-col-title">📦 Linhas de Produtos</span>
              <span class="badge-trend trend-neg">Detratores de Meta</span>
            </div>
            <div class="highlight-list" id="diagListDetratoresLinhas"></div>

            <div class="diag-col-header" style="margin-top: 10px;">
              <span class="diag-col-title">📦 Linhas de Produtos</span>
              <span class="badge-trend trend-pos">Aceleradores</span>
            </div>
            <div class="highlight-list" id="diagListAceleradoresLinhas"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Rodapé Estilo Apple -->
    <footer class="footer">
      <div>
        <strong>Farmácias São João</strong> — Diretoria de E-commerce & Negócios Digitais
      </div>
      <div>
        Atualizado em: <span id="dataAtualizacao" style="font-variant-numeric: tabular-nums; font-weight: 600;">-</span> | Fonte: Qlik Sense Enterprise & Metas Diarizadas
      </div>
    </footer>

  </div>

  <!-- Injeção dos Dados no Script -->
  <script>
    window.DASHBOARD_DATA = {data_content};
  </script>

  <!-- Lógica da Aplicação -->
  <script>
    let activeChannel = 'total'; // 'total', 'app', 'site', 'marketplace'
    let activeTableTab = 'canais'; // 'canais', 'hierarquia', 'laboratorios', 'diagnostico', 'skus'
    let hierarquiaSubView = 'linhas'; // 'linhas', 'subgrupos', 'grupos'
    
    // Filtros Globais
    let selectedGrupo = '';
    let selectedSubgrupo = '';
    let selectedLab = '';
    let searchText = '';

    let chartInstance = null;

    const fmtMoney = (v) => {{
      if (v === null || v === undefined || isNaN(v)) return 'R$ 0';
      return new Intl.NumberFormat('pt-BR', {{ style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }}).format(v);
    }};

    const fmtPct = (v) => {{
      if (v === null || v === undefined || isNaN(v)) return '0.0%';
      return v.toFixed(1) + '%';
    }};

    const fmtSignPct = (v) => {{
      if (v === null || v === undefined || isNaN(v)) return '0.0%';
      return (v > 0 ? '+' : '') + v.toFixed(1) + '%';
    }};

    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('sj_digital_theme', next);
      renderChart();
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      const savedTheme = localStorage.getItem('sj_digital_theme');
      if (savedTheme) {{
        document.documentElement.setAttribute('data-theme', savedTheme);
      }}
      initDashboard();
    }});

    function initDashboard() {{
      const d = window.DASHBOARD_DATA;
      if (!d) return;

      document.getElementById('headerCutDate').textContent = d.kpis.data_corte;
      document.getElementById('dataAtualizacao').textContent = d.gerado_em;

      populateFilterDropdowns();
      updateChannelNavSummary();
      updateKpis();
      renderChart();
      renderHighlights();
      renderTable();

      // Fechar busca rápida ao clicar fora
      document.addEventListener('click', (e) => {{
        const wrapper = document.querySelector('.apple-search-wrapper');
        if (wrapper && !wrapper.contains(e.target)) {{
          closeQuickSearch();
        }}
      }});
    }}

    function normStr(str) {{
      return (str || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    }}

    function getSearchMatchesFromSkus(qNorm) {{
      if (!qNorm) return {{ linhas: new Set(), labs: new Set(), grupos: new Set(), subgrupos: new Set() }};
      const topSkus = window.DASHBOARD_DATA.top_skus || [];
      const matchingSkus = topSkus.filter(s => 
        String(s.id).includes(qNorm) || 
        normStr(s.nome).includes(qNorm) ||
        normStr(s.laboratorio).includes(qNorm) ||
        normStr(s.linha).includes(qNorm)
      );
      return {{
        linhas: new Set(matchingSkus.map(s => s.linha)),
        labs: new Set(matchingSkus.map(s => s.laboratorio)),
        grupos: new Set(matchingSkus.map(s => s.grupo)),
        subgrupos: new Set(matchingSkus.map(s => s.subgrupo))
      }};
    }}

    function getFilteredLinhas(ignoreCategoryFilters = false) {{
      let items = window.DASHBOARD_DATA.linhas || [];
      if (!ignoreCategoryFilters) {{
        if (selectedGrupo) items = items.filter(l => l.grupo === selectedGrupo);
        if (selectedSubgrupo) items = items.filter(l => l.subgrupo === selectedSubgrupo);
        if (selectedLab) items = items.filter(l => l.laboratorios && l.laboratorios.includes(selectedLab));
      }}
      if (searchText) {{
        const q = normStr(searchText);
        const skuMatches = getSearchMatchesFromSkus(q);
        items = items.filter(l => 
          normStr(l.linha).includes(q) ||
          normStr(l.subgrupo).includes(q) ||
          normStr(l.grupo).includes(q) ||
          (l.laboratorios && l.laboratorios.some(lab => normStr(lab).includes(q))) ||
          (l.skus && l.skus.some(s => normStr(s).includes(q))) ||
          skuMatches.linhas.has(l.linha)
        );
      }}
      return items;
    }}

    function getFilteredSubgrupos(ignoreCategoryFilters = false) {{
      let items = window.DASHBOARD_DATA.subgrupos || [];
      if (!ignoreCategoryFilters) {{
        if (selectedGrupo) items = items.filter(s => s.grupo === selectedGrupo);
        if (selectedSubgrupo) items = items.filter(s => s.subgrupo === selectedSubgrupo);
        if (selectedLab) items = items.filter(s => s.laboratorios && s.laboratorios.includes(selectedLab));
      }}
      if (searchText) {{
        const q = normStr(searchText);
        const fl = getFilteredLinhas(ignoreCategoryFilters);
        const matchedSubs = new Set(fl.map(l => l.subgrupo));
        const skuMatches = getSearchMatchesFromSkus(q);
        items = items.filter(s => 
          normStr(s.subgrupo).includes(q) ||
          normStr(s.grupo).includes(q) ||
          (s.laboratorios && s.laboratorios.some(lab => normStr(lab).includes(q))) ||
          matchedSubs.has(s.subgrupo) ||
          skuMatches.subgrupos.has(s.subgrupo)
        );
      }}
      return items;
    }}

    function getFilteredGrupos(ignoreCategoryFilters = false) {{
      let items = window.DASHBOARD_DATA.grupos || [];
      if (!ignoreCategoryFilters) {{
        if (selectedGrupo) items = items.filter(g => g.grupo === selectedGrupo);
        if (selectedLab) {{
          const filtros = window.DASHBOARD_DATA.filtros || {{}};
          items = items.filter(g => filtros.grupos_labs && filtros.grupos_labs[g.grupo] && filtros.grupos_labs[g.grupo].includes(selectedLab));
        }}
      }}
      if (searchText) {{
        const q = normStr(searchText);
        const fl = getFilteredLinhas(ignoreCategoryFilters);
        const matchedGrupos = new Set(fl.map(l => l.grupo));
        const skuMatches = getSearchMatchesFromSkus(q);
        items = items.filter(g => 
          normStr(g.grupo).includes(q) || 
          matchedGrupos.has(g.grupo) ||
          skuMatches.grupos.has(g.grupo)
        );
      }}
      return items;
    }}

    function getFilteredLaboratorios(ignoreCategoryFilters = false) {{
      let items = window.DASHBOARD_DATA.laboratorios || [];
      if (!ignoreCategoryFilters) {{
        if (selectedGrupo) items = items.filter(l => l.grupos && l.grupos.includes(selectedGrupo));
        if (selectedSubgrupo) items = items.filter(l => l.subgrupos && l.subgrupos.includes(selectedSubgrupo));
        if (selectedLab) items = items.filter(l => l.laboratorio === selectedLab);
      }}
      if (searchText) {{
        const q = normStr(searchText);
        const skuMatches = getSearchMatchesFromSkus(q);
        items = items.filter(l => 
          normStr(l.laboratorio).includes(q) ||
          (l.linhas && l.linhas.some(lin => normStr(lin).includes(q))) ||
          (l.grupos && l.grupos.some(grp => normStr(grp).includes(q))) ||
          (l.subgrupos && l.subgrupos.some(sub => normStr(sub).includes(q))) ||
          (l.skus && l.skus.some(s => normStr(s).includes(q))) ||
          skuMatches.labs.has(l.laboratorio)
        );
      }}
      return items;
    }}

    function getFilteredSkus(ignoreCategoryFilters = false) {{
      let items = window.DASHBOARD_DATA.top_skus || [];
      if (!ignoreCategoryFilters) {{
        if (selectedGrupo) items = items.filter(s => s.grupo === selectedGrupo);
        if (selectedSubgrupo) items = items.filter(s => s.subgrupo === selectedSubgrupo);
        if (selectedLab) items = items.filter(s => s.laboratorio === selectedLab);
      }}
      if (searchText) {{
        const q = normStr(searchText);
        items = items.filter(s => 
          String(s.id).includes(q) ||
          normStr(s.nome).includes(q) ||
          normStr(s.laboratorio).includes(q) ||
          normStr(s.linha).includes(q) ||
          normStr(s.subgrupo).includes(q) ||
          normStr(s.grupo).includes(q)
        );
      }}
      return items;
    }}

    function formatCanaisBlock(canaisObj) {{
      const chList = [
        {{ id: 'total', nome: 'Total Digital', icone: '🌐', key: 'total' }},
        {{ id: 'app', nome: 'App São João', icone: '📱', key: 'app' }},
        {{ id: 'marketplace', nome: 'Marketplaces', icone: '🛍️', key: 'marketplace' }},
        {{ id: 'site', nome: 'Site Oficial', icone: '🌐', key: 'site' }}
      ];
      return chList.map(item => {{
        const d = canaisObj[item.key] || {{}};
        return {{
          id: item.id,
          nome: item.nome,
          icone: item.icone,
          venda_mtd: d.realizado_mtd || 0,
          meta_mtd: d.meta_mtd || 0,
          ating_mtd_pct: d.ating_mtd_pct || 0,
          gap_mtd: d.gap_mtd || 0,
          desvio_pct: d.desvio_pct || 0,
          v26_06_mtd: d.v26_06_mtd || 0,
          crescimento_mom_pct: d.crescimento_mom_pct || 0,
          crescimento_mom_diff: d.crescimento_mom_diff || 0,
          v25_mtd: d.v25_mtd || 0,
          crescimento_yoy_pct: d.crescimento_yoy_pct || 0,
          crescimento_yoy_diff: d.crescimento_yoy_diff || 0,
          share_realizado_pct: d.share_pct || 0,
          projecao_fechamento: d.projecao_fechamento || 0,
          meta_mensal: d.meta_mensal || 0
        }};
      }});
    }}

    function getFilteredCanaisData() {{
      const isFilterActive = !!(selectedGrupo || selectedSubgrupo || selectedLab || searchText);
      if (!isFilterActive) {{
        return window.DASHBOARD_DATA.canais_tabela;
      }}

      // Caso 1: Apenas laboratório selecionado sem outros filtros
      if (selectedLab && !selectedGrupo && !selectedSubgrupo && !searchText) {{
        const labItem = (window.DASHBOARD_DATA.laboratorios || []).find(l => l.laboratorio === selectedLab);
        if (labItem && labItem.canais) {{
          return formatCanaisBlock(labItem.canais);
        }}
      }}

      // Caso 2: Apenas Subgrupo selecionado
      if (selectedSubgrupo && !selectedLab && !searchText) {{
        const subItem = (window.DASHBOARD_DATA.subgrupos || []).find(s => s.subgrupo === selectedSubgrupo && (!selectedGrupo || s.grupo === selectedGrupo));
        if (subItem && subItem.canais) {{
          return formatCanaisBlock(subItem.canais);
        }}
      }}

      // Caso 3: Apenas Grupo selecionado
      if (selectedGrupo && !selectedSubgrupo && !selectedLab && !searchText) {{
        const grpItem = (window.DASHBOARD_DATA.grupos || []).find(g => g.grupo === selectedGrupo);
        if (grpItem && grpItem.canais) {{
          return formatCanaisBlock(grpItem.canais);
        }}
      }}

      // Caso 4: Agregação genérica a partir das linhas filtradas
      const linhas = getFilteredLinhas();
      const channels = ['total', 'app', 'marketplace', 'site'];
      const channelNames = {{
        'total': 'Total Digital',
        'app': 'App São João',
        'marketplace': 'Marketplaces',
        'site': 'Site Oficial'
      }};
      const channelIcons = {{
        'total': '🌐',
        'app': '📱',
        'marketplace': '🛍️',
        'site': '🌐'
      }};

      const pctCurva = (window.DASHBOARD_DATA.kpis && window.DASHBOARD_DATA.kpis.pct_curva_acum) ? (window.DASHBOARD_DATA.kpis.pct_curva_acum / 100) : 0.1073;

      let totalRealizado = 0;
      const res = channels.map(ch => {{
        let r = 0, m_mtd = 0, m_mes = 0, v06 = 0, v25 = 0;
        linhas.forEach(l => {{
          const c = l.canais ? l.canais[ch] : null;
          if (c) {{
            r += c.realizado_mtd || 0;
            m_mtd += c.meta_mtd || 0;
            m_mes += c.meta_mensal || 0;
            v06 += c.v26_06_mtd || 0;
            v25 += c.v25_mtd || 0;
          }}
        }});

        r = Math.round(r * 100) / 100;
        m_mtd = Math.round(m_mtd * 100) / 100;
        m_mes = Math.round(m_mes * 100) / 100;
        v06 = Math.round(v06 * 100) / 100;
        v25 = Math.round(v25 * 100) / 100;

        if (ch === 'total') totalRealizado = r;

        const gap = Math.round((r - m_mtd) * 100) / 100;
        const ating = m_mtd > 0 ? ((r / m_mtd) * 100) : 0;
        const desvio = m_mtd > 0 ? (((r / m_mtd) - 1) * 100) : 0;
        const mom = v06 > 0 ? (((r - v06) / v06) * 100) : 0;
        const mom_diff = Math.round((r - v06) * 100) / 100;
        const yoy = v25 > 0 ? (((r - v25) / v25) * 100) : 0;
        const yoy_diff = Math.round((r - v25) * 100) / 100;
        const proj = pctCurva > 0 ? Math.round((r / pctCurva) * 100) / 100 : 0;

        return {{
          id: ch,
          nome: channelNames[ch],
          icone: channelIcons[ch],
          venda_mtd: r,
          meta_mtd: m_mtd,
          ating_mtd_pct: ating,
          gap_mtd: gap,
          desvio_pct: desvio,
          v26_06_mtd: v06,
          crescimento_mom_pct: mom,
          crescimento_mom_diff: mom_diff,
          v25_mtd: v25,
          crescimento_yoy_pct: yoy,
          crescimento_yoy_diff: yoy_diff,
          share_realizado_pct: 0,
          projecao_fechamento: proj,
          meta_mensal: m_mes
        }};
      }});

      res.forEach(c => {{
        if (c.id !== 'total' && totalRealizado > 0) {{
          c.share_realizado_pct = (c.venda_mtd / totalRealizado) * 100;
        }} else if (c.id === 'total') {{
          c.share_realizado_pct = 100;
        }}
      }});

      return res;
    }}

    function populateFilterDropdowns() {{
      const filtros = window.DASHBOARD_DATA.filtros || {{}};
      const grupoSel = document.getElementById('filterGrupo');
      grupoSel.innerHTML = '<option value="">Todos os Grupos (Macro)</option>';

      if (filtros.grupos) {{
        filtros.grupos.forEach(g => {{
          const opt = document.createElement('option');
          opt.value = g;
          opt.textContent = g;
          grupoSel.appendChild(opt);
        }});
      }}

      updateSubgrupoDropdown();
      updateLabDropdown();
    }}

    function updateSubgrupoDropdown() {{
      const filtros = window.DASHBOARD_DATA.filtros || {{}};
      const subgrupoSel = document.getElementById('filterSubgrupo');
      subgrupoSel.innerHTML = '<option value="">Todos os Subgrupos</option>';

      let subs = [];
      if (selectedGrupo && filtros.subgrupos && filtros.subgrupos[selectedGrupo]) {{
        subs = filtros.subgrupos[selectedGrupo];
      }} else if (!selectedGrupo && filtros.subgrupos) {{
        const allSubs = new Set();
        Object.values(filtros.subgrupos).forEach(list => list.forEach(s => allSubs.add(s)));
        subs = Array.from(allSubs).sort();
      }}

      let stillValid = false;
      subs.forEach(s => {{
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        if (s === selectedSubgrupo) {{
          opt.selected = true;
          stillValid = true;
        }}
        subgrupoSel.appendChild(opt);
      }});
      if (!stillValid) selectedSubgrupo = '';
    }}

    function updateLabDropdown() {{
      const filtros = window.DASHBOARD_DATA.filtros || {{}};
      const labSel = document.getElementById('filterLab');
      labSel.innerHTML = '<option value="">Todos os Fornecedores</option>';

      let labs = [];
      if (selectedSubgrupo && filtros.subgrupos_labs && filtros.subgrupos_labs[selectedSubgrupo]) {{
        labs = filtros.subgrupos_labs[selectedSubgrupo];
      }} else if (selectedGrupo && filtros.grupos_labs && filtros.grupos_labs[selectedGrupo]) {{
        labs = filtros.grupos_labs[selectedGrupo];
      }} else if (filtros.laboratorios) {{
        labs = filtros.laboratorios;
      }}

      let stillValid = false;
      labs.forEach(l => {{
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        if (l === selectedLab) {{
          opt.selected = true;
          stillValid = true;
        }}
        labSel.appendChild(opt);
      }});
      if (!stillValid) selectedLab = '';
    }}

    function onFilterGrupoChange() {{
      selectedGrupo = document.getElementById('filterGrupo').value;
      selectedSubgrupo = '';
      selectedLab = '';
      updateSubgrupoDropdown();
      updateLabDropdown();
      applyGlobalFilters();
    }}

    function onFilterSubgrupoChange() {{
      selectedSubgrupo = document.getElementById('filterSubgrupo').value;
      selectedLab = '';
      updateLabDropdown();
      applyGlobalFilters();
    }}

    function onFilterLabChange() {{
      selectedLab = document.getElementById('filterLab').value;
      applyGlobalFilters();
    }}

    function selectQuickGrupo(grp) {{
      document.getElementById('filterGrupo').value = grp;
      onFilterGrupoChange();
    }}

    function updateQuickPillsState() {{
      const g = selectedGrupo;
      const pills = [
        {{ id: 'pillGrupoAll', val: '' }},
        {{ id: 'pillGrupoMed', val: 'Medicamentos(1)' }},
        {{ id: 'pillGrupoPerf', val: 'Perfumaria(2)' }},
        {{ id: 'pillGrupoConv', val: 'Conveniencia(3)' }},
        {{ id: 'pillGrupoHosp', val: 'Hospitalar(4)' }}
      ];
      pills.forEach(p => {{
        const el = document.getElementById(p.id);
        if (el) {{
          if (p.val === g) {{
            el.classList.add('active');
          }} else {{
            el.classList.remove('active');
          }}
        }}
      }});
    }}

    function onSearchTextInput() {{
      const input = document.getElementById('filterSearchText');
      const val = input.value.trim();
      const clearBtn = document.getElementById('btnSearchClear');
      if (clearBtn) clearBtn.style.display = val ? 'inline-flex' : 'none';

      renderQuickSearchDropdown(val);
      applyGlobalFilters();
    }}

    function onSearchKeyDown(e) {{
      if (e.key === 'Escape') {{
        closeQuickSearch();
      }} else if (e.key === 'Enter') {{
        closeQuickSearch();
        const fskus = getFilteredSkus();
        const fl = getFilteredLinhas();
        
        // Se a busca não achou nada com os filtros de categoria atuais, mas tem resultados globais, limpa os filtros de categoria e reaplica
        if (fskus.length === 0 && fl.length === 0) {{
          const globalSkus = getFilteredSkus(true);
          const globalLinhas = getFilteredLinhas(true);
          if (globalSkus.length > 0 || globalLinhas.length > 0) {{
            resetCategoryFiltersKeepSearch();
            if (globalSkus.length > 0) {{
              switchTableTab('skus');
            }} else {{
              switchTableTab('hierarquia');
            }}
            return;
          }}
        }}

        if (fskus.length > 0 && activeTableTab === 'canais') {{
          switchTableTab('skus');
        }} else if (fl.length > 0 && activeTableTab === 'canais') {{
          switchTableTab('hierarquia');
        }}
      }}
    }}

    function clearSearchInput() {{
      const input = document.getElementById('filterSearchText');
      input.value = '';
      const clearBtn = document.getElementById('btnSearchClear');
      if (clearBtn) clearBtn.style.display = 'none';
      closeQuickSearch();
      applyGlobalFilters();
    }}

    function closeQuickSearch() {{
      const drop = document.getElementById('quickSearchDropdown');
      if (drop) drop.style.display = 'none';
    }}

    function renderQuickSearchDropdown(query) {{
      const drop = document.getElementById('quickSearchDropdown');
      if (!drop) return;

      if (!query || query.length < 2) {{
        drop.style.display = 'none';
        return;
      }}

      const qNorm = normStr(query);
      const skus = (window.DASHBOARD_DATA.top_skus || []).filter(s => 
        String(s.id).includes(qNorm) || 
        normStr(s.nome).includes(qNorm) ||
        normStr(s.laboratorio).includes(qNorm) ||
        normStr(s.linha).includes(qNorm)
      ).slice(0, 5);

      const linhas = (window.DASHBOARD_DATA.linhas || []).filter(l => 
        normStr(l.linha).includes(qNorm) || 
        normStr(l.subgrupo).includes(qNorm) ||
        normStr(l.grupo).includes(qNorm) ||
        (l.skus && l.skus.some(s => normStr(s).includes(qNorm)))
      );
      const seenLinhas = new Set();
      const uniqueLinhas = [];
      for (const l of linhas) {{
        if (!seenLinhas.has(l.linha)) {{
          seenLinhas.add(l.linha);
          uniqueLinhas.push(l);
          if (uniqueLinhas.length >= 4) break;
        }}
      }}

      const labs = (window.DASHBOARD_DATA.laboratorios || []).filter(l => 
        normStr(l.laboratorio).includes(qNorm)
      ).slice(0, 4);

      if (skus.length === 0 && uniqueLinhas.length === 0 && labs.length === 0) {{
        drop.innerHTML = `
          <div style="padding: 16px; text-align: center; color: var(--text-tertiary); font-size: 12px;">
            Nenhum resultado rápido para "${{query}}"<br>
            <span style="font-size: 11px;">(Pressione Enter para buscar em todas as tabelas)</span>
          </div>
        `;
        drop.style.display = 'block';
        return;
      }}

      let html = '';

      if (skus.length > 0) {{
        html += `<div class="quick-search-header"><span>🏷️ SKUs em Destaque</span><span style="font-size: 10px;">${{skus.length}}</span></div>`;
        skus.forEach(s => {{
          html += `
            <div class="quick-search-item" onclick="selectQuickSku('${{s.id}}', '${{s.nome.replace(/'/g, "\\'")}}')">
              <div class="quick-search-info">
                <span class="quick-search-title">${{s.id}} - ${{s.nome}}</span>
                <span class="quick-search-subtitle">${{s.laboratorio}} • ${{s.linha}}</span>
              </div>
              <div class="quick-search-metric">Meta: ${{fmtMoney(s.meta_mtd)}}</div>
            </div>
          `;
        }});
      }}

      if (uniqueLinhas.length > 0) {{
        html += `<div class="quick-search-header"><span>🏢 Linhas de Categoria</span><span style="font-size: 10px;">${{uniqueLinhas.length}}</span></div>`;
        uniqueLinhas.forEach(l => {{
          html += `
            <div class="quick-search-item" onclick="selectQuickLinha('${{l.linha.replace(/'/g, "\\'")}}')">
              <div class="quick-search-info">
                <span class="quick-search-title">${{l.linha}}</span>
                <span class="quick-search-subtitle">${{l.grupo}} • ${{l.subgrupo}}</span>
              </div>
              <div class="quick-search-metric" style="color: ${{l.gap_mtd >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">${{(l.gap_mtd >= 0 ? '+' : '') + fmtMoney(l.gap_mtd)}}</div>
            </div>
          `;
        }});
      }}

      if (labs.length > 0) {{
        html += `<div class="quick-search-header"><span>🏭 Fornecedores / Laboratórios</span><span style="font-size: 10px;">${{labs.length}}</span></div>`;
        labs.forEach(l => {{
          html += `
            <div class="quick-search-item" onclick="selectQuickLab('${{l.laboratorio.replace(/'/g, "\\'")}}')">
              <div class="quick-search-info">
                <span class="quick-search-title">${{l.laboratorio}}</span>
                <span class="quick-search-subtitle">${{(l.grupos || []).join(', ')}}</span>
              </div>
              <div class="quick-search-metric">Ating: ${{fmtPct(l.ating_mtd_pct)}}</div>
            </div>
          `;
        }});
      }}

      html += `
        <div style="padding: 8px 14px; background: var(--surface-hover); font-size: 11px; color: var(--text-tertiary); display: flex; justify-content: space-between; border-top: 1px solid var(--border);">
          <span>💡 Clique em qualquer item para filtrar diretamente</span>
          <span style="cursor: pointer; color: var(--apple-blue); font-weight: 600;" onclick="closeQuickSearch()">Fechar ✕</span>
        </div>
      `;

      drop.innerHTML = html;
      drop.style.display = 'block';
    }}

    function selectQuickSku(id, nome) {{
      const skuObj = (window.DASHBOARD_DATA.top_skus || []).find(s => String(s.id) === String(id));
      if (skuObj) {{
        // Sincroniza categoria real do SKU para garantir exibição
        document.getElementById('filterGrupo').value = skuObj.grupo || '';
        selectedGrupo = skuObj.grupo || '';
        updateSubgrupoDropdown();
        document.getElementById('filterSubgrupo').value = skuObj.subgrupo || '';
        selectedSubgrupo = skuObj.subgrupo || '';
        updateLabDropdown();
        document.getElementById('filterLab').value = skuObj.laboratorio || '';
        selectedLab = skuObj.laboratorio || '';
      }}
      document.getElementById('filterSearchText').value = id;
      closeQuickSearch();
      switchTableTab('skus');
      applyGlobalFilters();
    }}

    function selectQuickLinha(linha) {{
      const linhaObj = (window.DASHBOARD_DATA.linhas || []).find(l => l.linha === linha);
      if (linhaObj) {{
        document.getElementById('filterGrupo').value = linhaObj.grupo || '';
        selectedGrupo = linhaObj.grupo || '';
        updateSubgrupoDropdown();
        document.getElementById('filterSubgrupo').value = linhaObj.subgrupo || '';
        selectedSubgrupo = linhaObj.subgrupo || '';
        updateLabDropdown();
        document.getElementById('filterLab').value = '';
        selectedLab = '';
      }}
      document.getElementById('filterSearchText').value = linha;
      closeQuickSearch();
      switchTableTab('hierarquia');
      hierarquiaSubView = 'linhas';
      switchHierarquiaView('linhas');
      applyGlobalFilters();
    }}

    function selectQuickLab(lab) {{
      const labObj = (window.DASHBOARD_DATA.laboratorios || []).find(l => l.laboratorio === lab);
      if (labObj && selectedGrupo && !(labObj.grupos || []).includes(selectedGrupo)) {{
        document.getElementById('filterGrupo').value = '';
        selectedGrupo = '';
        updateSubgrupoDropdown();
      }}
      document.getElementById('filterSubgrupo').value = '';
      selectedSubgrupo = '';
      document.getElementById('filterLab').value = lab;
      selectedLab = lab;
      document.getElementById('filterSearchText').value = '';
      closeQuickSearch();
      switchTableTab('laboratorios');
      applyGlobalFilters();
    }}

    function selectLabDirect(lab) {{
      document.getElementById('filterLab').value = lab;
      selectedLab = lab;
      applyGlobalFilters();
    }}

    function selectSubgrupoDirect(sub, grp) {{
      if (grp) {{
        document.getElementById('filterGrupo').value = grp;
        selectedGrupo = grp;
        updateSubgrupoDropdown();
      }}
      document.getElementById('filterSubgrupo').value = sub;
      selectedSubgrupo = sub;
      updateLabDropdown();
      applyGlobalFilters();
    }}

    function filterByLinhaDirect(linha) {{
      document.getElementById('filterSearchText').value = linha;
      applyGlobalFilters();
    }}

    function removeSingleFilter(type) {{
      if (type === 'grupo') {{
        document.getElementById('filterGrupo').value = '';
        onFilterGrupoChange();
      }} else if (type === 'subgrupo') {{
        document.getElementById('filterSubgrupo').value = '';
        onFilterSubgrupoChange();
      }} else if (type === 'lab') {{
        document.getElementById('filterLab').value = '';
        onFilterLabChange();
      }} else if (type === 'search') {{
        clearSearchInput();
      }}
    }}

    function resetCategoryFiltersKeepSearch() {{
      document.getElementById('filterGrupo').value = '';
      document.getElementById('filterSubgrupo').value = '';
      document.getElementById('filterLab').value = '';
      selectedGrupo = '';
      selectedSubgrupo = '';
      selectedLab = '';
      updateSubgrupoDropdown();
      updateLabDropdown();
      applyGlobalFilters();
    }}

    function resetGlobalFilters() {{
      document.getElementById('filterGrupo').value = '';
      document.getElementById('filterSubgrupo').value = '';
      document.getElementById('filterLab').value = '';
      document.getElementById('filterSearchText').value = '';

      selectedGrupo = '';
      selectedSubgrupo = '';
      selectedLab = '';
      searchText = '';

      const clearBtn = document.getElementById('btnSearchClear');
      if (clearBtn) clearBtn.style.display = 'none';
      closeQuickSearch();

      updateSubgrupoDropdown();
      updateLabDropdown();
      applyGlobalFilters();
    }}

    function applyGlobalFilters() {{
      selectedGrupo = document.getElementById('filterGrupo').value;
      selectedSubgrupo = document.getElementById('filterSubgrupo').value;
      selectedLab = document.getElementById('filterLab').value;
      searchText = document.getElementById('filterSearchText').value.trim();

      // Sincronizar pílulas de grupos
      updateQuickPillsState();

      // Listas filtradas
      const fl = getFilteredLinhas();
      const flab = getFilteredLaboratorios();
      const fskus = getFilteredSkus();

      // Atualizar badges nas abas das tabelas
      const isFilterActive = !!(selectedGrupo || selectedSubgrupo || selectedLab || searchText);

      const bHier = document.getElementById('badgeCountHierarquia');
      if (bHier) {{
        bHier.style.display = isFilterActive ? 'inline-block' : 'none';
        bHier.textContent = fl.length;
      }}
      const bLabs = document.getElementById('badgeCountLabs');
      if (bLabs) {{
        bLabs.style.display = isFilterActive ? 'inline-block' : 'none';
        bLabs.textContent = flab.length;
      }}
      const bSkus = document.getElementById('badgeCountSkus');
      if (bSkus) {{
        bSkus.style.display = isFilterActive ? 'inline-block' : 'none';
        bSkus.textContent = fskus.length;
      }}

      // Chips de Filtros Ativos
      const activeParts = [];
      if (selectedGrupo) activeParts.push(`<span class="filter-badge-pill">🏢 Grupo: ${{selectedGrupo}} <span onclick="removeSingleFilter('grupo')" style="cursor:pointer;margin-left:4px;font-weight:bold;" title="Remover">✕</span></span>`);
      if (selectedSubgrupo) activeParts.push(`<span class="filter-badge-pill">📂 Subgrupo: ${{selectedSubgrupo}} <span onclick="removeSingleFilter('subgrupo')" style="cursor:pointer;margin-left:4px;font-weight:bold;" title="Remover">✕</span></span>`);
      if (selectedLab) activeParts.push(`<span class="filter-badge-pill">🏭 Fornecedor: ${{selectedLab}} <span onclick="removeSingleFilter('lab')" style="cursor:pointer;margin-left:4px;font-weight:bold;" title="Remover">✕</span></span>`);
      if (searchText) activeParts.push(`<span class="filter-badge-pill">🏷️ Busca: "${{searchText}}" <span onclick="removeSingleFilter('search')" style="cursor:pointer;margin-left:4px;font-weight:bold;" title="Remover">✕</span></span>`);

      if (activeParts.length > 1) {{
        activeParts.push(`<span class="filter-badge-pill clickable" onclick="resetGlobalFilters()" style="background: rgba(255, 59, 48, 0.12); color: var(--apple-red); border: 1px solid rgba(255, 59, 48, 0.25); font-weight: 600;" title="Limpar todos os filtros">✕ Limpar Tudo</span>`);
      }}

      const statusEl = document.getElementById('filterActiveStatus');
      if (activeParts.length > 0) {{
        statusEl.innerHTML = `<span style="color: var(--apple-blue); font-weight: 600; margin-right: 6px;">Filtros Ativos:</span> ` + activeParts.join(' ');
      }} else {{
        statusEl.textContent = 'Visualizando todos os registros';
      }}

      // Banner de busca inteligente com atalhos de visualização e aviso de escopo cruzado
      const searchBanner = document.getElementById('filterSearchBanner');
      if (searchBanner) {{
        if (searchText) {{
          searchBanner.style.display = 'flex';
          const hasZeroCategoryMatches = (fl.length === 0 && fskus.length === 0 && flab.length === 0);
          const hasCategoryFilters = !!(selectedGrupo || selectedSubgrupo || selectedLab);
          
          let conflictNotice = '';
          if (hasZeroCategoryMatches && hasCategoryFilters) {{
            const globalSkus = getFilteredSkus(true);
            const globalLinhas = getFilteredLinhas(true);
            const globalCount = globalSkus.length || globalLinhas.length;
            if (globalCount > 0) {{
              conflictNotice = `
                <div style="width: 100%; margin-top: 8px; background: rgba(255, 149, 0, 0.12); border: 1px solid rgba(255, 149, 0, 0.35); border-radius: 8px; padding: 7px 12px; display: flex; align-items: center; justify-content: space-between; font-size: 11.5px;">
                  <span>⚠️ Nenhum resultado no grupo <strong>${{selectedGrupo || selectedSubgrupo || selectedLab}}</strong>, mas encontramos <strong>${{globalCount}}</strong> itens em outras categorias!</span>
                  <button onclick="resetCategoryFiltersKeepSearch()" style="background: var(--apple-blue); color: white; border: none; border-radius: 6px; padding: 4px 10px; font-weight: 600; cursor: pointer; font-size: 11px; margin-left: 8px;">🔍 Buscar em Todo o Dashboard</button>
                </div>
              `;
            }}
          }}

          searchBanner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; width: 100%;">
              <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; flex: 1;">
                <span style="font-size: 13px;">🎯</span>
                <span>Resultados para "<strong>${{searchText}}</strong>":</span>
                <span class="filter-badge-pill clickable" onclick="switchTableTab('hierarquia')" title="Ver linhas encontradas">🏢 ${{fl.length}} Linhas</span>
                <span class="filter-badge-pill clickable" onclick="switchTableTab('laboratorios')" title="Ver fornecedores encontrados">🏭 ${{flab.length}} Fornecedores</span>
                <span class="filter-badge-pill clickable" onclick="switchTableTab('skus')" title="Ver SKUs encontrados">🏷️ ${{fskus.length}} SKUs</span>
                <span class="filter-badge-pill clickable" onclick="switchTableTab('canais')" title="Ver consolidação nos canais">🌐 Visão Canais</span>
              </div>
              <div style="font-size: 11px; color: var(--apple-blue); cursor: pointer; text-decoration: underline; font-weight: 600;" onclick="removeSingleFilter('search')">
                Limpar busca ✕
              </div>
              ${{conflictNotice}}
            </div>
          `;
        }} else {{
          searchBanner.style.display = 'none';
        }}
      }}

      updateChannelNavSummary();
      updateKpis();
      renderChart();
      renderHighlights();
      renderTable();
    }}

    function switchChannel(channelId) {{
      activeChannel = channelId;

      document.querySelectorAll('.channel-tab').forEach(tab => {{
        tab.classList.remove('active');
      }});
      const activeEl = document.querySelector(`.tab-${{channelId}}`);
      if (activeEl) activeEl.classList.add('active');

      updateKpis();
      renderChart();
      renderHighlights();
      renderTable();
      renderDiagnosticoView();
    }}

    function switchTableTab(tabId) {{
      activeTableTab = tabId;

      const btnMap = {{
        'canais': 'tabBtnCanais',
        'hierarquia': 'tabBtnHierarquia',
        'laboratorios': 'tabBtnLabs',
        'diagnostico': 'tabBtnDiagnostico',
        'skus': 'tabBtnSkus'
      }};

      document.querySelectorAll('.segmented-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(btnMap[tabId]);
      if (activeBtn) activeBtn.classList.add('active');

      const hierSub = document.getElementById('hierarquiaSubControl');
      hierSub.style.display = (tabId === 'hierarquia') ? 'inline-flex' : 'none';

      renderTable();
    }}

    function switchHierarquiaView(view) {{
      hierarquiaSubView = view;
      document.querySelectorAll('.sub-seg-btn').forEach(btn => btn.classList.remove('active'));
      if (view === 'linhas') document.getElementById('hierSubLinhas').classList.add('active');
      if (view === 'subgrupos') document.getElementById('hierSubSubgrupos').classList.add('active');
      if (view === 'grupos') document.getElementById('hierSubGrupos').classList.add('active');
      renderTable();
    }}

    function updateChannelNavSummary() {{
      const k = window.DASHBOARD_DATA.kpis.canais;
      
      const fillTab = (id, obj) => {{
        document.getElementById(`tabSales${{id}}`).textContent = fmtMoney(obj.venda_mtd);
        document.getElementById(`tabMeta${{id}}`).textContent = fmtMoney(obj.meta_mtd);
        document.getElementById(`badgeAting${{id}}`).textContent = fmtPct(obj.ating_mtd_pct) + (obj.ating_mtd_pct >= 100 ? ' 🚀' : '');
        
        const gapEl = document.getElementById(`tabGap${{id}}`);
        gapEl.textContent = (obj.gap_mtd >= 0 ? '+' : '') + fmtMoney(obj.gap_mtd);
        gapEl.className = 'badge-trend ' + (obj.gap_mtd >= 0 ? 'trend-pos' : 'trend-neg');

        const desvioEl = document.getElementById(`tabDesvioPct${{id}}`);
        if (desvioEl) {{
          desvioEl.textContent = fmtSignPct(obj.desvio_pct);
          desvioEl.style.color = obj.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';
        }}

        const momEl = document.getElementById(`tabMom${{id}}`);
        if (momEl) {{
          momEl.textContent = fmtSignPct(obj.crescimento_mom_pct);
          momEl.style.color = obj.crescimento_mom_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';
        }}

        const yoyEl = document.getElementById(`tabYoy${{id}}`);
        if (yoyEl) {{
          yoyEl.textContent = fmtSignPct(obj.crescimento_yoy_pct);
          yoyEl.style.color = obj.crescimento_yoy_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';
        }}
      }};

      fillTab('Total', k.total);
      fillTab('App', k.app);
      fillTab('Site', k.site);
      fillTab('Mkt', k.marketplace);
    }}

    function updateKpis() {{
      const canaisList = getFilteredCanaisData();
      const c = canaisList.find(item => item.id === activeChannel) || canaisList[0];
      const pctCurva = window.DASHBOARD_DATA.kpis.pct_curva_acum || 10.73;

      // 1. Venda Realizada MTD
      const elVenda = document.getElementById('kpiVendaMtd');
      if (elVenda) {{ elVenda.textContent = fmtMoney(c.venda_mtd); }}
      const metaRef = document.getElementById('kpiMetaMtdRef');
      if (metaRef) {{ metaRef.textContent = fmtMoney(c.meta_mtd); }}
      const curvaRef = document.getElementById('kpiPctCurva');
      if (curvaRef) {{ curvaRef.textContent = pctCurva + '%'; }}

      // 2. Atingimento & GAP MTD
      const ating = c.ating_mtd_pct;
      const atingElem = document.getElementById('kpiAtingMtd');
      if (atingElem) {{
        atingElem.textContent = fmtPct(ating);
        atingElem.style.color = ating >= 100 ? 'var(--apple-green)' : (ating >= 90 ? 'var(--apple-orange)' : 'var(--apple-red)');
      }}
      const barElem = document.getElementById('kpiProgressBar');
      if (barElem) {{
        barElem.style.width = Math.min(ating, 100) + '%';
        barElem.style.background = ating >= 100 ? 'var(--apple-green)' : (ating >= 90 ? 'var(--apple-orange)' : 'var(--apple-red)');
      }}
      const gapBadge = document.getElementById('kpiGapBadge');
      if (gapBadge) {{
        gapBadge.textContent = (c.gap_mtd >= 0 ? '+' : '') + fmtMoney(c.gap_mtd) + (c.gap_mtd >= 0 ? ' Superávit' : ' Déficit');
        gapBadge.className = 'badge-trend ' + (c.gap_mtd >= 0 ? 'trend-pos' : 'trend-neg');
      }}
      const desvioRef = document.getElementById('kpiDesvioPctRef');
      if (desvioRef) {{
        desvioRef.textContent = `Desvio: ${{fmtSignPct(c.desvio_pct)}}`;
      }}

      // 3. Diária Necessária (Run Rate)
      const diasRestantes = c.dias_restantes || 27;
      const diariaNec = c.diaria_necessaria !== undefined ? c.diaria_necessaria : (Math.max(0, (c.meta_mensal - c.venda_mtd)) / diasRestantes);
      const diariaElem = document.getElementById('kpiDiariaNec');
      if (diariaElem) {{ diariaElem.textContent = fmtMoney(diariaNec) + ' / dia'; }}

      const maxDiaVal = (window.DASHBOARD_DATA.kpis && window.DASHBOARD_DATA.kpis.max_dia) || 5;
      const maxDiaPad = String(maxDiaVal).padStart(2, '0');
      const ritmoDiff = c.ritmo_diff !== undefined ? c.ritmo_diff : ((c.venda_mtd / maxDiaVal) - diariaNec);
      const ritmoBadge = document.getElementById('kpiRitmoBadge');
      if (ritmoBadge) {{
        const isRitmoPos = ritmoDiff >= 0;
        ritmoBadge.textContent = (isRitmoPos ? '+' : '') + fmtMoney(ritmoDiff) + '/dia Ritmo';
        ritmoBadge.className = 'badge-trend ' + (isRitmoPos ? 'trend-pos' : 'trend-neg');
      }}
      const diasRef = document.getElementById('kpiDiasRestantesRef');
      if (diasRef) {{
        const falta = c.falta_para_meta !== undefined ? c.falta_para_meta : Math.max(0, (c.meta_mensal - c.venda_mtd));
        const faltaStr = falta >= 1000000 ? ('R$ ' + (falta / 1000000).toFixed(1) + 'M') : fmtMoney(falta);
        diasRef.textContent = diasRestantes + 'd rest. (' + faltaStr + ')';
      }}

      // 4. Crescimento MoM (vs Ago/26)
      const mom = c.crescimento_mom_pct || 0;
      const momElem = document.getElementById('kpiMoMValue');
      if (momElem) {{
        momElem.textContent = fmtSignPct(mom);
        momElem.style.color = mom >= 0 ? 'var(--apple-green)' : 'var(--apple-red)';
      }}
      const momBadge = document.getElementById('kpiMoMBadge');
      if (momBadge) {{
        momBadge.textContent = (c.crescimento_mom_diff >= 0 ? '+' : '') + fmtMoney(c.crescimento_mom_diff);
        momBadge.className = 'badge-trend ' + (c.crescimento_mom_diff >= 0 ? 'trend-pos' : 'trend-neg');
      }}
      const momRef = document.getElementById('kpiMoMPeriodRef');
      if (momRef) {{ momRef.textContent = `vs 01 a ${{maxDiaPad}}/Ago`; }}

      // 5. Evolução YoY (vs Set/25)
      const yoy = c.crescimento_yoy_pct || 0;
      const yoyElem = document.getElementById('kpiYoYValue');
      if (yoyElem) {{
        yoyElem.textContent = fmtSignPct(yoy);
        yoyElem.style.color = yoy >= 0 ? 'var(--apple-green)' : 'var(--apple-red)';
      }}
      const yoyBadge = document.getElementById('kpiYoYBadge');
      if (yoyBadge) {{
        yoyBadge.textContent = (c.crescimento_yoy_diff >= 0 ? '+' : '') + fmtMoney(c.crescimento_yoy_diff);
        yoyBadge.className = 'badge-trend ' + (c.crescimento_yoy_diff >= 0 ? 'trend-pos' : 'trend-neg');
      }}
      const yoyRef = document.getElementById('kpiYoYPeriodRef');
      if (yoyRef) {{ yoyRef.textContent = `vs 01 a ${{maxDiaPad}}/Set/25`; }}

      // 6. Projeção de Fechamento
      const projElem = document.getElementById('kpiProjecao');
      if (projElem) {{ projElem.textContent = fmtMoney(c.projecao_fechamento); }}
      const gapProj = (c.projecao_fechamento || 0) - (c.meta_mensal || 0);
      const atingProjElem = document.getElementById('kpiAtingProj');
      if (atingProjElem) {{
        const gapAbs = Math.abs(gapProj);
        const gapProjStr = gapAbs >= 1000000 ? ('R$ ' + (gapAbs / 1000000).toFixed(1) + 'M') : (gapAbs >= 1000 ? ('R$ ' + (gapAbs / 1000).toFixed(1) + 'k') : fmtMoney(gapAbs));
        atingProjElem.textContent = (gapProj >= 0 ? '+' : '-') + gapProjStr + ' vs Meta';
        atingProjElem.className = 'badge-trend ' + (gapProj >= 0 ? 'trend-pos' : 'trend-neg');
      }}
      const metaMesElem = document.getElementById('kpiMetaMensalRef');
      if (metaMesElem) {{
        const metaM = (c.meta_mensal / 1000000).toFixed(1);
        metaMesElem.textContent = 'Meta Mês: R$ ' + metaM + 'M';
      }}
    }}

    /* NOVO GRÁFICO DIÁRIO COM DESVIO % POR DIA (SOLICITADO PELO USUÁRIO) */
    function renderChart() {{
      const curva = window.DASHBOARD_DATA.curva_diaria;
      const ctx = document.getElementById('chartEvolucaoDiaria').getContext('2d');
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

      const labels = curva.map(c => `${{c.dia}} (${{c.dow}})`);
      
      let realKey = 'real_dia_total';
      let metaKey = 'meta_dia_total';
      let desvioKey = 'desvio_dia_total';
      let channelLabel = 'Total Digital';

      if (activeChannel === 'app') {{
        realKey = 'real_dia_app'; metaKey = 'meta_dia_app'; desvioKey = 'desvio_dia_app';
        channelLabel = 'Canal App';
      }} else if (activeChannel === 'site') {{
        realKey = 'real_dia_site'; metaKey = 'meta_dia_site'; desvioKey = 'desvio_dia_site';
        channelLabel = 'Canal Site';
      }} else if (activeChannel === 'marketplace') {{
        realKey = 'real_dia_mkt'; metaKey = 'meta_dia_mkt'; desvioKey = 'desvio_dia_mkt';
        channelLabel = 'Canal Marketplace';
      }}

      // Atualizar título do gráfico com o canal ativo
      const isFiltered = !!(selectedGrupo || selectedSubgrupo || selectedLab || searchText);
      const titleElem = document.getElementById('chartTitleText');
      if (titleElem) {{
        if (isFiltered) {{
          titleElem.innerHTML = `📅 Curva Diária [${{channelLabel}}]: Realizado vs Meta Diária + Desvio % por Dia <span style="font-size: 11px; font-weight: 600; color: var(--apple-blue); background: rgba(0, 113, 227, 0.1); padding: 2px 8px; border-radius: 10px; border: 1px solid rgba(0, 113, 227, 0.2); margin-left: 6px;">Consolidado do Canal</span>`;
        }} else {{
          titleElem.textContent = `📅 Curva Diária [${{channelLabel}}]: Realizado vs Meta Diária + Desvio % por Dia`;
        }}
      }}

      const dataReal = curva.map(c => c[realKey]);
      const dataMeta = curva.map(c => c[metaKey]);
      const dataDesvio = curva.map(c => c[desvioKey]);

      if (chartInstance) chartInstance.destroy();

      const blueColor = isDark ? '#2997FF' : '#0071E3';
      const metaBarColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)';
      const textColor = isDark ? '#8E8E93' : '#86868B';

      // Plugin Apple Design: desenha badges elegantes com o % de Desvio flutuando diretamente sobre cada barra realizada
      const desvioBadgesPlugin = {{
        id: 'desvioBadges',
        afterDatasetsDraw(chart) {{
          const {{ ctx }} = chart;
          const realMeta = chart.getDatasetMeta(0);
          if (!realMeta || !chart.data.datasets[0] || !chart.data.datasets[1]) return;

          const realData = chart.data.datasets[0].data;
          const metaData = chart.data.datasets[1].data;

          realMeta.data.forEach((bar, idx) => {{
            const realVal = realData[idx];
            const metaVal = metaData[idx];
            if (realVal === null || realVal === undefined || realVal <= 0) return;
            if (!metaVal || metaVal <= 0) return;

            const desvio = ((realVal - metaVal) / metaVal) * 100;
            const isPos = desvio >= 0;
            const text = (isPos ? '+' : '') + desvio.toFixed(1) + '%';

            ctx.save();
            ctx.font = '700 11px -apple-system, BlinkMacSystemFont, "SF Pro Text", "Outfit", sans-serif';
            const textWidth = ctx.measureText(text).width;
            const badgeW = textWidth + 14;
            const badgeH = 20;
            const badgeX = bar.x - badgeW / 2;
            const badgeY = bar.y - badgeH - 7;

            // Sombra suave
            ctx.shadowColor = isDark ? 'rgba(0, 0, 0, 0.45)' : 'rgba(0, 0, 0, 0.08)';
            ctx.shadowBlur = 5;
            ctx.shadowOffsetY = 2;

            // Fundo e borda arredondada estilo Apple pill
            ctx.fillStyle = isDark
              ? (isPos ? 'rgba(48, 209, 88, 0.22)' : 'rgba(255, 69, 58, 0.22)')
              : (isPos ? '#EBF9F0' : '#FDF0EE');
            ctx.strokeStyle = isPos ? (isDark ? '#30D158' : '#34C759') : (isDark ? '#FF453A' : '#FF3B30');
            ctx.lineWidth = 1.2;

            ctx.beginPath();
            if (ctx.roundRect) {{
              ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 10);
            }} else {{
              ctx.rect(badgeX, badgeY, badgeW, badgeH);
            }}
            ctx.fill();
            ctx.stroke();

            // Texto do % de Desvio
            ctx.shadowColor = 'transparent';
            ctx.fillStyle = isPos ? (isDark ? '#30D158' : '#248A3D') : (isDark ? '#FF453A' : '#D70015');
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(text, bar.x, badgeY + badgeH / 2);

            ctx.restore();
          }});
        }}
      }};

      chartInstance = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Realizado Diário',
              data: dataReal,
              backgroundColor: blueColor,
              borderRadius: 6,
              yAxisID: 'y',
              order: 1,
              maxBarThickness: 32
            }},
            {{
              label: 'Meta Diária Oficial',
              data: dataMeta,
              backgroundColor: metaBarColor,
              borderRadius: 6,
              yAxisID: 'y',
              order: 2,
              maxBarThickness: 32
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'index', intersect: false }},
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              backgroundColor: isDark ? 'rgba(44, 44, 46, 0.96)' : 'rgba(29, 29, 31, 0.94)',
              titleColor: '#FFFFFF',
              bodyColor: '#E5E5EA',
              padding: 12,
              cornerRadius: 10,
              callbacks: {{
                label: function(context) {{
                  const val = context.parsed.y;
                  if (val === null || val === undefined) return '';
                  return `${{context.dataset.label}}: ${{fmtMoney(val)}}`;
                }},
                afterBody: function(contexts) {{
                  if (!contexts || !contexts.length) return [];
                  const idx = contexts[0].dataIndex;
                  const c = curva[idx];
                  const real = c[realKey];
                  const meta = c[metaKey];
                  if (real && meta && real > 0) {{
                    const desvio = ((real - meta) / meta) * 100;
                    const gap = real - meta;
                    const sign = desvio >= 0 ? '+' : '';
                    return [
                      '───────────────────────',
                      `Desvio % vs Meta: ${{sign}}${{desvio.toFixed(1)}}% ${{desvio >= 0 ? '🟢 (Superávit)' : '🔴 (Déficit)'}}`,
                      `GAP no Dia: ${{gap >= 0 ? '+' : ''}}${{fmtMoney(gap)}}`
                    ];
                  }}
                  return [];
                }}
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{ display: false }},
              ticks: {{ color: textColor, font: {{ size: 11 }} }}
            }},
            y: {{
              position: 'left',
              grace: '18%',
              grid: {{ color: gridColor }},
              ticks: {{
                color: textColor,
                font: {{ size: 11 }},
                callback: v => (v / 1000).toFixed(0) + 'k'
              }}
            }}
          }}
        }},
        plugins: [desvioBadgesPlugin]
      }});
    }}

    function renderHighlights() {{
      const chLabel = activeChannel === 'total' ? 'Digital' : (activeChannel === 'app' ? 'App' : (activeChannel === 'site' ? 'Site' : 'Marketplace'));
      const tAcel = document.getElementById('titleAceleradores');
      const tDetr = document.getElementById('titleDetratores');
      if (tAcel) tAcel.textContent = `🚀 Top Linhas Superando a Meta (${{chLabel}})`;
      if (tDetr) tDetr.textContent = `⚠️ Top Linhas com Maior Oportunidade (${{chLabel}})`;

      const filteredLinhas = getFilteredLinhas();
      const itemsChannel = filteredLinhas.map(l => {{
        const ch = (l.canais && l.canais[activeChannel]) ? l.canais[activeChannel] : {{
          realizado_mtd: l.realizado_mtd,
          meta_mtd: l.meta_mtd,
          gap_mtd: l.gap_mtd,
          desvio_pct: l.desvio_pct,
          ating_mtd_pct: l.ating_mtd_pct,
          crescimento_mom_pct: l.crescimento_mom_pct
        }};
        return {{
          linha: l.linha,
          grupo: l.grupo,
          subgrupo: l.subgrupo,
          realizado_mtd: ch.realizado_mtd || 0,
          meta_mtd: ch.meta_mtd || 0,
          gap_mtd: ch.gap_mtd || 0,
          desvio_pct: ch.desvio_pct || 0,
          ating_mtd_pct: ch.ating_mtd_pct || 0
        }};
      }});

      // Agrupar por nome da linha para consolidar métricas
      const linhaMap = new Map();
      itemsChannel.forEach(item => {{
        if (!linhaMap.has(item.linha)) {{
          linhaMap.set(item.linha, {{ ...item }});
        }} else {{
          const ex = linhaMap.get(item.linha);
          ex.realizado_mtd += item.realizado_mtd;
          ex.meta_mtd += item.meta_mtd;
          ex.gap_mtd = ex.realizado_mtd - ex.meta_mtd;
          ex.ating_mtd_pct = ex.meta_mtd > 0 ? (ex.realizado_mtd / ex.meta_mtd) * 100 : 0;
          ex.desvio_pct = ex.meta_mtd > 0 ? ((ex.realizado_mtd / ex.meta_mtd) - 1) * 100 : 0;
        }}
      }});

      const uniqueItems = Array.from(linhaMap.values());

      const acel = uniqueItems
        .filter(x => x.gap_mtd > 0)
        .sort((a, b) => b.gap_mtd - a.gap_mtd)
        .slice(0, 8);

      const detr = uniqueItems
        .filter(x => x.gap_mtd < 0)
        .sort((a, b) => a.gap_mtd - b.gap_mtd)
        .slice(0, 8);

      const renderList = (items, isPositive) => {{
        if (!items || items.length === 0) {{
          return `<div style="padding: 18px; text-align: center; color: var(--text-tertiary); font-size: 12px;">Nenhum destaque para o filtro selecionado</div>`;
        }}
        return items.map((item, idx) => `
          <div class="highlight-item" onclick="filterByLinhaDirect('${{item.linha.replace(/'/g, "\\'")}}')" style="cursor: pointer;" title="Clique para filtrar por ${{item.linha}}">
            <div class="highlight-info">
              <span class="highlight-name" title="${{item.linha}}">
                <span style="color: var(--text-tertiary); font-size: 11px; margin-right: 4px; font-weight: 600;">#${{idx + 1}}</span>${{item.linha}}
              </span>
              <span class="highlight-cat">${{item.grupo || ''}} • Ating: ${{fmtPct(item.ating_mtd_pct)}}</span>
            </div>
            <div class="highlight-metric">
              <div class="highlight-gap" style="color: ${{isPositive ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{(item.gap_mtd >= 0 ? '+' : '') + fmtMoney(item.gap_mtd)}}
              </div>
              <div style="font-size: 11px; color: var(--text-tertiary);">Desvio: ${{fmtSignPct(item.desvio_pct)}}</div>
            </div>
          </div>
        `).join('');
      }};

      document.getElementById('listAceleradores').innerHTML = renderList(acel, true);
      document.getElementById('listDetratores').innerHTML = renderList(detr, false);
    }}

    function renderTable() {{
      const tableWrapper = document.getElementById('tableContainerWrapper');
      const diagWrapper = document.getElementById('diagnosticoContainerWrapper');
      const thead = document.getElementById('tableHead');
      const tbody = document.getElementById('tableBody');

      if (activeTableTab === 'diagnostico') {{
        tableWrapper.style.display = 'none';
        diagWrapper.style.display = 'block';
        renderDiagnosticoView();
        return;
      }}

      tableWrapper.style.display = 'block';
      diagWrapper.style.display = 'none';

      if (activeTableTab === 'canais') {{
        renderCanaisTable(thead, tbody);
      }} else if (activeTableTab === 'hierarquia') {{
        renderHierarquiaTable(thead, tbody);
      }} else if (activeTableTab === 'laboratorios') {{
        renderLaboratoriosTable(thead, tbody);
      }} else if (activeTableTab === 'skus') {{
        renderSkusTable(thead, tbody);
      }}
    }}

    /* ABA 1: Visão Geral de Canais */
    function renderCanaisTable(thead, tbody) {{
      thead.innerHTML = `
        <tr>
          <th>Canal Digital</th>
          <th class="num-cell">Realizado MTD</th>
          <th class="num-cell">Meta MTD</th>
          <th class="num-cell">Ating. %</th>
          <th class="num-cell">Desvio R$ (GAP)</th>
          <th class="num-cell">Desvio %</th>
          <th class="num-cell">Ago/26 MTD</th>
          <th class="num-cell">Cresc. MoM %</th>
          <th class="num-cell">Set/25 MTD</th>
          <th class="num-cell">Evol. YoY %</th>
          <th class="num-cell">Share %</th>
          <th class="num-cell">Projeção Mês</th>
          <th class="num-cell">Meta Mensal</th>
        </tr>
      `;

      const canais = getFilteredCanaisData();
      const isFiltered = !!(selectedGrupo || selectedSubgrupo || selectedLab || searchText);

      if (!canais || canais.length === 0 || (isFiltered && canais[0].venda_mtd === 0 && canais[0].meta_mtd === 0)) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="13" style="text-align: center; padding: 36px 16px; color: var(--text-tertiary);">
              <div style="font-size: 24px; margin-bottom: 6px;">🔍</div>
              <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">Nenhum dado encontrado nos canais para os filtros ativos</div>
              <div style="font-size: 11.5px;">Tente alterar os filtros de grupo, fornecedor ou o termo de busca.</div>
              <button class="apple-btn-secondary" onclick="resetGlobalFilters()" style="margin: 12px auto 0; display: inline-flex;">✕ Limpar Filtros</button>
            </td>
          </tr>
        `;
        return;
      }}

      tbody.innerHTML = canais.map(c => `
        <tr style="${{c.id === activeChannel ? 'background: var(--surface-hover); font-weight: 600;' : ''}}">
          <td>
            <strong>${{c.icone || ''}} ${{c.nome}}</strong>
            ${{isFiltered ? '<span class="badge-trend trend-neutral" style="font-size: 10px; margin-left: 6px;">Filtrado</span>' : ''}}
          </td>
          <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(c.venda_mtd)}}</td>
          <td class="num-cell">${{fmtMoney(c.meta_mtd)}}</td>
          <td class="num-cell">
            <span class="badge-trend ${{c.ating_mtd_pct >= 100 ? 'trend-pos' : c.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
              ${{fmtPct(c.ating_mtd_pct)}}
            </span>
          </td>
          <td class="num-cell" style="font-weight: 700; color: ${{c.gap_mtd >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
            ${{(c.gap_mtd >= 0 ? '+' : '') + fmtMoney(c.gap_mtd)}}
          </td>
          <td class="num-cell" style="color: ${{c.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
            ${{fmtSignPct(c.desvio_pct)}}
          </td>
          <td class="num-cell">${{fmtMoney(c.v26_06_mtd)}}</td>
          <td class="num-cell">
            <span class="badge-trend ${{c.crescimento_mom_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
              ${{fmtSignPct(c.crescimento_mom_pct)}}
            </span>
          </td>
          <td class="num-cell">${{fmtMoney(c.v25_mtd)}}</td>
          <td class="num-cell">
            <span class="badge-trend ${{c.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
              ${{fmtSignPct(c.crescimento_yoy_pct)}}
            </span>
          </td>
          <td class="num-cell">${{fmtPct(c.share_realizado_pct)}}</td>
          <td class="num-cell" style="color: var(--apple-blue);">${{fmtMoney(c.projecao_fechamento)}}</td>
          <td class="num-cell" style="color: var(--text-tertiary);">${{fmtMoney(c.meta_mensal)}}</td>
        </tr>
      `).join('');
    }}

    /* ABA 2: Hierarquia (Grupo > Subgrupo > Linha) */
    function renderHierarquiaTable(thead, tbody) {{
      if (hierarquiaSubView === 'grupos') {{
        thead.innerHTML = `
          <tr>
            <th>Categoria / Grupo</th>
            <th class="num-cell">Realizado MTD</th>
            <th class="num-cell">Meta MTD</th>
            <th class="num-cell">Ating. %</th>
            <th class="num-cell">Desvio R$ (GAP)</th>
            <th class="num-cell">Desvio %</th>
            <th class="num-cell">Cresc. MoM %</th>
            <th class="num-cell">Evol. YoY %</th>
            <th class="num-cell">Share %</th>
            <th class="num-cell">Projeção Mês</th>
          </tr>
        `;

        let items = getFilteredGrupos();

        if (items.length === 0) {{
          tbody.innerHTML = `
            <tr>
              <td colspan="10" style="text-align: center; padding: 36px 16px; color: var(--text-tertiary);">
                <div style="font-size: 24px; margin-bottom: 6px;">🔍</div>
                <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">Nenhum grupo corresponde aos filtros ativos</div>
                <button class="apple-btn-secondary" onclick="resetGlobalFilters()" style="margin: 12px auto 0; display: inline-flex;">✕ Limpar Filtros</button>
              </td>
            </tr>
          `;
          return;
        }}

        tbody.innerHTML = items.map(g => {{
          const ch = g.canais[activeChannel] || g;
          const isPos = ch.gap_mtd >= 0;
          return `
            <tr>
              <td><strong>${{g.grupo}}</strong> <span style="font-size: 11px; color: var(--text-tertiary);">(${{g.total_linhas}} linhas)</span></td>
              <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(ch.realizado_mtd)}}</td>
              <td class="num-cell">${{fmtMoney(ch.meta_mtd)}}</td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.ating_mtd_pct >= 100 ? 'trend-pos' : ch.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                  ${{fmtPct(ch.ating_mtd_pct)}}
                </span>
              </td>
              <td class="num-cell" style="font-weight: 700; color: ${{isPos ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{(isPos ? '+' : '') + fmtMoney(ch.gap_mtd)}}
              </td>
              <td class="num-cell" style="color: ${{ch.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{fmtSignPct(ch.desvio_pct)}}
              </td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.crescimento_mom_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                  ${{fmtSignPct(ch.crescimento_mom_pct)}}
                </span>
              </td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                  ${{fmtSignPct(ch.crescimento_yoy_pct)}}
                </span>
              </td>
              <td class="num-cell">${{fmtPct(ch.share_pct)}}</td>
              <td class="num-cell" style="color: var(--apple-blue);">${{fmtMoney(ch.projecao_fechamento)}}</td>
            </tr>
          `;
        }}).join('');

      }} else if (hierarquiaSubView === 'subgrupos') {{
        thead.innerHTML = `
          <tr>
            <th>Subgrupo de Categoria</th>
            <th>Grupo</th>
            <th class="num-cell">Realizado MTD</th>
            <th class="num-cell">Meta MTD</th>
            <th class="num-cell">Ating. %</th>
            <th class="num-cell">Desvio R$ (GAP)</th>
            <th class="num-cell">Desvio %</th>
            <th class="num-cell">Cresc. MoM %</th>
            <th class="num-cell">Evol. YoY %</th>
            <th class="num-cell">Projeção Mês</th>
          </tr>
        `;

        let items = getFilteredSubgrupos();

        if (items.length === 0) {{
          tbody.innerHTML = `
            <tr>
              <td colspan="10" style="text-align: center; padding: 36px 16px; color: var(--text-tertiary);">
                <div style="font-size: 24px; margin-bottom: 6px;">🔍</div>
                <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">Nenhum subgrupo corresponde aos filtros ativos</div>
                <button class="apple-btn-secondary" onclick="resetGlobalFilters()" style="margin: 12px auto 0; display: inline-flex;">✕ Limpar Filtros</button>
              </td>
            </tr>
          `;
          return;
        }}

        tbody.innerHTML = items.map(s => {{
          const ch = s.canais[activeChannel] || s;
          const isPos = ch.gap_mtd >= 0;
          return `
            <tr onclick="selectSubgrupoDirect('${{s.subgrupo.replace(/'/g, "\\'")}}', '${{s.grupo.replace(/'/g, "\\'")}}')" style="cursor: pointer;" title="Clique para filtrar pelo subgrupo ${{s.subgrupo}}">
              <td><strong>${{s.subgrupo}}</strong></td>
              <td style="color: var(--text-secondary); font-size: 12px;">${{s.grupo}}</td>
              <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(ch.realizado_mtd)}}</td>
              <td class="num-cell">${{fmtMoney(ch.meta_mtd)}}</td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.ating_mtd_pct >= 100 ? 'trend-pos' : ch.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                  ${{fmtPct(ch.ating_mtd_pct)}}
                </span>
              </td>
              <td class="num-cell" style="font-weight: 700; color: ${{isPos ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{(isPos ? '+' : '') + fmtMoney(ch.gap_mtd)}}
              </td>
              <td class="num-cell" style="color: ${{ch.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{fmtSignPct(ch.desvio_pct)}}
              </td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.crescimento_mom_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                  ${{fmtSignPct(ch.crescimento_mom_pct)}}
                </span>
              </td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                  ${{fmtSignPct(ch.crescimento_yoy_pct)}}
                </span>
              </td>
              <td class="num-cell" style="color: var(--apple-blue);">${{fmtMoney(ch.projecao_fechamento)}}</td>
            </tr>
          `;
        }}).join('');

      }} else {{
        // Linhas (Padrão)
        thead.innerHTML = `
          <tr>
            <th>Linha de Produto</th>
            <th>Subgrupo</th>
            <th>Grupo</th>
            <th class="num-cell">Realizado MTD</th>
            <th class="num-cell">Meta MTD</th>
            <th class="num-cell">Ating. %</th>
            <th class="num-cell">Desvio R$ (GAP)</th>
            <th class="num-cell">Desvio %</th>
            <th class="num-cell">Cresc. MoM %</th>
            <th class="num-cell">Evol. YoY %</th>
            <th class="num-cell">Projeção Mês</th>
          </tr>
        `;

        let items = getFilteredLinhas();

        if (items.length === 0) {{
          tbody.innerHTML = `
            <tr>
              <td colspan="11" style="text-align: center; padding: 36px 16px; color: var(--text-tertiary);">
                <div style="font-size: 24px; margin-bottom: 6px;">🔍</div>
                <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">Nenhuma linha de produto encontrada para os filtros ativos</div>
                <div style="font-size: 11.5px;">Tente alterar o fornecedor, o subgrupo ou o termo de busca.</div>
                <button class="apple-btn-secondary" onclick="resetGlobalFilters()" style="margin: 12px auto 0; display: inline-flex;">✕ Limpar Filtros</button>
              </td>
            </tr>
          `;
          return;
        }}

        tbody.innerHTML = items.slice(0, 150).map(l => {{
          const ch = l.canais[activeChannel] || l;
          const isPos = ch.gap_mtd >= 0;
          return `
            <tr onclick="filterByLinhaDirect('${{l.linha.replace(/'/g, "\\'")}}')" style="cursor: pointer;" title="Clique para buscar a linha ${{l.linha}}">
              <td><strong>${{l.linha}}</strong></td>
              <td style="color: var(--text-secondary); font-size: 11.5px;">${{l.subgrupo}}</td>
              <td style="color: var(--text-tertiary); font-size: 11px;">${{l.grupo}}</td>
              <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(ch.realizado_mtd)}}</td>
              <td class="num-cell">${{fmtMoney(ch.meta_mtd)}}</td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.ating_mtd_pct >= 100 ? 'trend-pos' : ch.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                  ${{fmtPct(ch.ating_mtd_pct)}}
                </span>
              </td>
              <td class="num-cell" style="font-weight: 700; color: ${{isPos ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{(isPos ? '+' : '') + fmtMoney(ch.gap_mtd)}}
              </td>
              <td class="num-cell" style="color: ${{ch.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{fmtSignPct(ch.desvio_pct)}}
              </td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.crescimento_mom_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                  ${{fmtSignPct(ch.crescimento_mom_pct)}}
                </span>
              </td>
              <td class="num-cell">
                <span class="badge-trend ${{ch.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                  ${{fmtSignPct(ch.crescimento_yoy_pct)}}
                </span>
              </td>
              <td class="num-cell" style="color: var(--apple-blue);">${{fmtMoney(ch.projecao_fechamento)}}</td>
            </tr>
          `;
        }}).join('');
      }}
    }}

    /* ABA 3: Fornecedores / Laboratórios */
    function renderLaboratoriosTable(thead, tbody) {{
      thead.innerHTML = `
        <tr>
          <th>Laboratório / Fornecedor</th>
          <th class="num-cell">Realizado MTD</th>
          <th class="num-cell">Meta MTD</th>
          <th class="num-cell">Ating. %</th>
          <th class="num-cell">Desvio R$ (GAP)</th>
          <th class="num-cell">Desvio %</th>
          <th class="num-cell">Cresc. MoM %</th>
          <th class="num-cell">Evol. YoY %</th>
          <th class="num-cell">Share %</th>
          <th class="num-cell">Projeção Mês</th>
          <th class="num-cell">Meta Mensal</th>
        </tr>
      `;

      let items = getFilteredLaboratorios();

      if (items.length === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="11" style="text-align: center; padding: 36px 16px; color: var(--text-tertiary);">
              <div style="font-size: 24px; margin-bottom: 6px;">🔍</div>
              <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">Nenhum fornecedor encontrado para os filtros ativos</div>
              <div style="font-size: 11.5px;">Tente selecionar outro Grupo/Subgrupo ou limpar a busca.</div>
              <button class="apple-btn-secondary" onclick="resetGlobalFilters()" style="margin: 12px auto 0; display: inline-flex;">✕ Limpar Filtros</button>
            </td>
          </tr>
        `;
        return;
      }}

      tbody.innerHTML = items.slice(0, 150).map(l => {{
        const ch = l.canais[activeChannel] || l;
        const isPos = ch.gap_mtd >= 0;
        return `
          <tr onclick="selectLabDirect('${{l.laboratorio.replace(/'/g, "\\'")}}')" style="cursor: pointer;" title="Clique para filtrar pelo fornecedor ${{l.laboratorio}}">
            <td><strong>${{l.laboratorio}}</strong></td>
            <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(ch.realizado_mtd)}}</td>
            <td class="num-cell">${{fmtMoney(ch.meta_mtd)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{ch.ating_mtd_pct >= 100 ? 'trend-pos' : ch.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                ${{fmtPct(ch.ating_mtd_pct)}}
              </span>
            </td>
            <td class="num-cell" style="font-weight: 700; color: ${{isPos ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
              ${{(isPos ? '+' : '') + fmtMoney(ch.gap_mtd)}}
            </td>
            <td class="num-cell" style="color: ${{ch.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
              ${{fmtSignPct(ch.desvio_pct)}}
            </td>
            <td class="num-cell">
              <span class="badge-trend ${{ch.crescimento_mom_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                ${{fmtSignPct(ch.crescimento_mom_pct)}}
              </span>
            </td>
            <td class="num-cell">
              <span class="badge-trend ${{ch.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                ${{fmtSignPct(ch.crescimento_yoy_pct)}}
              </span>
            </td>
            <td class="num-cell">${{fmtPct(ch.share_pct)}}</td>
            <td class="num-cell" style="color: var(--apple-blue);">${{fmtMoney(ch.projecao_fechamento)}}</td>
            <td class="num-cell" style="color: var(--text-tertiary);">${{fmtMoney(ch.meta_mensal)}}</td>
          </tr>
        `;
      }}).join('');
    }}

    /* ABA 4: Raio-X de Problemas / Diagnóstico Executivo */
    function renderDiagnosticoView() {{
      const diagObj = window.DASHBOARD_DATA.diagnostico_causas || {{}};
      const defaultDiag = diagObj[activeChannel] || diagObj.total || {{}};

      const channelNames = {{
        'total': 'Total Digital',
        'app': 'App São João',
        'site': 'Site Oficial',
        'marketplace': 'Marketplaces'
      }};

      const isFiltered = !!(selectedGrupo || selectedSubgrupo || selectedLab || searchText);
      document.getElementById('diagSummaryTitle').textContent = `Raio-X de Causa-Raiz — ${{channelNames[activeChannel]}} (D-1)${{isFiltered ? ' [Escopo Filtrado]' : ''}}`;

      const renderDiagList = (items, isPositive) => {{
        if (!items || items.length === 0) return '<div style="font-size: 11.5px; color: var(--text-tertiary); padding: 8px;">Nenhum item relevante para o escopo</div>';
        return items.slice(0, 6).map(item => `
          <div class="highlight-item" onclick="filterByLinhaDirect('${{item.nome.replace(/'/g, "\\'")}}')" style="cursor: pointer;" title="Clique para filtrar por ${{item.nome}}">
            <div class="highlight-info">
              <span class="highlight-name" title="${{item.nome}}">${{item.nome}}</span>
              <span class="highlight-cat">${{item.grupo ? item.grupo + ' • ' : ''}}Ating: ${{fmtPct(item.ating_mtd_pct)}} | MoM: ${{fmtSignPct(item.crescimento_mom_pct)}}</span>
            </div>
            <div class="highlight-metric">
              <div class="highlight-gap" style="color: ${{isPositive ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
                ${{(item.gap_mtd >= 0 ? '+' : '') + fmtMoney(item.gap_mtd)}}
              </div>
              <div style="font-size: 10.5px; color: var(--text-tertiary);">Desvio: ${{fmtSignPct(item.desvio_pct)}}</div>
            </div>
          </div>
        `).join('');
      }};

      if (!isFiltered) {{
        document.getElementById('diagListDetratoresLabs').innerHTML = renderDiagList(defaultDiag.detratores_laboratorios, false);
        document.getElementById('diagListAceleradoresLabs').innerHTML = renderDiagList(defaultDiag.aceleradores_laboratorios, true);
        document.getElementById('diagListDetratoresSubgrupos').innerHTML = renderDiagList(defaultDiag.detratores_subgrupos, false);
        document.getElementById('diagListAceleradoresSubgrupos').innerHTML = renderDiagList(defaultDiag.aceleradores_subgrupos, true);
        document.getElementById('diagListDetratoresLinhas').innerHTML = renderDiagList(defaultDiag.detratores_linhas, false);
        document.getElementById('diagListAceleradoresLinhas').innerHTML = renderDiagList(defaultDiag.aceleradores_linhas, true);
        return;
      }}

      // Escopo filtrado: computar dinamicamente
      const fLabs = getFilteredLaboratorios();
      const fSubs = getFilteredSubgrupos();
      const fLins = getFilteredLinhas();

      const extractMetrics = (items, nameProp) => {{
        return items.map(it => {{
          const ch = (it.canais && it.canais[activeChannel]) ? it.canais[activeChannel] : it;
          return {{
            nome: it[nameProp],
            grupo: it.grupo || (it.grupos ? it.grupos[0] : ''),
            gap_mtd: ch.gap_mtd || 0,
            desvio_pct: ch.desvio_pct || 0,
            ating_mtd_pct: ch.ating_mtd_pct || 0,
            crescimento_mom_pct: ch.crescimento_mom_pct || 0
          }};
        }});
      }};

      const labsM = extractMetrics(fLabs, 'laboratorio');
      const subsM = extractMetrics(fSubs, 'subgrupo');
      const linsM = extractMetrics(fLins, 'linha');

      document.getElementById('diagListDetratoresLabs').innerHTML = renderDiagList(labsM.filter(x => x.gap_mtd < 0).sort((a,b) => a.gap_mtd - b.gap_mtd), false);
      document.getElementById('diagListAceleradoresLabs').innerHTML = renderDiagList(labsM.filter(x => x.gap_mtd > 0).sort((a,b) => b.gap_mtd - a.gap_mtd), true);

      document.getElementById('diagListDetratoresSubgrupos').innerHTML = renderDiagList(subsM.filter(x => x.gap_mtd < 0).sort((a,b) => a.gap_mtd - b.gap_mtd), false);
      document.getElementById('diagListAceleradoresSubgrupos').innerHTML = renderDiagList(subsM.filter(x => x.gap_mtd > 0).sort((a,b) => b.gap_mtd - a.gap_mtd), true);

      document.getElementById('diagListDetratoresLinhas').innerHTML = renderDiagList(linsM.filter(x => x.gap_mtd < 0).sort((a,b) => a.gap_mtd - b.gap_mtd), false);
      document.getElementById('diagListAceleradoresLinhas').innerHTML = renderDiagList(linsM.filter(x => x.gap_mtd > 0).sort((a,b) => b.gap_mtd - a.gap_mtd), true);
    }}

    /* ABA 5: Top SKUs */
    function renderSkusTable(thead, tbody) {{
      thead.innerHTML = `
        <tr>
          <th>ID</th>
          <th>Descrição do SKU</th>
          <th>Laboratório</th>
          <th>Linha</th>
          <th class="num-cell">Meta MTD Total</th>
          <th class="num-cell">Meta MTD App</th>
          <th class="num-cell">Meta MTD Site</th>
          <th class="num-cell">Meta MTD Mkt</th>
          <th class="num-cell">Meta Mensal</th>
        </tr>
      `;

      let items = getFilteredSkus();

      if (items.length === 0) {{
        tbody.innerHTML = `
          <tr>
            <td colspan="9" style="text-align: center; padding: 36px 16px; color: var(--text-tertiary);">
              <div style="font-size: 24px; margin-bottom: 6px;">🔍</div>
              <div style="font-weight: 600; color: var(--text-secondary); margin-bottom: 4px;">Nenhum SKU encontrado para os filtros ativos</div>
              <div style="font-size: 11.5px;">Tente ajustar os critérios ou pesquisar por código ID, nome ou fornecedor.</div>
              <button class="apple-btn-secondary" onclick="resetGlobalFilters()" style="margin: 12px auto 0; display: inline-flex;">✕ Limpar Filtros</button>
            </td>
          </tr>
        `;
        return;
      }}

      tbody.innerHTML = items.slice(0, 150).map(s => `
        <tr>
          <td style="font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', monospace; font-size: 11.5px; font-weight: 600; color: var(--apple-blue);">${{s.id}}</td>
          <td><strong>${{s.nome}}</strong></td>
          <td style="color: var(--text-secondary); font-size: 12px;">${{s.laboratorio}}</td>
          <td style="color: var(--text-tertiary); font-size: 11.5px;">${{s.linha}}</td>
          <td class="num-cell" style="font-weight: 700; color: var(--apple-green-text);">${{fmtMoney(s.meta_mtd)}}</td>
          <td class="num-cell" style="${{activeChannel === 'app' ? 'font-weight: 700; color: var(--apple-indigo);' : ''}}">${{fmtMoney(s.meta_mtd_app)}}</td>
          <td class="num-cell" style="${{activeChannel === 'site' ? 'font-weight: 700; color: var(--apple-purple);' : ''}}">${{fmtMoney(s.meta_mtd_site)}}</td>
          <td class="num-cell" style="${{activeChannel === 'marketplace' ? 'font-weight: 700; color: var(--apple-orange);' : ''}}">${{fmtMoney(s.meta_mtd_mkt)}}</td>
          <td class="num-cell" style="color: var(--text-secondary);">${{fmtMoney(s.meta_mensal)}}</td>
        </tr>
      `).join('');
    }}

    function exportToCSV() {{
      let csv = '';
      const dateStr = new Date().toISOString().slice(0,10);

      if (activeTableTab === 'canais') {{
        csv = 'Canal;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;Ago26_MTD;MoM_Pct;Set25_MTD;YoY_Pct;Share_Pct;Projecao_Mes;Meta_Mensal\\n';
        getFilteredCanaisData().forEach(c => {{
          csv += `"${{c.nome}}";${{c.venda_mtd}};${{c.meta_mtd}};${{c.ating_mtd_pct}};${{c.gap_mtd}};${{c.desvio_pct}};${{c.v26_06_mtd}};${{c.crescimento_mom_pct}};${{c.v25_mtd}};${{c.crescimento_yoy_pct}};${{c.share_realizado_pct}};${{c.projecao_fechamento}};${{c.meta_mensal}}\\n`;
        }});
      }} else if (activeTableTab === 'hierarquia') {{
        if (hierarquiaSubView === 'grupos') {{
          csv = 'Grupo;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Share_Pct;Projecao_Mes\\n';
          getFilteredGrupos().forEach(g => {{
            const ch = g.canais[activeChannel] || g;
            csv += `"${{g.grupo}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.share_pct}};${{ch.projecao_fechamento}}\\n`;
          }});
        }} else if (hierarquiaSubView === 'subgrupos') {{
          csv = 'Subgrupo;Grupo;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Projecao_Mes\\n';
          getFilteredSubgrupos().forEach(s => {{
            const ch = s.canais[activeChannel] || s;
            csv += `"${{s.subgrupo}}";"${{s.grupo}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.projecao_fechamento}}\\n`;
          }});
        }} else {{
          csv = 'Linha;Subgrupo;Grupo;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Projecao_Mes\\n';
          getFilteredLinhas().forEach(l => {{
            const ch = l.canais[activeChannel] || l;
            csv += `"${{l.linha}}";"${{l.subgrupo}}";"${{l.grupo}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.projecao_fechamento}}\\n`;
          }});
        }}
      }} else if (activeTableTab === 'laboratorios') {{
        csv = 'Laboratorio;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Share_Pct;Projecao_Mes\\n';
        getFilteredLaboratorios().forEach(l => {{
          const ch = l.canais[activeChannel] || l;
          csv += `"${{l.laboratorio}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.share_pct}};${{ch.projecao_fechamento}}\\n`;
        }});
      }} else if (activeTableTab === 'skus') {{
        csv = 'ID;Descricao;Laboratorio;Linha;Meta_MTD;Meta_App;Meta_Site;Meta_Mkt;Meta_Mensal\\n';
        getFilteredSkus().forEach(s => {{
          csv += `${{s.id}};"${{s.nome}}";"${{s.laboratorio}}";"${{s.linha}}";${{s.meta_mtd}};${{s.meta_mtd_app}};${{s.meta_mtd_site}};${{s.meta_mtd_mkt}};${{s.meta_mensal}}\\n`;
        }});
      }}

      const blob = new Blob(["\\uFEFF" + csv], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `Acompanhamento_Digital_${{activeTableTab}}_${{activeChannel}}_${{dateStr}}.csv`;
      link.click();
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Dashboard Executivo (Apple Design com Diagnóstico Macro-to-Micro) compilado em: {OUTPUT_HTML}")
    print(f"   Tamanho final do HTML: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")
    print(f"🎉 Compilação concluída em {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    build()
