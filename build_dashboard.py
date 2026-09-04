"""
build_dashboard.py — Compila o Dashboard Executivo Moderno (HTML5 + CSS Glassmorphism + JS Interativo)
para o projeto Acompanhamento Categorias Digital (Site, App e Marketplace).
Gera um arquivo 'index.html' independente, ultra-rápido e responsivo.
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
    print("  COMPILAÇÃO DO DASHBOARD EXECUTIVO: CATEGORIAS DIGITAL")
    print("=" * 70)

    if not os.path.exists(DATA_JSON_PATH):
        print("Arquivo dashboard_digital_data.json não encontrado. Rodando process_digital_analytics...")
        import process_digital_analytics
        process_digital_analytics.main()

    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data_content = f.read()

    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Acompanhamento Digital — Farmácias São João (App, Site e Marketplace)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg-base: #080c14;
      --bg-surface: #0f172a;
      --bg-card: rgba(15, 23, 42, 0.75);
      --bg-card-hover: rgba(30, 41, 59, 0.85);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(6, 182, 212, 0.5);
      
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-subtle: #64748b;
      
      --accent-cyan: #06b6d4;
      --accent-blue: #3b82f6;
      --accent-indigo: #6366f1;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #a855f7;

      --glow-cyan: 0 0 25px rgba(6, 182, 212, 0.25);
      --glow-emerald: 0 0 25px rgba(16, 185, 129, 0.25);
      --glow-rose: 0 0 25px rgba(244, 63, 94, 0.25);
      --glow-amber: 0 0 25px rgba(245, 158, 11, 0.25);

      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-full: 9999px;
      --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-base);
      color: var(--text-main);
      min-height: 100vh;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 15% 10%, rgba(6, 182, 212, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 25%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 90%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
      background-attachment: fixed;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-base); }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}

    /* Layout */
    .app-container {{
      max-width: 1720px;
      margin: 0 auto;
      padding: 24px 32px 64px 32px;
    }}

    /* Top Navigation Bar */
    header.header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      margin-bottom: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .logo-badge {{
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, #e11d48, #be123c);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 18px;
      letter-spacing: -0.5px;
      color: white;
      box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
    }}

    .brand-text h1 {{
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .brand-text h1 .pill {{
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: var(--radius-full);
      background: rgba(6, 182, 212, 0.15);
      color: var(--accent-cyan);
      border: 1px solid rgba(6, 182, 212, 0.3);
    }}

    .brand-text p {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge-status {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: var(--radius-full);
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.25);
      font-size: 12px;
      font-weight: 600;
      color: var(--accent-emerald);
    }}

    .pulse-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-emerald);
      box-shadow: 0 0 10px var(--accent-emerald);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
      100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: var(--transition);
      border: 1px solid var(--border-subtle);
      background: rgba(30, 41, 59, 0.7);
      color: var(--text-main);
    }}

    .btn:hover {{
      background: rgba(51, 65, 85, 0.9);
      border-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-1px);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      border: none;
      color: white;
      box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }}

    .btn-primary:hover {{
      filter: brightness(1.1);
      box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
    }}

    /* Channel Selector Tabs (App, Site, Marketplace, Total) */
    .channel-nav {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 24px;
    }}

    .channel-tab {{
      display: flex;
      flex-direction: column;
      padding: 16px 20px;
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      cursor: pointer;
      transition: var(--transition);
      position: relative;
      overflow: hidden;
    }}

    .channel-tab::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background: transparent;
      transition: var(--transition);
    }}

    .channel-tab:hover {{
      transform: translateY(-2px);
      background: var(--bg-card-hover);
      border-color: rgba(255, 255, 255, 0.15);
    }}

    .channel-tab.active {{
      background: rgba(30, 41, 59, 0.95);
      border-color: var(--active-color, var(--accent-cyan));
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4), var(--active-glow, var(--glow-cyan));
    }}

    .channel-tab.active::before {{
      background: var(--active-color, var(--accent-cyan));
    }}

    .channel-tab-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .channel-name {{
      font-size: 14px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-main);
    }}

    .channel-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: var(--radius-full);
      background: rgba(255, 255, 255, 0.08);
    }}

    .channel-sales {{
      font-size: 22px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: -0.5px;
      margin-bottom: 4px;
    }}

    .channel-meta-sub {{
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    /* Specific Channel Theme Colors */
    .tab-total {{ --active-color: var(--accent-emerald); --active-glow: var(--glow-emerald); }}
    .tab-app {{ --active-color: var(--accent-cyan); --active-glow: var(--glow-cyan); }}
    .tab-site {{ --active-color: var(--accent-purple); --active-glow: 0 0 25px rgba(168, 85, 247, 0.25); }}
    .tab-mkt {{ --active-color: var(--accent-amber); --active-glow: var(--glow-amber); }}

    /* KPI Grid Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: var(--transition);
      position: relative;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.15);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }}

    .kpi-title {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .kpi-value {{
      font-size: 24px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
    }}

    .kpi-subtext {{
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .badge-trend {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }}

    .trend-pos {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }}
    .trend-neg {{ background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); }}
    .trend-neutral {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }}

    /* Progress bar */
    .progress-bar-container {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-full);
      overflow: hidden;
      margin-top: 8px;
    }}

    .progress-bar-fill {{
      height: 100%;
      border-radius: var(--radius-full);
      transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Main Chart and Side Insights Section */
    .section-charts {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}

    .chart-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 22px 24px;
      display: flex;
      flex-direction: column;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
    }}

    .chart-title {{
      font-size: 16px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .chart-legend {{
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: var(--text-muted);
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-bullet {{
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }}

    .chart-canvas-wrapper {{
      position: relative;
      width: 100%;
      height: 320px;
    }}

    /* Insights / Highlights Column */
    .highlights-container {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .highlight-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 20px;
      flex: 1;
    }}

    .highlight-card-title {{
      font-size: 14px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 14px;
    }}

    .highlight-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .highlight-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      transition: var(--transition);
    }}

    .highlight-item:hover {{
      background: rgba(255, 255, 255, 0.06);
    }}

    .highlight-info {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .highlight-name {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      max-width: 240px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .highlight-cat {{
      font-size: 11px;
      color: var(--text-subtle);
    }}

    .highlight-metric {{
      text-align: right;
    }}

    .highlight-gap {{
      font-size: 13px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* Data Tables Section (Tabs: Categorias, Linhas, SKUs) */
    .table-section {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }}

    .table-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .table-nav-tabs {{
      display: flex;
      gap: 8px;
      background: rgba(15, 23, 42, 0.8);
      padding: 4px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-subtle);
    }}

    .nav-tab-btn {{
      padding: 8px 16px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      background: transparent;
      border: none;
      cursor: pointer;
      transition: var(--transition);
    }}

    .nav-tab-btn.active {{
      background: rgba(30, 41, 59, 1);
      color: var(--text-main);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }}

    .table-search-box {{
      position: relative;
      width: 320px;
    }}

    .table-search-box input {{
      width: 100%;
      padding: 10px 14px 10px 38px;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      color: var(--text-main);
      font-size: 13px;
      outline: none;
      transition: var(--transition);
    }}

    .table-search-box input:focus {{
      border-color: var(--accent-cyan);
      box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
    }}

    .table-search-box svg {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-subtle);
    }}

    /* Table Styling */
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
      color: var(--text-muted);
      border-bottom: 2px solid rgba(255, 255, 255, 0.08);
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}

    table.data-table th:hover {{
      color: var(--text-main);
    }}

    table.data-table td {{
      padding: 12px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-main);
      white-space: nowrap;
    }}

    table.data-table tbody tr {{
      transition: var(--transition);
    }}

    table.data-table tbody tr:hover {{
      background: rgba(255, 255, 255, 0.03);
    }}

    .num-cell {{
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 500;
    }}

    .badge-channel {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
    }}

    /* Footer */
    footer.footer {{
      margin-top: 40px;
      text-align: center;
      font-size: 12px;
      color: var(--text-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 20px;
      border-top: 1px solid var(--border-subtle);
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

    <!-- Header Executivo -->
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
        <button class="btn" id="btnExportExcel" onclick="exportToCSV()" title="Exportar dados da tabela ativa">
          📥 Exportar CSV
        </button>
        <button class="btn btn-primary" onclick="window.print()" title="Imprimir ou gerar PDF">
          🖨️ Relatório PDF
        </button>
      </div>
    </header>

    <!-- Seletor de Canal Executivo (Tabs Superiores) -->
    <nav class="channel-nav">
      <div class="channel-tab tab-total active" onclick="switchChannel('total')">
        <div class="channel-tab-header">
          <span class="channel-name">🌐 Total Digital</span>
          <span class="channel-badge" id="badgeAtingTotal">94.9%</span>
        </div>
        <div class="channel-sales" id="tabSalesTotal">R$ 5.897.259</div>
        <div class="channel-meta-sub">
          <span>Meta MTD: <strong id="tabMetaTotal">R$ 6.213.585</strong></span>
          <span id="tabGapTotal" class="trend-neg" style="padding: 2px 4px; border-radius: 4px;">-R$ 316.326</span>
        </div>
      </div>

      <div class="channel-tab tab-app" onclick="switchChannel('app')">
        <div class="channel-tab-header">
          <span class="channel-name">📱 App</span>
          <span class="channel-badge trend-pos" id="badgeAtingApp">109.2% 🚀</span>
        </div>
        <div class="channel-sales" id="tabSalesApp">R$ 3.215.637</div>
        <div class="channel-meta-sub">
          <span>Meta MTD: <strong id="tabMetaApp">R$ 2.944.468</strong></span>
          <span id="tabGapApp" class="trend-pos" style="padding: 2px 4px; border-radius: 4px;">+R$ 271.169</span>
        </div>
        <div style="font-size: 10px; color: var(--text-subtle); margin-top: 4px;">App + App Tele Entrega</div>
      </div>

      <div class="channel-tab tab-site" onclick="switchChannel('site')">
        <div class="channel-tab-header">
          <span class="channel-name">💻 Site</span>
          <span class="channel-badge trend-neg" id="badgeAtingSite">63.4% ⚠️</span>
        </div>
        <div class="channel-sales" id="tabSalesSite">R$ 1.042.709</div>
        <div class="channel-meta-sub">
          <span>Meta MTD: <strong id="tabMetaSite">R$ 1.645.057</strong></span>
          <span id="tabGapSite" class="trend-neg" style="padding: 2px 4px; border-radius: 4px;">-R$ 602.348</span>
        </div>
        <div style="font-size: 10px; color: var(--text-subtle); margin-top: 4px;">Site + Site Tele Entrega</div>
      </div>

      <div class="channel-tab tab-mkt" onclick="switchChannel('marketplace')">
        <div class="channel-tab-header">
          <span class="channel-name">🛍️ Marketplace</span>
          <span class="channel-badge trend-pos" id="badgeAtingMkt">100.9% 🎯</span>
        </div>
        <div class="channel-sales" id="tabSalesMkt">R$ 1.638.913</div>
        <div class="channel-meta-sub">
          <span>Meta MTD: <strong id="tabMetaMkt">R$ 1.624.060</strong></span>
          <span id="tabGapMkt" class="trend-pos" style="padding: 2px 4px; border-radius: 4px;">+R$ 14.852</span>
        </div>
        <div style="font-size: 10px; color: var(--text-subtle); margin-top: 4px;">iFood + Ecommerce + Rappi</div>
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
        <div class="kpi-value" id="kpiVendaMtd" style="color: var(--accent-cyan);">R$ 5.897.259</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiYoYBadge">↑ +43.2% YoY</span>
          <span style="color: var(--text-subtle);">vs Set/25</span>
        </div>
      </div>

      <!-- 2. Meta Diarizada MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Meta Diarizada MTD</span>
          <span>🎯</span>
        </div>
        <div class="kpi-value" id="kpiMetaMtd">R$ 6.213.585</div>
        <div class="kpi-subtext" style="color: var(--text-muted);">
          <span>Curva Acumulada: <strong id="kpiPctCurva">11.35%</strong></span>
        </div>
      </div>

      <!-- 3. Atingimento MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Atingimento MTD</span>
          <span>📊</span>
        </div>
        <div class="kpi-value" id="kpiAtingMtd" style="color: var(--accent-amber);">94.9%</div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" id="kpiProgressBar" style="width: 94.9%; background: var(--accent-amber);"></div>
        </div>
      </div>

      <!-- 4. GAP / Desvio MTD -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Desvio GAP (MTD)</span>
          <span>⚖️</span>
        </div>
        <div class="kpi-value" id="kpiGapMtd" style="color: var(--accent-rose);">-R$ 316.326</div>
        <div class="kpi-subtext">
          <span id="kpiGapStatus" style="color: var(--text-muted);">Déficit vs Curva Oficial</span>
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
          <span style="color: var(--text-subtle);">Mês: R$ 54.7M</span>
        </div>
      </div>

      <!-- 6. Crescimento MoM -->
      <div class="kpi-card">
        <div class="kpi-title">
          <span>Evolução MoM (vs Ago)</span>
          <span>📈</span>
        </div>
        <div class="kpi-value" id="kpiMoMValue" style="color: var(--accent-emerald);">+17.1%</div>
        <div class="kpi-subtext">
          <span class="badge-trend trend-pos" id="kpiMoMBadge">+R$ 861.851</span>
          <span style="color: var(--text-subtle);">vs Ago/26 MTD</span>
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
              <div class="legend-bullet" style="background: var(--accent-cyan);"></div>
              <span>Realizado Diário</span>
            </div>
            <div class="legend-item">
              <div class="legend-bullet" style="background: rgba(255,255,255,0.3);"></div>
              <span>Meta Diária Oficial</span>
            </div>
            <div class="legend-item">
              <div class="legend-bullet" style="background: var(--accent-emerald);"></div>
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
        <div class="highlight-card" style="border-left: 3px solid var(--accent-emerald);">
          <div class="highlight-card-title" style="color: var(--accent-emerald);">
            <span>🚀 Top Linhas Superando a Meta</span>
          </div>
          <div class="highlight-list" id="listAceleradores">
            <!-- Renderizado via JS -->
          </div>
        </div>

        <!-- Detratores -->
        <div class="highlight-card" style="border-left: 3px solid var(--accent-rose);">
          <div class="highlight-card-title" style="color: var(--accent-rose);">
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
        <div class="table-nav-tabs">
          <button class="nav-tab-btn active" id="tabBtnGrupos" onclick="switchTableTab('grupos')">
            🏢 Grupos de Categorias
          </button>
          <button class="nav-tab-btn" id="tabBtnLinhas" onclick="switchTableTab('linhas')">
            📦 Linhas de Produtos (300)
          </button>
          <button class="nav-tab-btn" id="tabBtnSkus" onclick="switchTableTab('skus')">
            🏷️ Top SKUs (28.857 Itens)
          </button>
        </div>

        <div class="table-search-box">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
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

    <!-- Rodapé -->
    <footer class="footer">
      <div>
        Farmácias São João — Diretoria de E-commerce & Negócios Digitais
      </div>
      <div>
        Atualizado em: <span id="dataAtualizacao" style="font-family: 'JetBrains Mono', monospace;">-</span> | Base Qlik Sense Enterprise
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

    document.addEventListener('DOMContentLoaded', () => {{
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
      
      // Update Tab CSS
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
      document.querySelectorAll('.nav-tab-btn').forEach(btn => btn.classList.remove('active'));
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
      // App
      document.getElementById('tabSalesApp').textContent = fmtMoney(k.app.venda_mtd);
      document.getElementById('tabMetaApp').textContent = fmtMoney(k.app.meta_mtd);
      document.getElementById('badgeAtingApp').textContent = fmtPct(k.app.ating_mtd_pct) + (k.app.ating_mtd_pct >= 100 ? ' 🚀' : '');
      document.getElementById('tabGapApp').textContent = (k.app.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.app.gap_mtd);
      // Site
      document.getElementById('tabSalesSite').textContent = fmtMoney(k.site.venda_mtd);
      document.getElementById('tabMetaSite').textContent = fmtMoney(k.site.meta_mtd);
      document.getElementById('badgeAtingSite').textContent = fmtPct(k.site.ating_mtd_pct);
      document.getElementById('tabGapSite').textContent = (k.site.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.site.gap_mtd);
      // Marketplace
      document.getElementById('tabSalesMkt').textContent = fmtMoney(k.marketplace.venda_mtd);
      document.getElementById('tabMetaMkt').textContent = fmtMoney(k.marketplace.meta_mtd);
      document.getElementById('badgeAtingMkt').textContent = fmtPct(k.marketplace.ating_mtd_pct) + (k.marketplace.ating_mtd_pct >= 100 ? ' 🎯' : '');
      document.getElementById('tabGapMkt').textContent = (k.marketplace.gap_mtd >= 0 ? '+' : '') + fmtMoney(k.marketplace.gap_mtd);
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
        atingElem.style.color = 'var(--accent-emerald)';
        barElem.style.background = 'var(--accent-emerald)';
      }} else if (ating >= 90) {{
        atingElem.style.color = 'var(--accent-amber)';
        barElem.style.background = 'var(--accent-amber)';
      }} else {{
        atingElem.style.color = 'var(--accent-rose)';
        barElem.style.background = 'var(--accent-rose)';
      }}

      // GAP
      const gapElem = document.getElementById('kpiGapMtd');
      gapElem.textContent = (c.gap_mtd >= 0 ? '+' : '') + fmtMoney(c.gap_mtd);
      gapElem.style.color = c.gap_mtd >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)';
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
      momElem.style.color = mom >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)';
      document.getElementById('kpiMoMBadge').textContent = (c.crescimento_mom_diff >= 0 ? '+' : '') + fmtMoney(c.crescimento_mom_diff);
    }}

    function renderChart() {{
      const curva = window.DASHBOARD_DATA.curva_diaria;
      const ctx = document.getElementById('chartEvolucaoDiaria').getContext('2d');

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

      chartInstance = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: 'Realizado Diário',
              data: dataReal,
              backgroundColor: 'rgba(6, 182, 212, 0.85)',
              borderRadius: 4,
              order: 2
            }},
            {{
              label: 'Meta Diária Oficial',
              data: dataMeta,
              backgroundColor: 'rgba(255, 255, 255, 0.12)',
              borderRadius: 4,
              order: 3
            }},
            {{
              label: 'Meta Acumulada',
              data: dataMetaAcum,
              type: 'line',
              borderColor: 'rgba(255, 255, 255, 0.4)',
              borderDash: [5, 5],
              pointRadius: 0,
              yAxisID: 'yAcum',
              order: 1
            }},
            {{
              label: 'Realizado Acumulado',
              data: dataRealAcum,
              type: 'line',
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              tension: 0.3,
              pointRadius: 4,
              pointBackgroundColor: '#10b981',
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
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              titleColor: '#f8fafc',
              bodyColor: '#cbd5e1',
              borderColor: 'rgba(255,255,255,0.1)',
              borderWidth: 1,
              padding: 12,
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
              grid: {{ color: 'rgba(255, 255, 255, 0.04)' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}
            }},
            y: {{
              position: 'left',
              grid: {{ color: 'rgba(255, 255, 255, 0.04)' }},
              ticks: {{
                color: '#94a3b8',
                font: {{ size: 11 }},
                callback: v => (v / 1000).toFixed(0) + 'k'
              }}
            }},
            yAcum: {{
              position: 'right',
              grid: {{ display: false }},
              ticks: {{
                color: '#10b981',
                font: {{ size: 11 }},
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
            <div class="highlight-gap" style="color: var(--accent-emerald);">+${{fmtMoney(item.gap_mtd)}}</div>
            <div style="font-size: 11px; color: var(--text-subtle);">Venda: ${{fmtMoney(item.realizado_mtd)}}</div>
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
            <div class="highlight-gap" style="color: var(--accent-rose);">${{fmtMoney(item.gap_mtd)}}</div>
            <div style="font-size: 11px; color: var(--text-subtle);">Venda: ${{fmtMoney(item.realizado_mtd)}}</div>
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
            <td><strong>${{g.grupo}}</strong> <span style="font-size: 11px; color: var(--text-subtle);">(${{g.total_linhas}} linhas)</span></td>
            <td class="num-cell">${{fmtMoney(g.meta_mtd)}}</td>
            <td class="num-cell" style="font-weight: 700; color: var(--accent-cyan);">${{fmtMoney(g.realizado_mtd)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{g.ating_mtd_pct >= 100 ? 'trend-pos' : g.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                ${{fmtPct(g.ating_mtd_pct)}}
              </span>
            </td>
            <td class="num-cell" style="color: ${{isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)'}};">
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
            <td style="color: var(--text-muted); font-size: 12px;">${{l.grupo}}</td>
            <td class="num-cell">${{fmtMoney(l.meta_mtd)}}</td>
            <td class="num-cell" style="font-weight: 700; color: var(--accent-cyan);">${{fmtMoney(l.realizado_mtd)}}</td>
            <td class="num-cell">
              <span class="badge-trend ${{l.ating_mtd_pct >= 100 ? 'trend-pos' : l.ating_mtd_pct >= 90 ? 'trend-neutral' : 'trend-neg'}}">
                ${{fmtPct(l.ating_mtd_pct)}}
              </span>
            </td>
            <td class="num-cell" style="color: ${{isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)'}};">
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
          <td style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--accent-cyan);">${{s.id}}</td>
          <td><strong>${{s.nome}}</strong></td>
          <td style="color: var(--text-muted); font-size: 12px;">${{s.laboratorio}}</td>
          <td style="color: var(--text-subtle); font-size: 12px;">${{s.linha}}</td>
          <td class="num-cell" style="font-weight: 700; color: var(--accent-emerald);">${{fmtMoney(s.meta_mtd)}}</td>
          <td class="num-cell">${{fmtMoney(s.meta_app)}}</td>
          <td class="num-cell">${{fmtMoney(s.meta_site)}}</td>
          <td class="num-cell">${{fmtMoney(s.meta_mkt)}}</td>
          <td class="num-cell" style="color: var(--text-muted);">${{fmtMoney(s.meta_mensal)}}</td>
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

    print(f"✅ Dashboard Executivo compilado com sucesso em: {OUTPUT_HTML}")
    print(f"   Tamanho final do HTML: {os.path.getsize(OUTPUT_HTML) / 1024:.1f} KB")
    print(f"🎉 Compilação concluída em {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    build()
