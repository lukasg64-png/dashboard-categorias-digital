"""
build_dashboard.py — Compila o Dashboard Executivo Moderno (HTML5 + CSS Apple Design System + JS Interativo)
para o projeto Acompanhamento Categorias Digital (Site, App e Marketplace).
Baseado no Design System oficial das Farmácias São João (macOS / iOS Apple Human Interface Guidelines):
- Cores: Parchment (#F5F5F7), Surface (#FFFFFF), Ink (#1D1D1F), Action Blue (#0071E3), Apple Green (#34C759), Apple Red (#FF3B30), Apple Orange (#FF9500)
- Fontes: SF Pro Display / SF Pro Text / Outfit / Inter com tracking negativo e tabular-nums
- Componentes: Segmented Controls, Pill Badges, Glassmorphism Frosted Nav, Cards arredondados (18px) e tema claro/escuro.
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
    print("  COMPILAÇÃO DO DASHBOARD EXECUTIVO: APPLE DESIGN SYSTEM")
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
  
  <!-- Apple Typography (Outfit & Inter / SF Pro Stack) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <style>
    /* ==========================================================================
       FARMÁCIAS SÃO JOÃO — APPLE DESIGN SYSTEM (macOS / iOS HIG)
       ========================================================================== */
    
    :root {{
      /* Apple Light Palette (Default) */
      --bg-canvas: #F5F5F7;
      --surface: #FFFFFF;
      --surface-translucent: rgba(255, 255, 255, 0.85);
      --surface-hover: #F8F8FA;
      --surface-sunken: #EBEBED;
      --surface-subtle: #FAFAFC;

      /* Apple Borders & Hairlines */
      --border: rgba(0, 0, 0, 0.08);
      --border-subtle: rgba(0, 0, 0, 0.04);
      --border-hover: rgba(0, 0, 0, 0.16);
      --separator: rgba(60, 60, 67, 0.12);

      /* Apple Typography Colors */
      --text-primary: #1D1D1F;
      --text-secondary: #6E6E73;
      --text-tertiary: #86868B;
      --text-quaternary: #A1A1A6;

      /* Apple Vibrant Accents */
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

      --apple-teal: #30B0C7;
      --apple-teal-soft: rgba(48, 176, 199, 0.12);

      /* Radii & Elevation */
      --radius-xs: 6px;
      --radius-sm: 10px;
      --radius-md: 14px;
      --radius-lg: 18px;
      --radius-xl: 24px;
      --radius-pill: 9999px;

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
      --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03);
      --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.07), 0 2px 6px rgba(0, 0, 0, 0.03);
      --shadow-float: 0 20px 48px rgba(0, 0, 0, 0.09), 0 4px 12px rgba(0, 0, 0, 0.04);

      --chart-grid: rgba(0, 0, 0, 0.05);
      --chart-tooltip-bg: rgba(29, 29, 31, 0.92);
      --chart-tooltip-text: #FFFFFF;
    }}

    /* Apple Dark Mode Variables */
    [data-theme="dark"] {{
      --bg-canvas: #000000;
      --surface: #1C1C1E;
      --surface-translucent: rgba(28, 28, 30, 0.85);
      --surface-hover: #2C2C2E;
      --surface-sunken: #141416;
      --surface-subtle: #242426;

      --border: rgba(255, 255, 255, 0.10);
      --border-subtle: rgba(255, 255, 255, 0.05);
      --border-hover: rgba(255, 255, 255, 0.20);
      --separator: rgba(255, 255, 255, 0.12);

      --text-primary: #FFFFFF;
      --text-secondary: #A1A1A6;
      --text-tertiary: #8E8E93;
      --text-quaternary: #636366;

      --apple-blue: #2997FF;
      --apple-blue-hover: #47A3FF;
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

      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.5);

      --chart-grid: rgba(255, 255, 255, 0.06);
      --chart-tooltip-bg: rgba(44, 44, 46, 0.95);
      --chart-tooltip-text: #FFFFFF;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", sans-serif;
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.45;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
      transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* Layout */
    .app-container {{
      max-width: 1720px;
      margin: 0 auto;
      padding: 24px 32px 64px 32px;
    }}

    /* Apple Frosted Navigation Bar */
    header.header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      background: var(--surface-translucent);
      backdrop-filter: blur(24px) saturate(180%);
      -webkit-backdrop-filter: blur(24px) saturate(180%);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
      position: sticky;
      top: 16px;
      z-index: 1000;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .logo-badge {{
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(145deg, #0071E3, #004bb5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Outfit', -apple-system, sans-serif;
      font-weight: 800;
      font-size: 19px;
      letter-spacing: -0.5px;
      color: white;
      box-shadow: 0 6px 16px rgba(0, 113, 227, 0.35);
    }}

    .brand-text h1 {{
      font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.4px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text-primary);
    }}

    .brand-text h1 .pill {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      background: var(--apple-blue-soft);
      color: var(--apple-blue);
      border: 1px solid var(--apple-blue-border);
      letter-spacing: 0;
    }}

    .brand-text p {{
      font-size: 12.5px;
      color: var(--text-secondary);
      margin-top: 2px;
      font-weight: 400;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .badge-status {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      background: var(--apple-green-soft);
      border: 1px solid var(--apple-green-border);
      font-size: 12px;
      font-weight: 600;
      color: var(--apple-green-text);
      font-variant-numeric: tabular-nums;
    }}

    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--apple-green);
      box-shadow: 0 0 8px var(--apple-green);
      animation: applePulse 2s infinite;
    }}

    @keyframes applePulse {{
      0% {{ transform: scale(0.95); opacity: 0.8; }}
      50% {{ transform: scale(1.15); opacity: 1; }}
      100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}

    /* Apple Buttons */
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: var(--radius-pill);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text-primary);
      box-shadow: var(--shadow-sm);
    }}

    .btn:hover {{
      background: var(--surface-hover);
      border-color: var(--border-hover);
      transform: translateY(-1px);
    }}

    .btn:active {{
      transform: scale(0.97);
    }}

    .btn-primary {{
      background: var(--apple-blue);
      border: 1px solid transparent;
      color: #FFFFFF;
      box-shadow: 0 4px 12px rgba(0, 113, 227, 0.28);
    }}

    .btn-primary:hover {{
      background: var(--apple-blue-hover);
      box-shadow: 0 6px 18px rgba(0, 113, 227, 0.38);
      color: #FFFFFF;
    }}

    .btn-theme-toggle {{
      width: 36px;
      height: 36px;
      padding: 0;
      border-radius: var(--radius-pill);
      display: grid;
      place-items: center;
      font-size: 16px;
    }}

    /* Channel Selector Tabs (Apple Segmented Cards) */
    .channel-nav {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }}

    .channel-tab {{
      display: flex;
      flex-direction: column;
      padding: 18px 22px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-sm);
    }}

    .channel-tab:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: var(--border-hover);
    }}

    .channel-tab.active {{
      background: var(--surface);
      border-color: var(--active-accent, var(--apple-blue));
      box-shadow: 0 8px 24px rgba(0, 113, 227, 0.12), var(--shadow-md);
    }}

    .channel-tab.active::after {{
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--active-accent, var(--apple-blue));
      border-radius: 3px 3px 0 0;
    }}

    .tab-total {{ --active-accent: var(--apple-blue); }}
    .tab-app {{ --active-accent: var(--apple-indigo); }}
    .tab-site {{ --active-accent: var(--apple-purple); }}
    .tab-mkt {{ --active-accent: var(--apple-orange); }}

    .channel-tab-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .channel-name {{
      font-family: 'Outfit', -apple-system, sans-serif;
      font-size: 15px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-primary);
      letter-spacing: -0.2px;
    }}

    .channel-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: var(--radius-pill);
      font-variant-numeric: tabular-nums;
    }}

    .channel-sales {{
      font-size: 24px;
      font-weight: 800;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      letter-spacing: -0.8px;
      margin-bottom: 6px;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
      line-height: 1.15;
    }}

    .channel-meta-sub {{
      font-size: 12px;
      color: var(--text-secondary);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-variant-numeric: tabular-nums;
    }}

    .channel-sub-details {{
      font-size: 10.5px;
      color: var(--text-tertiary);
      margin-top: 4px;
    }}

    /* KPI Grid Cards (Apple Style) */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: var(--shadow-sm);
      position: relative;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: var(--border-hover);
    }}

    .kpi-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--text-tertiary);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .kpi-value {{
      font-size: 26px;
      font-weight: 800;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      letter-spacing: -0.8px;
      margin-bottom: 8px;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
      line-height: 1.1;
    }}

    .kpi-subtext {{
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
    }}

    /* Apple Trend Badges & Pills */
    .badge-trend {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      font-variant-numeric: tabular-nums;
      line-height: 1.2;
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

    /* Apple Progress Bar Track & Fill */
    .progress-bar-container {{
      width: 100%;
      height: 7px;
      background: var(--surface-sunken);
      border-radius: var(--radius-pill);
      overflow: hidden;
      margin-top: 8px;
    }}

    .progress-bar-fill {{
      height: 100%;
      border-radius: var(--radius-pill);
      transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* Main Chart and Side Insights Section */
    .section-charts {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}

    .chart-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 24px 26px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-sm);
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }}

    .chart-title {{
      font-family: 'Outfit', -apple-system, sans-serif;
      font-size: 16.5px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
      letter-spacing: -0.3px;
    }}

    .chart-legend {{
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-bullet {{
      width: 10px;
      height: 10px;
      border-radius: 3px;
    }}

    .chart-canvas-wrapper {{
      position: relative;
      width: 100%;
      height: 330px;
    }}

    /* Highlights Column (Top Aceleradores & Detratores) */
    .highlights-container {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .highlight-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 20px 22px;
      flex: 1;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
    }}

    .highlight-card-title {{
      font-family: 'Outfit', -apple-system, sans-serif;
      font-size: 14px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 14px;
      letter-spacing: -0.2px;
    }}

    .highlight-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      flex: 1;
    }}

    .highlight-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      background: var(--surface-subtle);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      transition: all 0.15s ease;
    }}

    .highlight-item:hover {{
      background: var(--surface-hover);
      border-color: var(--border);
      transform: translateX(2px);
    }}

    .highlight-info {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .highlight-name {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      max-width: 240px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .highlight-cat {{
      font-size: 11px;
      color: var(--text-tertiary);
    }}

    .highlight-metric {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}

    .highlight-gap {{
      font-size: 13.5px;
      font-weight: 700;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}

    /* Data Tables Section (Apple Segmented Toolbar) */
    .table-section {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 24px 26px;
      box-shadow: var(--shadow-sm);
    }}

    .table-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 16px;
    }}

    /* Apple Segmented Control for Table Navigation */
    .apple-segmented-control {{
      display: inline-flex;
      align-items: center;
      background: rgba(120, 120, 128, 0.12);
      padding: 4px;
      border-radius: var(--radius-md);
      gap: 2px;
    }}

    .segmented-btn {{
      border: none;
      background: transparent;
      padding: 7px 18px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}

    .segmented-btn:hover {{
      color: var(--text-primary);
    }}

    .segmented-btn.active {{
      background: var(--surface);
      color: var(--text-primary);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.1);
    }}

    /* Apple Pill Search Box */
    .table-search-box {{
      position: relative;
      width: 340px;
    }}

    .table-search-box input {{
      width: 100%;
      padding: 10px 16px 10px 38px;
      background: var(--surface-sunken);
      border: 1px solid transparent;
      border-radius: var(--radius-pill);
      color: var(--text-primary);
      font-size: 13px;
      outline: none;
      transition: all 0.2s ease;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}

    .table-search-box input:focus {{
      background: var(--surface);
      border-color: var(--apple-blue);
      box-shadow: 0 0 0 3px var(--apple-blue-soft);
    }}

    .table-search-box svg {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-tertiary);
    }}

    /* Table Styling (Apple macOS Table Style) */
    .table-responsive {{
      width: 100%;
      overflow-x: auto;
    }}

    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}

    table.data-table th {{
      padding: 12px 16px;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.5px;
      color: var(--text-tertiary);
      border-bottom: 1px solid var(--border);
      background: var(--surface-subtle);
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}

    table.data-table th:first-child {{
      border-top-left-radius: var(--radius-sm);
      border-bottom-left-radius: var(--radius-sm);
    }}

    table.data-table th:last-child {{
      border-top-right-radius: var(--radius-sm);
      border-bottom-right-radius: var(--radius-sm);
    }}

    table.data-table th:hover {{
      color: var(--text-primary);
    }}

    table.data-table td {{
      padding: 13px 16px;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text-primary);
      white-space: nowrap;
    }}

    table.data-table tbody tr {{
      transition: background 0.15s ease;
    }}

    table.data-table tbody tr:hover {{
      background: var(--surface-hover);
    }}

    .num-cell {{
      text-align: right;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", sans-serif;
      font-variant-numeric: tabular-nums;
      font-weight: 500;
    }}

    /* Footer */
    footer.footer {{
      margin-top: 40px;
      text-align: center;
      font-size: 12px;
      color: var(--text-tertiary);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 20px;
      border-top: 1px solid var(--border);
    }}

    @media (max-width: 1200px) {{
      .kpi-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .section-charts {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 768px) {{
      .app-container {{ padding: 16px; }}
      .channel-nav {{ grid-template-columns: repeat(2, 1fr); }}
      .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
      header.header {{ flex-direction: column; align-items: flex-start; gap: 16px; }}
      .header-actions {{ width: 100%; justify-content: space-between; }}
    }}
  </style>
</head>
<body>

  <div class="app-container">

    <!-- Header Executivo Estilo Apple HIG -->
    <header class="header">
      <div class="brand">
        <div class="logo-badge">SJ</div>
        <div class="brand-text">
          <h1>
            Acompanhamento Categorias Digital
            <span class="pill">Setembro 2026</span>
          </h1>
          <p>Visão Integrada de Vendas, Metas Diarizadas e Desvios — App, Site e Marketplace</p>
        </div>
      </div>

      <div class="header-actions">
        <div class="badge-status">
          <div class="pulse-dot"></div>
          <span id="headerPeriodo">D-1 Oficial (01 a 03/09/2026)</span>
        </div>
        
        <button class="btn btn-theme-toggle" id="btnThemeToggle" onclick="toggleTheme()" title="Alternar Modo Claro / Escuro">
          🌓
        </button>

        <button class="btn" id="btnExportExcel" onclick="exportToCSV()" title="Exportar dados da tabela ativa">
          📥 Exportar CSV
        </button>
        <button class="btn btn-primary" onclick="window.print()" title="Imprimir ou gerar PDF">
          🖨️ Relatório PDF
        </button>
      </div>
    </header>

    <!-- Seletor de Canais (Tabs Segmentadas Estilo Apple) -->
    <nav class="channel-nav">
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
        <div class="channel-sub-details">Consolidado Geral (App + Site + Mkt)</div>
      </div>

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
        <div class="channel-sub-details">App + App Tele Entrega</div>
      </div>

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
        <div class="channel-sub-details">Site + Site Tele Entrega</div>
      </div>

      <div class="channel-tab tab-mkt" onclick="switchChannel('marketplace')">
        <div class="channel-tab-header">
          <span class="channel-name">🛍️ Marketplace</span>
          <span class="channel-badge trend-pos" id="badgeAtingMkt">100.9% 🎯</span>
        </div>
        <div class="channel-sales" id="tabSalesMkt">R$ 1.638.913</div>
        <div class="channel-meta-sub">
          <span>Meta MTD: <strong id="tabMetaMkt">R$ 1.624.060</strong></span>
          <span id="tabGapMkt" class="badge-trend trend-pos">+R$ 14.852</span>
        </div>
        <div class="channel-sub-details">iFood + Ecommerce + Rappi</div>
      </div>
    </nav>

    <!-- Grid de KPIs Dinâmicos -->
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
          <span>vs Set/25</span>
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
          <span>Curva Acumulada: <strong id="kpiPctCurva" style="color: var(--text-primary);">11.35%</strong></span>
        </div>
      </div>

      <!-- 3. Atingimento MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Atingimento MTD</span>
          <span>📊</span>
        </div>
        <div class="kpi-value" id="kpiAtingMtd" style="color: var(--apple-orange);">94.9%</div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" id="kpiProgressBar" style="width: 94.9%; background: var(--apple-orange);"></div>
        </div>
      </div>

      <!-- 4. GAP / Desvio MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Desvio GAP (MTD)</span>
          <span>⚖️</span>
        </div>
        <div class="kpi-value" id="kpiGapMtd" style="color: var(--apple-red);">-R$ 316.326</div>
        <div class="kpi-subtext">
          <span id="kpiGapStatus">Déficit vs Curva Oficial</span>
        </div>
      </div>

      <!-- 5. Projeção Fechamento -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Projeção Fechamento</span>
          <span>🔮</span>
        </div>
        <div class="kpi-value" id="kpiProjecao">R$ 51.958.230</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-neutral" id="kpiAtingProj">94.9% da Meta</span>
          <span>Mês: R$ 54.7M</span>
        </div>
      </div>

      <!-- 6. Crescimento MoM -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Evolução MoM (vs Ago)</span>
          <span>📈</span>
        </div>
        <div class="kpi-value" id="kpiMoMValue" style="color: var(--apple-green);">+17.1%</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiMoMBadge">+R$ 861.851</span>
          <span>vs Ago/26 MTD</span>
        </div>
      </div>
    </section>

    <!-- Gráficos e Destaques -->
    <section class="section-charts">
      <!-- Gráfico de Evolução Diária da Curva de Metas -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span>📅 Curva Diária de Metas vs Realizado (30 Dias de Setembro)</span>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <div class="legend-bullet" style="background: var(--apple-blue);"></div>
              <span>Realizado Diário</span>
            </div>
            <div class="legend-item">
              <div class="legend-bullet" style="background: var(--text-quaternary);"></div>
              <span>Meta Diária Oficial</span>
            </div>
            <div class="legend-item">
              <div class="legend-bullet" style="background: var(--apple-green);"></div>
              <span>Curva Acumulada</span>
            </div>
          </div>
        </div>
        <div class="chart-canvas-wrapper">
          <canvas id="chartEvolucaoDiaria"></canvas>
        </div>
      </div>

      <!-- Card Lateral de Destaques: Top Aceleradores e Detratores -->
      <div class="highlights-container">
        <!-- Aceleradores -->
        <div class="highlight-card" style="border-top: 3px solid var(--apple-green);">
          <div class="highlight-card-title" style="color: var(--apple-green-text);">
            <span>🚀 Top Linhas Superando a Meta</span>
          </div>
          <div class="highlight-list" id="listAceleradores">
            <!-- Renderizado via JS -->
          </div>
        </div>

        <!-- Detratores -->
        <div class="highlight-card" style="border-top: 3px solid var(--apple-red);">
          <div class="highlight-card-title" style="color: var(--apple-red-text);">
            <span>⚠️ Top Linhas com Maior Oportunidade (GAP)</span>
          </div>
          <div class="highlight-list" id="listDetratores">
            <!-- Renderizado via JS -->
          </div>
        </div>
      </div>
    </section>

    <!-- Tabela Analítica Multidimensional -->
    <section class="table-section">
      <div class="table-toolbar">
        <div class="apple-segmented-control">
          <button class="segmented-btn active" id="tabBtnGrupos" onclick="switchTableTab('grupos')">
            🏢 Grupos de Categorias
          </button>
          <button class="segmented-btn" id="tabBtnLinhas" onclick="switchTableTab('linhas')">
            📦 Linhas de Produtos (300)
          </button>
          <button class="segmented-btn" id="tabBtnSkus" onclick="switchTableTab('skus')">
            🏷️ Top SKUs (28.857 Itens)
          </button>
        </div>

        <div class="table-search-box">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input type="text" id="tableSearchInput" placeholder="Buscar por grupo, linha, produto ou ID..." oninput="handleSearch(this.value)">
        </div>
      </div>

      <div class="table-responsive">
        <table class="data-table" id="mainDataTable">
          <thead id="tableHead">
            <!-- Dynamic columns based on active tab -->
          </thead>
          <tbody id="tableBody">
            <!-- Dynamic rows -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Rodapé Estilo Apple -->
    <footer class="footer">
      <div>
        <strong>Farmácias São João</strong> — Diretoria de E-commerce & Negócios Digitais
      </div>
      <div>
        Atualizado em: <span id="dataAtualizacao" style="font-variant-numeric: tabular-nums; font-weight: 600;">-</span> | Fonte: Qlik Sense Enterprise
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
    let activeTableTab = 'grupos'; // 'grupos', 'linhas', 'skus'
    let searchTerm = '';
    let chartInstance = null;

    const fmtMoney = (v) => {{
      if (v === null || v === undefined || isNaN(v)) return 'R$ 0';
      return new Intl.NumberFormat('pt-BR', {{ style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }}).format(v);
    }};

    const fmtPct = (v) => {{
      if (v === null || v === undefined || isNaN(v)) return '0.0%';
      return v.toFixed(1) + '%';
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
      const data = window.DASHBOARD_DATA;
      if (!data) return;

      document.getElementById('dataAtualizacao').textContent = data.gerado_em || 'Hoje';
      document.getElementById('headerPeriodo').textContent = `D-1 Oficial (${{data.kpis.data_corte}})`;

      updateChannelNavSummary();
      updateKpis();
      renderChart();
      renderHighlights();
      renderTable();
    }}

    function switchChannel(canal) {{
      activeChannel = canal;
      
      document.querySelectorAll('.channel-tab').forEach(tab => tab.classList.remove('active'));
      if (canal === 'total') document.querySelector('.tab-total').classList.add('active');
      else if (canal === 'app') document.querySelector('.tab-app').classList.add('active');
      else if (canal === 'site') document.querySelector('.tab-site').classList.add('active');
      else if (canal === 'marketplace') document.querySelector('.tab-mkt').classList.add('active');

      updateKpis();
      renderChart();
      renderTable();
    }}

    function switchTableTab(tab) {{
      activeTableTab = tab;
      document.querySelectorAll('.segmented-btn').forEach(btn => btn.classList.remove('active'));
      if (tab === 'grupos') document.getElementById('tabBtnGrupos').classList.add('active');
      else if (tab === 'linhas') document.getElementById('tabBtnLinhas').classList.add('active');
      else if (tab === 'skus') document.getElementById('tabBtnSkus').classList.add('active');

      renderTable();
    }}

    function handleSearch(term) {{
      searchTerm = term.trim().toLowerCase();
      renderTable();
    }}

    function updateChannelNavSummary() {{
      const k = window.DASHBOARD_DATA.kpis.canais;
      // Total
      document.getElementById('tabSalesTotal').textContent = fmtMoney(k.total.venda_mtd);
      document.getElementById('tabMetaTotal').textContent = fmtMoney(k.total.meta_mtd);
      document.getElementById('badgeAtingTotal').textContent = fmtPct(k.total.ating_mtd_pct);
      document.getElementById('tabGapTotal').textContent = (k.total.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.total.gap_mtd);
      document.getElementById('tabGapTotal').className = 'badge-trend ' + (k.total.gap_mtd >= 0 ? 'trend-pos' : 'trend-neg');
      
      // App
      document.getElementById('tabSalesApp').textContent = fmtMoney(k.app.venda_mtd);
      document.getElementById('tabMetaApp').textContent = fmtMoney(k.app.meta_mtd);
      document.getElementById('badgeAtingApp').textContent = fmtPct(k.app.ating_mtd_pct) + (k.app.ating_mtd_pct >= 100 ? ' 🚀' : '');
      document.getElementById('tabGapApp').textContent = (k.app.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.app.gap_mtd);
      document.getElementById('tabGapApp').className = 'badge-trend ' + (k.app.gap_mtd >= 0 ? 'trend-pos' : 'trend-neg');

      // Site
      document.getElementById('tabSalesSite').textContent = fmtMoney(k.site.venda_mtd);
      document.getElementById('tabMetaSite').textContent = fmtMoney(k.site.meta_mtd);
      document.getElementById('badgeAtingSite').textContent = fmtPct(k.site.ating_mtd_pct);
      document.getElementById('tabGapSite').textContent = (k.site.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.site.gap_mtd);
      document.getElementById('tabGapSite').className = 'badge-trend ' + (k.site.gap_mtd >= 0 ? 'trend-pos' : 'trend-neg');

      // Marketplace
      document.getElementById('tabSalesMkt').textContent = fmtMoney(k.marketplace.venda_mtd);
      document.getElementById('tabMetaMkt').textContent = fmtMoney(k.marketplace.meta_mtd);
      document.getElementById('badgeAtingMkt').textContent = fmtPct(k.marketplace.ating_mtd_pct) + (k.marketplace.ating_mtd_pct >= 100 ? ' 🎯' : '');
      document.getElementById('tabGapMkt').textContent = (k.marketplace.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.marketplace.gap_mtd);
      document.getElementById('tabGapMkt').className = 'badge-trend ' + (k.marketplace.gap_mtd >= 0 ? 'trend-pos' : 'trend-neg');
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

      // GAP
      const gapElem = document.getElementById('kpiGapMtd');
      gapElem.textContent = (c.gap_mtd >= 0 ? '+' : '') + fmtMoney(c.gap_mtd);
      gapElem.style.color = c.gap_mtd >= 0 ? 'var(--apple-green-text)' : 'var(--apple-red-text)';
      document.getElementById('kpiGapStatus').textContent = c.gap_mtd >= 0 ? 'Superávit vs Curva' : 'Déficit vs Curva';

      // Projeção
      document.getElementById('kpiProjecao').textContent = fmtMoney(c.projecao_fechamento);
      document.getElementById('kpiAtingProj').textContent = fmtPct(c.ating_proj_pct) + ' da Meta';

      // YoY / MoM
      const yoy = c.crescimento_yoy_pct || 0;
      const yoyBadge = document.getElementById('kpiYoYBadge');
      yoyBadge.textContent = (yoy >= 0 ? '↑ +' : '↓ ') + yoy.toFixed(1) + '% YoY';
      yoyBadge.className = 'badge-trend ' + (yoy >= 0 ? 'trend-pos' : 'trend-neg');

      const mom = c.crescimento_mom_pct || 0;
      const momElem = document.getElementById('kpiMoMValue');
      momElem.textContent = (mom >= 0 ? '+' : '') + mom.toFixed(1) + '%';
      momElem.style.color = mom >= 0 ? 'var(--apple-green)' : 'var(--apple-red)';
      document.getElementById('kpiMoMBadge').textContent = (c.crescimento_mom_diff >= 0 ? '+' : '') + fmtMoney(c.crescimento_mom_diff);
      document.getElementById('kpiMoMBadge').className = 'badge-trend ' + (c.crescimento_mom_diff >= 0 ? 'trend-pos' : 'trend-neg');
    }}

    function renderChart() {{
      const curva = window.DASHBOARD_DATA.curva_diaria;
      const ctx = document.getElementById('chartEvolucaoDiaria').getContext('2d');
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

      const labels = curva.map(c => `${{c.dia}} (${{c.dow}})`);
      
      let realKey = 'real_dia_total';
      let metaKey = 'meta_dia_total';
      let acumKey = 'real_acum_total';
      let metaAcumKey = 'meta_acum_total';

      if (activeChannel === 'app') {{
        realKey = 'real_dia_app'; metaKey = 'meta_dia_app'; acumKey = 'real_acum_app'; metaAcumKey = 'meta_acum_app';
      }} else if (activeChannel === 'site') {{
        realKey = 'real_dia_site'; metaKey = 'meta_dia_site'; acumKey = 'real_acum_site'; metaAcumKey = 'meta_acum_site';
      }} else if (activeChannel === 'marketplace') {{
        realKey = 'real_dia_mkt'; metaKey = 'meta_dia_mkt'; acumKey = 'real_acum_mkt'; metaAcumKey = 'meta_acum_mkt';
      }}

      const dataReal = curva.map(c => c[realKey]);
      const dataMeta = curva.map(c => c[metaKey]);
      const dataRealAcum = curva.map(c => c[acumKey]);
      const dataMetaAcum = curva.map(c => c[metaAcumKey]);

      if (chartInstance) chartInstance.destroy();

      const blueColor = isDark ? '#2997FF' : '#0071E3';
      const greenColor = isDark ? '#30D158' : '#34C759';
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.05)';
      const metaBarColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.06)';
      const textColor = isDark ? '#8E8E93' : '#86868B';

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
              order: 2
            }},
            {{
              label: 'Meta Diária Oficial',
              data: dataMeta,
              backgroundColor: metaBarColor,
              borderRadius: 6,
              order: 3
            }},
            {{
              label: 'Meta Acumulada',
              data: dataMetaAcum,
              type: 'line',
              borderColor: textColor,
              borderDash: [5, 5],
              borderWidth: 2,
              pointRadius: 0,
              yAxisID: 'yAcum',
              order: 1
            }},
            {{
              label: 'Realizado Acumulado',
              data: dataRealAcum,
              type: 'line',
              borderColor: greenColor,
              backgroundColor: isDark ? 'rgba(48, 209, 88, 0.12)' : 'rgba(52, 199, 89, 0.10)',
              fill: true,
              tension: 0.35,
              borderWidth: 3,
              pointRadius: 4,
              pointHoverRadius: 6,
              pointBackgroundColor: greenColor,
              yAxisID: 'yAcum',
              order: 0
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
              backgroundColor: isDark ? 'rgba(44, 44, 46, 0.95)' : 'rgba(29, 29, 31, 0.92)',
              titleColor: '#FFFFFF',
              bodyColor: '#E5E5EA',
              padding: 12,
              cornerRadius: 10,
              titleFont: {{
                family: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
                size: 13,
                weight: '700'
              }},
              bodyFont: {{
                family: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                size: 12
              }},
              callbacks: {{
                label: function(context) {{
                  const val = context.parsed.y;
                  if (val === null || val === undefined) return '';
                  return `${{context.dataset.label}}: ${{fmtMoney(val)}}`;
                }}
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{ display: false }},
              ticks: {{
                color: textColor,
                font: {{
                  family: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                  size: 11
                }}
              }}
            }},
            y: {{
              position: 'left',
              grid: {{ color: gridColor }},
              ticks: {{
                color: textColor,
                font: {{
                  family: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                  size: 11
                }},
                callback: v => (v / 1000).toFixed(0) + 'k'
              }}
            }},
            yAcum: {{
              position: 'right',
              grid: {{ display: false }},
              ticks: {{
                color: greenColor,
                font: {{
                  family: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                  size: 11
                }},
                callback: v => (v / 1000000).toFixed(1) + 'M'
              }}
            }}
          }}
        }}
      }});
    }}

    function renderHighlights() {{
      const destaques = window.DASHBOARD_DATA.destaques;
      
      const elAcel = document.getElementById('listAceleradores');
      elAcel.innerHTML = destaques.aceleradores.map(item => `
        <div class="highlight-item">
          <div class="highlight-info">
            <span class="highlight-name" title="${{item.linha}}">${{item.linha}}</span>
            <span class="highlight-cat">${{item.grupo}} • ${{fmtPct(item.ating_mtd_pct)}} da Meta</span>
          </div>
          <div class="highlight-metric">
            <div class="highlight-gap" style="color: var(--apple-green-text);">+${{fmtMoney(item.gap_mtd)}}</div>
            <div style="font-size: 11px; color: var(--text-tertiary);">Venda: ${{fmtMoney(item.realizado_mtd)}}</div>
          </div>
        </div>
      `).join('');

      const elDet = document.getElementById('listDetratores');
      elDet.innerHTML = destaques.detratores.map(item => `
        <div class="highlight-item">
          <div class="highlight-info">
            <span class="highlight-name" title="${{item.linha}}">${{item.linha}}</span>
            <span class="highlight-cat">${{item.grupo}} • ${{fmtPct(item.ating_mtd_pct)}} da Meta</span>
          </div>
          <div class="highlight-metric">
            <div class="highlight-gap" style="color: var(--apple-red-text);">${{fmtMoney(item.gap_mtd)}}</div>
            <div style="font-size: 11px; color: var(--text-tertiary);">Venda: ${{fmtMoney(item.realizado_mtd)}}</div>
          </div>
        </div>
      `).join('');
    }}

    function renderTable() {{
      const thead = document.getElementById('tableHead');
      const tbody = document.getElementById('tableBody');

      if (activeTableTab === 'grupos') {{
        renderGruposTable(thead, tbody);
      }} else if (activeTableTab === 'linhas') {{
        renderLinhasTable(thead, tbody);
      }} else if (activeTableTab === 'skus') {{
        renderSkusTable(thead, tbody);
      }}
    }}

    function renderGruposTable(thead, tbody) {{
      thead.innerHTML = `
        <tr>
          <th>Grupo de Categorias</th>
          <th class="num-cell">Meta MTD</th>
          <th class="num-cell">Realizado MTD</th>
          <th class="num-cell">Ating. %</th>
          <th class="num-cell">GAP (R$)</th>
          <th class="num-cell">App MTD</th>
          <th class="num-cell">Site MTD</th>
          <th class="num-cell">Mkt MTD</th>
          <th class="num-cell">Projeção Mês</th>
          <th class="num-cell">YoY %</th>
        </tr>
      `;

      let items = window.DASHBOARD_DATA.grupos;
      if (searchTerm) {{
        items = items.filter(g => g.grupo.toLowerCase().includes(searchTerm));
      }}

      tbody.innerHTML = items.map(g => {{
        const isPos = g.gap_mtd >= 0;
        return `
          <tr>
            <td><strong>${{g.grupo}}</strong> <span style="font-size: 11px; color: var(--text-tertiary);">(${{g.total_linhas}} linhas)</span></td>
            <td class="num-cell">${{fmtMoney(g.meta_mtd)}}</td>
            <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(g.realizado_mtd)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{g.ating_mtd_pct >= 100 ? 'trend-pos' : g.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                ${{fmtPct(g.ating_mtd_pct)}}
              </span>
            </td>
            <td class="num-cell" style="font-weight: 700; color: ${{isPos ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
              ${{(isPos ? '+' : '') + fmtMoney(g.gap_mtd)}}
            </td>
            <td class="num-cell">${{fmtMoney(g.realizado_app)}}</td>
            <td class="num-cell">${{fmtMoney(g.realizado_site)}}</td>
            <td class="num-cell">${{fmtMoney(g.realizado_mkt)}}</td>
            <td class="num-cell">${{fmtMoney(g.projecao_fechamento)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{g.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                ${{(g.crescimento_yoy_pct >= 0 ? '+' : '') + g.crescimento_yoy_pct.toFixed(1)}}%
              </span>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function renderLinhasTable(thead, tbody) {{
      thead.innerHTML = `
        <tr>
          <th>Linha de Produto</th>
          <th>Grupo</th>
          <th class="num-cell">Meta MTD</th>
          <th class="num-cell">Realizado MTD</th>
          <th class="num-cell">Ating. %</th>
          <th class="num-cell">GAP (R$)</th>
          <th class="num-cell">App</th>
          <th class="num-cell">Site</th>
          <th class="num-cell">Mkt</th>
          <th class="num-cell">Projeção Mês</th>
          <th class="num-cell">YoY %</th>
        </tr>
      `;

      let items = window.DASHBOARD_DATA.linhas;
      if (searchTerm) {{
        items = items.filter(l => 
          l.linha.toLowerCase().includes(searchTerm) || 
          l.grupo.toLowerCase().includes(searchTerm)
        );
      }}

      tbody.innerHTML = items.slice(0, 100).map(l => {{
        const isPos = l.gap_mtd >= 0;
        return `
          <tr>
            <td><strong>${{l.linha}}</strong></td>
            <td style="color: var(--text-secondary); font-size: 12px;">${{l.grupo}}</td>
            <td class="num-cell">${{fmtMoney(l.meta_mtd)}}</td>
            <td class="num-cell" style="font-weight: 700; color: var(--apple-blue);">${{fmtMoney(l.realizado_mtd)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{l.ating_mtd_pct >= 100 ? 'trend-pos' : l.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                ${{fmtPct(l.ating_mtd_pct)}}
              </span>
            </td>
            <td class="num-cell" style="font-weight: 700; color: ${{isPos ? 'var(--apple-green-text)' : 'var(--apple-red-text)'}};">
              ${{(isPos ? '+' : '') + fmtMoney(l.gap_mtd)}}
            </td>
            <td class="num-cell">${{fmtMoney(l.realizado_app)}}</td>
            <td class="num-cell">${{fmtMoney(l.realizado_site)}}</td>
            <td class="num-cell">${{fmtMoney(l.realizado_mkt)}}</td>
            <td class="num-cell">${{fmtMoney(l.projecao_fechamento)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{l.crescimento_yoy_pct >= 0 ? 'trend-pos' : 'trend-neg'}}">
                ${{(l.crescimento_yoy_pct >= 0 ? '+' : '') + l.crescimento_yoy_pct.toFixed(1)}}%
              </span>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function renderSkusTable(thead, tbody) {{
      thead.innerHTML = `
        <tr>
          <th>ID</th>
          <th>Descrição do SKU</th>
          <th>Laboratório</th>
          <th>Linha</th>
          <th class="num-cell">Meta MTD</th>
          <th class="num-cell">Meta App</th>
          <th class="num-cell">Meta Site</th>
          <th class="num-cell">Meta Mkt</th>
          <th class="num-cell">Meta Mensal</th>
        </tr>
      `;

      let items = window.DASHBOARD_DATA.top_skus;
      if (searchTerm) {{
        items = items.filter(s => 
          String(s.id).includes(searchTerm) || 
          s.nome.toLowerCase().includes(searchTerm) ||
          s.laboratorio.toLowerCase().includes(searchTerm) ||
          s.linha.toLowerCase().includes(searchTerm)
        );
      }}

      tbody.innerHTML = items.slice(0, 100).map(s => `
        <tr>
          <td style="font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', monospace; font-size: 11.5px; font-weight: 600; color: var(--apple-blue);">${{s.id}}</td>
          <td><strong>${{s.nome}}</strong></td>
          <td style="color: var(--text-secondary); font-size: 12px;">${{s.laboratorio}}</td>
          <td style="color: var(--text-tertiary); font-size: 12px;">${{s.linha}}</td>
          <td class="num-cell" style="font-weight: 700; color: var(--apple-green-text);">${{fmtMoney(s.meta_mtd)}}</td>
          <td class="num-cell">${{fmtMoney(s.meta_app)}}</td>
          <td class="num-cell">${{fmtMoney(s.meta_site)}}</td>
          <td class="num-cell">${{fmtMoney(s.meta_mkt)}}</td>
          <td class="num-cell" style="color: var(--text-secondary);">${{fmtMoney(s.meta_mensal)}}</td>
        </tr>
      `).join('');
    }}

    function exportToCSV() {{
      let csv = '';
      if (activeTableTab === 'grupos') {{
        csv = 'Grupo;Meta_MTD;Realizado_MTD;Ating_Pct;GAP_MTD;App_MTD;Site_MTD;Mkt_MTD;Projecao_Mes;YoY_Pct\\n';
        window.DASHBOARD_DATA.grupos.forEach(g => {{
          csv += `"${{g.grupo}}";${{g.meta_mtd}};${{g.realizado_mtd}};${{g.ating_mtd_pct}};${{g.gap_mtd}};${{g.realizado_app}};${{g.realizado_site}};${{g.realizado_mkt}};${{g.projecao_fechamento}};${{g.crescimento_yoy_pct}}\\n`;
        }});
      }} else if (activeTableTab === 'linhas') {{
        csv = 'Linha;Grupo;Meta_MTD;Realizado_MTD;Ating_Pct;GAP_MTD;App_MTD;Site_MTD;Mkt_MTD;Projecao_Mes;YoY_Pct\\n';
        window.DASHBOARD_DATA.linhas.forEach(l => {{
          csv += `"${{l.linha}}";"${{l.grupo}}";${{l.meta_mtd}};${{l.realizado_mtd}};${{l.ating_mtd_pct}};${{l.gap_mtd}};${{l.realizado_app}};${{l.realizado_site}};${{l.realizado_mkt}};${{l.projecao_fechamento}};${{l.crescimento_yoy_pct}}\\n`;
        }});
      }} else if (activeTableTab === 'skus') {{
        csv = 'ID;Descricao;Laboratorio;Linha;Meta_MTD;Meta_App;Meta_Site;Meta_Mkt;Meta_Mensal\\n';
        window.DASHBOARD_DATA.top_skus.forEach(s => {{
          csv += `${{s.id}};"${{s.nome}}";"${{s.laboratorio}}";"${{s.linha}}";${{s.meta_mtd}};${{s.meta_app}};${{s.meta_site}};${{s.meta_mkt}};${{s.meta_mensal}}\\n`;
        }});
      }}

      const blob = new Blob(["\\uFEFF" + csv], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `Acompanhamento_Digital_${{activeTableTab}}_${{new Date().toISOString().slice(0,10)}}.csv`;
      link.click();
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Dashboard Executivo (Apple Design) compilado com sucesso em: {OUTPUT_HTML}")
    print(f"   Tamanho final do HTML: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")
    print(f"🎉 Compilação concluída em {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    build()
