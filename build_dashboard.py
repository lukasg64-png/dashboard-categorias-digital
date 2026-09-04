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
      gap: 6px;
      font-size: 11px;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
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
          <span id="headerCutDate">D-1: 01 a 03/09/2026</span>
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
            <span class="channel-badge trend-neutral" id="badgeAtingTotal">94.9%</span>
          </div>
          <div class="channel-sales" id="tabSalesTotal">R$ 5.897.259</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaTotal">R$ 6.213.585</strong></span>
            <span id="tabGapTotal" class="badge-trend trend-neg">-R$ 316.326</span>
          </div>
          <div class="channel-deltas-line">
            <span>Desvio: <strong id="tabDesvioPctTotal" style="color: var(--apple-red-text);">-5.1%</strong></span>
            <span>MoM: <strong id="tabMomTotal" style="color: var(--apple-green-text);">+17.1%</strong></span>
            <span>YoY: <strong id="tabYoyTotal" style="color: var(--apple-green-text);">+43.2%</strong></span>
          </div>
        </div>

        <!-- 2. App -->
        <div class="channel-tab tab-app" onclick="switchChannel('app')">
          <div class="channel-tab-header">
            <span class="channel-name">📱 App</span>
            <span class="channel-badge trend-pos" id="badgeAtingApp">109.2% 🚀</span>
          </div>
          <div class="channel-sales" id="tabSalesApp">R$ 3.215.637</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaApp">R$ 2.944.468</strong></span>
            <span id="tabGapApp" class="badge-trend trend-pos">+R$ 271.169</span>
          </div>
          <div class="channel-deltas-line">
            <span>Desvio: <strong id="tabDesvioPctApp" style="color: var(--apple-green-text);">+9.2%</strong></span>
            <span>MoM: <strong id="tabMomApp" style="color: var(--apple-green-text);">+38.5%</strong></span>
            <span>YoY: <strong id="tabYoyApp" style="color: var(--apple-green-text);">+53.4%</strong></span>
          </div>
        </div>

        <!-- 3. Marketplace -->
        <div class="channel-tab tab-marketplace" onclick="switchChannel('marketplace')">
          <div class="channel-tab-header">
            <span class="channel-name">🛍️ Marketplace</span>
            <span class="channel-badge trend-pos" id="badgeAtingMkt">100.9%</span>
          </div>
          <div class="channel-sales" id="tabSalesMkt">R$ 1.638.913</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaMkt">R$ 1.624.060</strong></span>
            <span id="tabGapMkt" class="badge-trend trend-pos">+R$ 14.852</span>
          </div>
          <div class="channel-deltas-line">
            <span>Desvio: <strong id="tabDesvioPctMkt" style="color: var(--apple-green-text);">+0.9%</strong></span>
            <span>MoM: <strong id="tabMomMkt" style="color: var(--apple-red-text);">-13.3%</strong></span>
            <span>YoY: <strong id="tabYoyMkt" style="color: var(--apple-green-text);">+115.5%</strong></span>
          </div>
        </div>

        <!-- 4. Site -->
        <div class="channel-tab tab-site" onclick="switchChannel('site')">
          <div class="channel-tab-header">
            <span class="channel-name">💻 Site</span>
            <span class="channel-badge trend-neg" id="badgeAtingSite">63.4% ⚠️</span>
          </div>
          <div class="channel-sales" id="tabSalesSite">R$ 1.042.709</div>
          <div class="channel-meta-sub">
            <span>Meta MTD: <strong id="tabMetaSite">R$ 1.645.057</strong></span>
            <span id="tabGapSite" class="badge-trend trend-neg">-R$ 602.348</span>
          </div>
          <div class="channel-deltas-line">
            <span>Desvio: <strong id="tabDesvioPctSite" style="color: var(--apple-red-text);">-36.6%</strong></span>
            <span>MoM: <strong id="tabMomSite" style="color: var(--apple-green-text);">+26.7%</strong></span>
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
          <select id="filterSubgrupo" class="apple-select" onchange="applyGlobalFilters()">
            <option value="">Todos os Subgrupos</option>
          </select>
        </div>

        <!-- 3. Fornecedor / Laboratório -->
        <div class="filter-control-group">
          <label for="filterLab">🏭 Fornecedor / Laboratório</label>
          <select id="filterLab" class="apple-select" onchange="applyGlobalFilters()">
            <option value="">Todos os Fornecedores</option>
          </select>
        </div>

        <!-- 4. Busca Textual -->
        <div class="filter-control-group">
          <label for="filterSearchText">🏷️ Busca SKU / Linha / Nome</label>
          <input type="text" id="filterSearchText" class="apple-input" placeholder="Ex: Mounjaro, Fralda, Lilly, Ozempic..." oninput="applyGlobalFilters()">
        </div>

        <!-- 5. Limpar -->
        <div>
          <button class="apple-btn-secondary" onclick="resetGlobalFilters()" title="Limpar filtros">
            ✕ Limpar Filtros
          </button>
        </div>
      </div>
    </section>

    <!-- Grid de 6 KPIs Dinâmicos (Vinculados ao Canal Selecionado) -->
    <section class="kpi-grid">
      <!-- 1. Realizado MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Venda Realizada MTD</span>
          <span>💰</span>
        </div>
        <div class="kpi-value" id="kpiVendaMtd" style="color: var(--apple-blue);">R$ 5.897.259</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiYoYBadge">↑ +43.2% YoY</span>
          <span id="kpiYoYDiff" style="color: var(--text-tertiary);">+R$ 1.78M</span>
        </div>
      </div>

      <!-- 2. Meta Diarizada MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Meta Diarizada MTD</span>
          <span>🎯</span>
        </div>
        <div class="kpi-value" id="kpiMetaMtd">R$ 6.213.585</div>
        <div class="kpi-subtext">
          <span>Curva Acum.: <strong id="kpiPctCurva" style="color: var(--text-primary);">11.35%</strong> (3/30 dias)</span>
        </div>
      </div>

      <!-- 3. Atingimento MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Atingimento da Meta</span>
          <span>📊</span>
        </div>
        <div class="kpi-value" id="kpiAtingMtd" style="color: var(--apple-orange);">94.9%</div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" id="kpiProgressBar" style="width: 94.9%; background: var(--apple-orange);"></div>
        </div>
      </div>

      <!-- 4. Desvio Meta (R$ e %) -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Desvio vs Meta (GAP)</span>
          <span>⚖️</span>
        </div>
        <div class="kpi-value" id="kpiGapMtd" style="color: var(--apple-red-text);">-R$ 316.326</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-neg" id="kpiDesvioPctBadge">-5.1% Desvio</span>
          <span id="kpiGapStatus">Déficit vs Curva</span>
        </div>
      </div>

      <!-- 5. Crescimento MoM (vs Ago/26) -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Crescimento MoM (vs Ago/26)</span>
          <span>📈</span>
        </div>
        <div class="kpi-value" id="kpiMoMValue" style="color: var(--apple-green);">+17.1%</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiMoMBadge">+R$ 861.5k</span>
          <span style="color: var(--text-tertiary);">vs 01 a 03/Ago</span>
        </div>
      </div>

      <!-- 6. Projeção de Fechamento -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Projeção de Fechamento</span>
          <span>🔮</span>
        </div>
        <div class="kpi-value" id="kpiProjecao">R$ 54.950.233</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiAtingProj">+R$ 205.0k</span>
          <span id="kpiMetaMensalRef" style="color: var(--text-tertiary);">Meta Mês: R$ 54.7M</span>
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
              🏢 Hierarquia (Grupo > Subgrupo > Linha)
            </button>
            <button class="segmented-btn" id="tabBtnLabs" onclick="switchTableTab('laboratorios')">
              🏭 Fornecedores / Labs
            </button>
            <button class="segmented-btn" id="tabBtnDiagnostico" onclick="switchTableTab('diagnostico')">
              ⚠️ Raio-X de Problemas
            </button>
            <button class="segmented-btn" id="tabBtnSkus" onclick="switchTableTab('skus')">
              🏷️ Top SKUs (Produtos)
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
    }}

    function populateFilterDropdowns() {{
      const filtros = window.DASHBOARD_DATA.filtros || {{}};
      const grupoSel = document.getElementById('filterGrupo');
      const subgrupoSel = document.getElementById('filterSubgrupo');
      const labSel = document.getElementById('filterLab');

      // 1. Grupos
      if (filtros.grupos) {{
        filtros.grupos.forEach(g => {{
          const opt = document.createElement('option');
          opt.value = g;
          opt.textContent = g;
          grupoSel.appendChild(opt);
        }});
      }}

      // 2. Labs
      if (filtros.laboratorios) {{
        filtros.laboratorios.forEach(l => {{
          const opt = document.createElement('option');
          opt.value = l;
          opt.textContent = l;
          labSel.appendChild(opt);
        }});
      }}

      updateSubgrupoDropdown();
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

      subs.forEach(s => {{
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        if (s === selectedSubgrupo) opt.selected = true;
        subgrupoSel.appendChild(opt);
      }});
    }}

    function onFilterGrupoChange() {{
      selectedGrupo = document.getElementById('filterGrupo').value;
      selectedSubgrupo = '';
      updateSubgrupoDropdown();
      applyGlobalFilters();
    }}

    function applyGlobalFilters() {{
      selectedGrupo = document.getElementById('filterGrupo').value;
      selectedSubgrupo = document.getElementById('filterSubgrupo').value;
      selectedLab = document.getElementById('filterLab').value;
      searchText = document.getElementById('filterSearchText').value.trim().toLowerCase();

      // Atualizar badge de filtros ativos
      const activeParts = [];
      if (selectedGrupo) activeParts.push(`Grupo: ${{selectedGrupo}}`);
      if (selectedSubgrupo) activeParts.push(`Subgrupo: ${{selectedSubgrupo}}`);
      if (selectedLab) activeParts.push(`Fornecedor: ${{selectedLab}}`);
      if (searchText) activeParts.push(`Busca: "${{searchText}}"`);

      const statusEl = document.getElementById('filterActiveStatus');
      if (activeParts.length > 0) {{
        statusEl.innerHTML = `<span style="color: var(--apple-blue); font-weight: 600;">Filtros Ativos:</span> ${{activeParts.join(' • ')}}`;
      }} else {{
        statusEl.textContent = 'Visualizando todos os registros';
      }}

      renderTable();
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

      updateSubgrupoDropdown();
      document.getElementById('filterActiveStatus').textContent = 'Visualizando todos os registros';
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
        desvioEl.textContent = fmtSignPct(obj.desvio_pct);
        desvioEl.style.color = obj.desvio_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';

        const momEl = document.getElementById(`tabMom${{id}}`);
        momEl.textContent = fmtSignPct(obj.crescimento_mom_pct);
        momEl.style.color = obj.crescimento_mom_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';

        const yoyEl = document.getElementById(`tabYoy${{id}}`);
        yoyEl.textContent = fmtSignPct(obj.crescimento_yoy_pct);
        yoyEl.style.color = obj.crescimento_yoy_pct >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';
      }};

      fillTab('Total', k.total);
      fillTab('App', k.app);
      fillTab('Site', k.site);
      fillTab('Mkt', k.marketplace);
    }}

    function updateKpis() {{
      const canais = window.DASHBOARD_DATA.kpis.canais;
      const c = canais[activeChannel] || canais.total;
      const pctCurva = window.DASHBOARD_DATA.kpis.pct_curva_acum;

      document.getElementById('kpiVendaMtd').textContent = fmtMoney(c.venda_mtd);
      document.getElementById('kpiMetaMtd').textContent = fmtMoney(c.meta_mtd);
      document.getElementById('kpiPctCurva').textContent = pctCurva + '%';

      // Atingimento
      const ating = c.ating_mtd_pct;
      const atingElem = document.getElementById('kpiAtingMtd');
      atingElem.textContent = fmtPct(ating);
      const barElem = document.getElementById('kpiProgressBar');
      barElem.style.width = Math.min(ating, 100) + '%';
      
      if (ating >= 100) {{
        atingElem.style.color = 'var(--apple-green)';
        barElem.style.background = 'var(--apple-green)';
      }} else if (ating >= 90) {{
        atingElem.style.color = 'var(--apple-orange)';
        barElem.style.background = 'var(--apple-orange)';
      }} else {{
        atingElem.style.color = 'var(--apple-red)';
        barElem.style.background = 'var(--apple-red)';
      }}

      // Desvio R$ e Desvio %
      const gapElem = document.getElementById('kpiGapMtd');
      gapElem.textContent = (c.gap_mtd >= 0 ? '+' : '') + fmtMoney(c.gap_mtd);
      gapElem.style.color = c.gap_mtd >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';
      
      const desvioBadge = document.getElementById('kpiDesvioPctBadge');
      desvioBadge.textContent = fmtSignPct(c.desvio_pct);
      desvioBadge.className = 'badge-trend ' + (c.desvio_pct >= 0 ? 'trend-pos' : 'trend-neg');
      document.getElementById('kpiGapStatus').textContent = c.gap_mtd >= 0 ? 'Superávit Meta' : 'Déficit Meta';

      // Projeção
      document.getElementById('kpiProjecao').textContent = fmtMoney(c.projecao_fechamento);
      const gapProj = (c.projecao_fechamento || 0) - (c.meta_mensal || 0);
      const atingProjElem = document.getElementById('kpiAtingProj');
      atingProjElem.textContent = (gapProj >= 0 ? '+' : '') + fmtMoney(gapProj) + ' vs Meta';
      atingProjElem.className = 'badge-trend ' + (gapProj >= 0 ? 'trend-pos' : 'trend-neg');
      document.getElementById('kpiMetaMensalRef').textContent = `Meta Mês: ${{fmtMoney(c.meta_mensal)}}`;

      // YoY
      const yoy = c.crescimento_yoy_pct || 0;
      const yoyBadge = document.getElementById('kpiYoYBadge');
      yoyBadge.textContent = (yoy >= 0 ? '↑ +' : '↓ ') + yoy.toFixed(1) + '% YoY';
      yoyBadge.className = 'badge-trend ' + (yoy >= 0 ? 'trend-pos' : 'trend-neg');
      document.getElementById('kpiYoYDiff').textContent = (c.crescimento_yoy_diff >= 0 ? '+' : '') + fmtMoney(c.crescimento_yoy_diff);

      // MoM
      const mom = c.crescimento_mom_pct || 0;
      const momElem = document.getElementById('kpiMoMValue');
      momElem.textContent = fmtSignPct(mom);
      momElem.style.color = mom >= 0 ? 'var(--apple-green)' : 'var(--apple-red)';
      const momBadge = document.getElementById('kpiMoMBadge');
      momBadge.textContent = (c.crescimento_mom_diff >= 0 ? '+' : '') + fmtMoney(c.crescimento_mom_diff);
      momBadge.className = 'badge-trend ' + (c.crescimento_mom_diff >= 0 ? 'trend-pos' : 'trend-neg');
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
      const titleElem = document.getElementById('chartTitleText');
      if (titleElem) {{
        titleElem.textContent = `📅 Curva Diária [${{channelLabel}}]: Realizado vs Meta Diária + Desvio % por Dia`;
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
      const diagObj = window.DASHBOARD_DATA.diagnostico_causas || window.DASHBOARD_DATA.destaques_por_canal || {{}};
      const destaques = diagObj[activeChannel] || window.DASHBOARD_DATA.destaques || {{}};

      const chLabel = activeChannel === 'total' ? 'Digital' : (activeChannel === 'app' ? 'App' : (activeChannel === 'site' ? 'Site' : 'Marketplace'));
      const tAcel = document.getElementById('titleAceleradores');
      const tDetr = document.getElementById('titleDetratores');
      if (tAcel) tAcel.textContent = `🚀 Top Linhas Superando a Meta (${{chLabel}})`;
      if (tDetr) tDetr.textContent = `⚠️ Top Linhas com Maior Oportunidade (${{chLabel}})`;
      
      const renderList = (items, isPositive) => {{
        if (!items || items.length === 0) {{
          return `<div style="padding: 18px; text-align: center; color: var(--text-tertiary); font-size: 12px;">Nenhum destaque para o filtro selecionado</div>`;
        }}
        const displayItems = items.slice(0, 8);
        return displayItems.map((item, idx) => `
          <div class="highlight-item">
            <div class="highlight-info">
              <span class="highlight-name" title="${{item.linha || item.nome}}">
                <span style="color: var(--text-tertiary); font-size: 11px; margin-right: 4px; font-weight: 600;">#${{idx + 1}}</span>${{item.linha || item.nome}}
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

      const acel = destaques.aceleradores_linhas || destaques.aceleradores || [];
      const detr = destaques.detratores_linhas || destaques.detratores || [];

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

      const canais = window.DASHBOARD_DATA.canais_tabela;
      tbody.innerHTML = canais.map(c => `
        <tr style="${{c.id === activeChannel ? 'background: var(--surface-hover); font-weight: 600;' : ''}}">
          <td><strong>${{c.icone || ''}} ${{c.nome}}</strong></td>
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

        let items = window.DASHBOARD_DATA.grupos;
        if (selectedGrupo) items = items.filter(g => g.grupo === selectedGrupo);
        if (searchText) items = items.filter(g => g.grupo.toLowerCase().includes(searchText));

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

        let items = window.DASHBOARD_DATA.subgrupos || [];
        if (selectedGrupo) items = items.filter(s => s.grupo === selectedGrupo);
        if (selectedSubgrupo) items = items.filter(s => s.subgrupo === selectedSubgrupo);
        if (searchText) items = items.filter(s => s.subgrupo.toLowerCase().includes(searchText) || s.grupo.toLowerCase().includes(searchText));

        tbody.innerHTML = items.map(s => {{
          const ch = s.canais[activeChannel] || s;
          const isPos = ch.gap_mtd >= 0;
          return `
            <tr>
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

        let items = window.DASHBOARD_DATA.linhas || [];
        if (selectedGrupo) items = items.filter(l => l.grupo === selectedGrupo);
        if (selectedSubgrupo) items = items.filter(l => l.subgrupo === selectedSubgrupo);
        if (searchText) items = items.filter(l => l.linha.toLowerCase().includes(searchText) || l.subgrupo.toLowerCase().includes(searchText) || l.grupo.toLowerCase().includes(searchText));

        tbody.innerHTML = items.slice(0, 150).map(l => {{
          const ch = l.canais[activeChannel] || l;
          const isPos = ch.gap_mtd >= 0;
          return `
            <tr>
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

      let items = window.DASHBOARD_DATA.laboratorios || [];
      if (selectedLab) items = items.filter(l => l.laboratorio === selectedLab);
      if (searchText) items = items.filter(l => l.laboratorio.toLowerCase().includes(searchText));

      tbody.innerHTML = items.slice(0, 150).map(l => {{
        const ch = l.canais[activeChannel] || l;
        const isPos = ch.gap_mtd >= 0;
        return `
          <tr>
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
      const diag = diagObj[activeChannel] || diagObj.total || {{}};

      const channelNames = {{
        'total': 'Total Digital',
        'app': 'App São João',
        'site': 'Site Oficial',
        'marketplace': 'Marketplaces'
      }};

      document.getElementById('diagSummaryTitle').textContent = `Raio-X de Causa-Raiz — ${{channelNames[activeChannel]}} (D-1)`;

      const renderDiagList = (items, isPositive) => {{
        if (!items || items.length === 0) return '<div style="font-size: 11.5px; color: var(--text-tertiary); padding: 8px;">Nenhum item relevante no canal</div>';
        return items.slice(0, 6).map(item => `
          <div class="highlight-item">
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

      document.getElementById('diagListDetratoresLabs').innerHTML = renderDiagList(diag.detratores_laboratorios, false);
      document.getElementById('diagListAceleradoresLabs').innerHTML = renderDiagList(diag.aceleradores_laboratorios, true);

      document.getElementById('diagListDetratoresSubgrupos').innerHTML = renderDiagList(diag.detratores_subgrupos, false);
      document.getElementById('diagListAceleradoresSubgrupos').innerHTML = renderDiagList(diag.aceleradores_subgrupos, true);

      document.getElementById('diagListDetratoresLinhas').innerHTML = renderDiagList(diag.detratores_linhas, false);
      document.getElementById('diagListAceleradoresLinhas').innerHTML = renderDiagList(diag.aceleradores_linhas, true);
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

      let items = window.DASHBOARD_DATA.top_skus || [];
      if (selectedGrupo) items = items.filter(s => s.grupo === selectedGrupo);
      if (selectedSubgrupo) items = items.filter(s => s.subgrupo === selectedSubgrupo);
      if (selectedLab) items = items.filter(s => s.laboratorio === selectedLab);
      if (searchText) {{
        items = items.filter(s => 
          String(s.id).includes(searchText) || 
          s.nome.toLowerCase().includes(searchText) ||
          s.laboratorio.toLowerCase().includes(searchText) ||
          s.linha.toLowerCase().includes(searchText)
        );
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
        window.DASHBOARD_DATA.canais_tabela.forEach(c => {{
          csv += `"${{c.nome}}";${{c.venda_mtd}};${{c.meta_mtd}};${{c.ating_mtd_pct}};${{c.gap_mtd}};${{c.desvio_pct}};${{c.v26_06_mtd}};${{c.crescimento_mom_pct}};${{c.v25_mtd}};${{c.crescimento_yoy_pct}};${{c.share_realizado_pct}};${{c.projecao_fechamento}};${{c.meta_mensal}}\\n`;
        }});
      }} else if (activeTableTab === 'hierarquia') {{
        if (hierarquiaSubView === 'grupos') {{
          csv = 'Grupo;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Share_Pct;Projecao_Mes\\n';
          window.DASHBOARD_DATA.grupos.forEach(g => {{
            const ch = g.canais[activeChannel] || g;
            csv += `"${{g.grupo}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.share_pct}};${{ch.projecao_fechamento}}\\n`;
          }});
        }} else if (hierarquiaSubView === 'subgrupos') {{
          csv = 'Subgrupo;Grupo;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Projecao_Mes\\n';
          window.DASHBOARD_DATA.subgrupos.forEach(s => {{
            const ch = s.canais[activeChannel] || s;
            csv += `"${{s.subgrupo}}";"${{s.grupo}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.projecao_fechamento}}\\n`;
          }});
        }} else {{
          csv = 'Linha;Subgrupo;Grupo;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Projecao_Mes\\n';
          window.DASHBOARD_DATA.linhas.forEach(l => {{
            const ch = l.canais[activeChannel] || l;
            csv += `"${{l.linha}}";"${{l.subgrupo}}";"${{l.grupo}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.projecao_fechamento}}\\n`;
          }});
        }}
      }} else if (activeTableTab === 'laboratorios') {{
        csv = 'Laboratorio;Realizado_MTD;Meta_MTD;Ating_Pct;Desvio_RS;Desvio_Pct;MoM_Pct;YoY_Pct;Share_Pct;Projecao_Mes\\n';
        window.DASHBOARD_DATA.laboratorios.forEach(l => {{
          const ch = l.canais[activeChannel] || l;
          csv += `"${{l.laboratorio}}";${{ch.realizado_mtd}};${{ch.meta_mtd}};${{ch.ating_mtd_pct}};${{ch.gap_mtd}};${{ch.desvio_pct}};${{ch.crescimento_mom_pct}};${{ch.crescimento_yoy_pct}};${{ch.share_pct}};${{ch.projecao_fechamento}}\\n`;
        }});
      }} else if (activeTableTab === 'skus') {{
        csv = 'ID;Descricao;Laboratorio;Linha;Meta_MTD;Meta_App;Meta_Site;Meta_Mkt;Meta_Mensal\\n';
        window.DASHBOARD_DATA.top_skus.forEach(s => {{
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
