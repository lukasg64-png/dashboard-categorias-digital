"""
process_digital_analytics.py — Motor Analítico de Consolidação Digital (Set/2026).
Cruza as Metas Diarizadas oficiais com o Realizado do Qlik Sense.
Calcula Desvios (Atingimento %, GAP R$ e Desvio %), Crescimento (MoM % e MoM R$),
Evolução (YoY % e YoY R$), Projeções de Fechamento e Curva Diária para:
- Total Digital
- App (App + App Tele Entrega)
- Site (Site + Site Tele Entrega)
- Marketplace (iFood + Ecommerce + Rappi)
Gera o pacote de dados final 'dashboard_digital_data.json'.
"""
import os, sys, time, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def clean_name(val):
    if pd.isna(val) or val is None or str(val).strip() in ('-', '', 'None'):
        return "OUTROS"
    return str(val).replace('\xa0', ' ').replace('\t', ' ').strip()

def map_channel_category(canal_name):
    c = str(canal_name).strip().upper()
    if c in ['APP', 'APP TELE ENTREGA']:
        return 'app'
    elif c in ['SITE', 'SITE TELE ENTREGA']:
        return 'site'
    elif c in ['IFOOD', 'E_COMMERCE', 'E-COMMERCE', 'ECOMMERCE', 'RAPPI', 'MERCADO LIVRE', 'PARCEIROS', 'SUPERFACIL']:
        return 'marketplace'
    else:
        return 'outros'

def calc_pct(num, den):
    if den and den > 0:
        return round((num / den) * 100.0, 2)
    return 0.0

def calc_desvio_pct(real, meta):
    if meta and meta > 0:
        return round(((real / meta) - 1.0) * 100.0, 2)
    return 0.0

def calc_growth(cur, prev):
    diff = cur - prev
    pct = (diff / prev * 100.0) if prev and prev > 0 else 0.0
    return round(pct, 2), round(diff, 2)

def main():
    t0 = time.time()
    print("=" * 70)
    print("  PROCESSAMENTO ANALÍTICO: METAS, DESVIOS, CRESCIMENTO & EVOLUÇÃO")
    print("=" * 70)

    # 1. Carregar Metas e Curva Diária
    with open(os.path.join(DATA_DIR, 'metas_resumo.json'), 'r', encoding='utf-8') as f:
        metas_resumo = json.load(f)

    with open(os.path.join(DATA_DIR, 'curva_diaria_digital.json'), 'r', encoding='utf-8') as f:
        curva_diaria = json.load(f)

    # 2. Carregar Dados Brutos do Qlik Sense
    qlik_raw_file = os.path.join(DATA_DIR, 'qlik_digital_raw.json')
    if not os.path.exists(qlik_raw_file):
        print("Arquivo qlik_digital_raw.json não encontrado. Executando extrator primeiro...")
        import extract_qlik_digital
        extract_qlik_digital.load_fallback_data()

    with open(qlik_raw_file, 'r', encoding='utf-8') as f:
        qlik_raw = json.load(f)

    max_dia = qlik_raw.get('maxDia', 3)
    if max_dia < 1: max_dia = 3
    print(f"Data de corte D-1 identificada: Dia {max_dia}/09/2026")

    pct_acum_dmax = curva_diaria[max_dia - 1]['pct_acum']
    print(f"Percentual acumulado da curva até o Dia {max_dia}: {pct_acum_dmax * 100:.2f}%")

    # 3. Processar Curva Diária de Vendas (Realizado x Meta)
    raw_canais_dia = qlik_raw.get('canais_dia', [])
    
    # Estrutura por Dia: total, app, site, marketplace (v26, v26_06, v25)
    daily_sales = defaultdict(lambda: {
        'total': 0.0, 'app': 0.0, 'site': 0.0, 'marketplace': 0.0,
        'v26_06_total': 0.0, 'v26_06_app': 0.0, 'v26_06_site': 0.0, 'v26_06_mkt': 0.0,
        'v25_total': 0.0, 'v25_app': 0.0, 'v25_site': 0.0, 'v25_mkt': 0.0
    })

    for r in raw_canais_dia:
        canal = r[0]
        dia = int(r[1]) if str(r[1]).isdigit() else 0
        v26 = float(r[2] or 0.0)
        v26_06 = float(r[3] or 0.0)
        v25 = float(r[4] or 0.0)

        cat = map_channel_category(canal)
        if cat != 'outros':
            daily_sales[dia]['total'] += v26
            daily_sales[dia][cat] += v26
            daily_sales[dia]['v26_06_total'] += v26_06
            daily_sales[dia]['v25_total'] += v25

            cat_key = 'mkt' if cat == 'marketplace' else cat
            daily_sales[dia][f'v26_06_{cat_key}'] += v26_06
            daily_sales[dia][f'v25_{cat_key}'] += v25

    # Construir tabela diária para gráficos
    curva_grafico = []
    real_acum_total = 0.0
    real_acum_app = 0.0
    real_acum_site = 0.0
    real_acum_mkt = 0.0

    meta_total_mensal = metas_resumo['metas']['total']
    meta_app_mensal = metas_resumo['metas']['app']
    meta_site_mensal = metas_resumo['metas']['site']
    meta_mkt_mensal = metas_resumo['metas']['marketplace']

    for item in curva_diaria:
        d = item['dia']
        pct_dia = item['pct_mes']
        pct_acum = item['pct_acum']

        m_dia_tot = item['meta_dia_total']
        m_acum_tot = item['meta_acum_total']
        m_dia_app = item['meta_dia_app']
        m_acum_app = item['meta_acum_app']
        m_dia_site = item['meta_dia_site']
        m_acum_site = item['meta_acum_site']
        m_dia_mkt = item['meta_dia_mkt']
        m_acum_mkt = item['meta_acum_mkt']

        ds = daily_sales.get(d, {'total': 0.0, 'app': 0.0, 'site': 0.0, 'marketplace': 0.0})
        is_realizado = (d <= max_dia)

        if is_realizado:
            real_acum_total += ds['total']
            real_acum_app += ds['app']
            real_acum_site += ds['site']
            real_acum_mkt += ds['marketplace']

        curva_grafico.append({
            'dia': d,
            'dow': item['dow'],
            'data': item['data'],
            'pct_mes': round(pct_dia * 100, 2),
            'pct_acum': round(pct_acum * 100, 2),
            'is_realizado': is_realizado,
            # Metas
            'meta_dia_total': m_dia_tot,
            'meta_acum_total': m_acum_tot,
            'meta_dia_app': m_dia_app,
            'meta_acum_app': m_acum_app,
            'meta_dia_site': m_dia_site,
            'meta_acum_site': m_acum_site,
            'meta_dia_mkt': m_dia_mkt,
            'meta_acum_mkt': m_acum_mkt,
            # Realizado
            'real_dia_total': round(ds['total'], 2) if is_realizado else None,
            'real_acum_total': round(real_acum_total, 2) if is_realizado else None,
            'real_dia_app': round(ds['app'], 2) if is_realizado else None,
            'real_acum_app': round(real_acum_app, 2) if is_realizado else None,
            'real_dia_site': round(ds['site'], 2) if is_realizado else None,
            'real_acum_site': round(real_acum_site, 2) if is_realizado else None,
            'real_dia_mkt': round(ds['marketplace'], 2) if is_realizado else None,
            'real_acum_mkt': round(real_acum_mkt, 2) if is_realizado else None,
            # Atingimento diário
            'ating_dia_total': calc_pct(ds['total'], m_dia_tot) if is_realizado else None,
            'ating_acum_total': calc_pct(real_acum_total, m_acum_tot) if is_realizado else None,
            # Desvio % e GAP R$ diários vs Meta (Solicitado pelo usuário)
            'desvio_dia_total': calc_desvio_pct(ds['total'], m_dia_tot) if is_realizado else None,
            'desvio_dia_app': calc_desvio_pct(ds['app'], m_dia_app) if is_realizado else None,
            'desvio_dia_site': calc_desvio_pct(ds['site'], m_dia_site) if is_realizado else None,
            'desvio_dia_mkt': calc_desvio_pct(ds['marketplace'], m_dia_mkt) if is_realizado else None,
            'gap_dia_total': round(ds['total'] - m_dia_tot, 2) if is_realizado else None,
            'gap_dia_app': round(ds['app'] - m_dia_app, 2) if is_realizado else None,
            'gap_dia_site': round(ds['site'] - m_dia_site, 2) if is_realizado else None,
            'gap_dia_mkt': round(ds['marketplace'] - m_dia_mkt, 2) if is_realizado else None
        })

    # 4. Totais Executivos MTD & Projeções
    meta_total_mtd = meta_total_mensal * pct_acum_dmax
    meta_app_mtd = meta_app_mensal * pct_acum_dmax
    meta_site_mtd = meta_site_mensal * pct_acum_dmax
    meta_mkt_mtd = meta_mkt_mensal * pct_acum_dmax

    # Histórico comparativo MTD Total
    v26_06_mtd_tot = sum(daily_sales[d]['v26_06_total'] for d in range(1, max_dia + 1))
    v25_mtd_tot = sum(daily_sales[d]['v25_total'] for d in range(1, max_dia + 1))

    # Histórico comparativo por canal
    v26_06_mtd_app = sum(daily_sales[d]['v26_06_app'] for d in range(1, max_dia + 1))
    v25_mtd_app = sum(daily_sales[d]['v25_app'] for d in range(1, max_dia + 1))

    v26_06_mtd_site = sum(daily_sales[d]['v26_06_site'] for d in range(1, max_dia + 1))
    v25_mtd_site = sum(daily_sales[d]['v25_site'] for d in range(1, max_dia + 1))

    v26_06_mtd_mkt = sum(daily_sales[d]['v26_06_mkt'] for d in range(1, max_dia + 1))
    v25_mtd_mkt = sum(daily_sales[d]['v25_mkt'] for d in range(1, max_dia + 1))

    # Projeção de Fechamento (Run Rate ponderado pela curva oficial)
    proj_total = (real_acum_total / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0
    proj_app = (real_acum_app / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0
    proj_site = (real_acum_site / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0
    proj_mkt = (real_acum_mkt / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0

    # Crescimentos MoM e YoY
    yoy_pct_tot, yoy_diff_tot = calc_growth(real_acum_total, v25_mtd_tot)
    mom_pct_tot, mom_diff_tot = calc_growth(real_acum_total, v26_06_mtd_tot)

    yoy_pct_app, yoy_diff_app = calc_growth(real_acum_app, v25_mtd_app)
    mom_pct_app, mom_diff_app = calc_growth(real_acum_app, v26_06_mtd_app)

    yoy_pct_site, yoy_diff_site = calc_growth(real_acum_site, v25_mtd_site)
    mom_pct_site, mom_diff_site = calc_growth(real_acum_site, v26_06_mtd_site)

    yoy_pct_mkt, yoy_diff_mkt = calc_growth(real_acum_mkt, v25_mtd_mkt)
    mom_pct_mkt, mom_diff_mkt = calc_growth(real_acum_mkt, v26_06_mtd_mkt)

    gap_mtd_tot = round(real_acum_total - meta_total_mtd, 2)
    gap_mtd_app = round(real_acum_app - meta_app_mtd, 2)
    gap_mtd_site = round(real_acum_site - meta_site_mtd, 2)
    gap_mtd_mkt = round(real_acum_mkt - meta_mkt_mtd, 2)

    kpis_executivos = {
        'data_corte': f"01 a {max_dia:02d}/09/2026 (D-1)",
        'max_dia': max_dia,
        'pct_tempo_mes': round(max_dia / 30 * 100, 1),
        'pct_curva_acum': round(pct_acum_dmax * 100, 2),
        'canais': {
            'total': {
                'id': 'total',
                'nome': 'Total Digital',
                'icone': '🌐',
                'venda_mtd': round(real_acum_total, 2),
                'meta_mtd': round(meta_total_mtd, 2),
                'meta_mensal': round(meta_total_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_total, meta_total_mtd),
                'gap_mtd': gap_mtd_tot,
                'desvio_pct': calc_desvio_pct(real_acum_total, meta_total_mtd),
                'ating_mensal_pct': calc_pct(real_acum_total, meta_total_mensal),
                'projecao_fechamento': round(proj_total, 2),
                'ating_proj_pct': calc_pct(proj_total, meta_total_mensal),
                'gap_projecao': round(proj_total - meta_total_mensal, 2),
                'share_realizado_pct': 100.0,
                'share_meta_pct': 100.0,
                'v26_06_mtd': round(v26_06_mtd_tot, 2),
                'crescimento_mom_pct': mom_pct_tot,
                'crescimento_mom_diff': mom_diff_tot,
                'v25_mtd': round(v25_mtd_tot, 2),
                'crescimento_yoy_pct': yoy_pct_tot,
                'crescimento_yoy_diff': yoy_diff_tot
            },
            'app': {
                'id': 'app',
                'nome': 'App',
                'icone': '📱',
                'venda_mtd': round(real_acum_app, 2),
                'meta_mtd': round(meta_app_mtd, 2),
                'meta_mensal': round(meta_app_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_app, meta_app_mtd),
                'gap_mtd': gap_mtd_app,
                'desvio_pct': calc_desvio_pct(real_acum_app, meta_app_mtd),
                'ating_mensal_pct': calc_pct(real_acum_app, meta_app_mensal),
                'projecao_fechamento': round(proj_app, 2),
                'ating_proj_pct': calc_pct(proj_app, meta_app_mensal),
                'gap_projecao': round(proj_app - meta_app_mensal, 2),
                'share_realizado_pct': calc_pct(real_acum_app, real_acum_total),
                'share_meta_pct': metas_resumo['shares']['app'],
                'v26_06_mtd': round(v26_06_mtd_app, 2),
                'crescimento_mom_pct': mom_pct_app,
                'crescimento_mom_diff': mom_diff_app,
                'v25_mtd': round(v25_mtd_app, 2),
                'crescimento_yoy_pct': yoy_pct_app,
                'crescimento_yoy_diff': yoy_diff_app
            },
            'site': {
                'id': 'site',
                'nome': 'Site',
                'icone': '💻',
                'venda_mtd': round(real_acum_site, 2),
                'meta_mtd': round(meta_site_mtd, 2),
                'meta_mensal': round(meta_site_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_site, meta_site_mtd),
                'gap_mtd': gap_mtd_site,
                'desvio_pct': calc_desvio_pct(real_acum_site, meta_site_mtd),
                'ating_mensal_pct': calc_pct(real_acum_site, meta_site_mensal),
                'projecao_fechamento': round(proj_site, 2),
                'ating_proj_pct': calc_pct(proj_site, meta_site_mensal),
                'gap_projecao': round(proj_site - meta_site_mensal, 2),
                'share_realizado_pct': calc_pct(real_acum_site, real_acum_total),
                'share_meta_pct': metas_resumo['shares']['site'],
                'v26_06_mtd': round(v26_06_mtd_site, 2),
                'crescimento_mom_pct': mom_pct_site,
                'crescimento_mom_diff': mom_diff_site,
                'v25_mtd': round(v25_mtd_site, 2),
                'crescimento_yoy_pct': yoy_pct_site,
                'crescimento_yoy_diff': yoy_diff_site
            },
            'marketplace': {
                'id': 'marketplace',
                'nome': 'Marketplace',
                'icone': '🛍️',
                'venda_mtd': round(real_acum_mkt, 2),
                'meta_mtd': round(meta_mkt_mtd, 2),
                'meta_mensal': round(meta_mkt_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_mkt, meta_mkt_mtd),
                'gap_mtd': gap_mtd_mkt,
                'desvio_pct': calc_desvio_pct(real_acum_mkt, meta_mkt_mtd),
                'ating_mensal_pct': calc_pct(real_acum_mkt, meta_mkt_mensal),
                'projecao_fechamento': round(proj_mkt, 2),
                'ating_proj_pct': calc_pct(proj_mkt, meta_mkt_mensal),
                'gap_projecao': round(proj_mkt - meta_mkt_mensal, 2),
                'share_realizado_pct': calc_pct(real_acum_mkt, real_acum_total),
                'share_meta_pct': metas_resumo['shares']['marketplace'],
                'v26_06_mtd': round(v26_06_mtd_mkt, 2),
                'crescimento_mom_pct': mom_pct_mkt,
                'crescimento_mom_diff': mom_diff_mkt,
                'v25_mtd': round(v25_mtd_mkt, 2),
                'crescimento_yoy_pct': yoy_pct_mkt,
                'crescimento_yoy_diff': yoy_diff_mkt
            }
        }
    }

    # Tabela Executiva de Canais (Resumo Comparativo Consolidado)
    canais_tabela = [
        kpis_executivos['canais']['total'],
        kpis_executivos['canais']['app'],
        kpis_executivos['canais']['marketplace'],
        kpis_executivos['canais']['site']
    ]

    print("\n--- RESUMO DE PERFORMANCE MTD (01 a {:02d}/09) ---".format(max_dia))
    for c in canais_tabela:
        print(f"  {c['nome']:15s}: Realizado: R$ {c['venda_mtd']:11,.2f} | Meta MTD: R$ {c['meta_mtd']:11,.2f} | Ating: {c['ating_mtd_pct']:6.1f}% | Desvio R$: R$ {c['gap_mtd']:+11,.2f} | MoM: {c['crescimento_mom_pct']:+5.1f}% | YoY: {c['crescimento_yoy_pct']:+5.1f}%")

    # 5. Processar Hierarquia por Linha
    with open(os.path.join(DATA_DIR, 'metas_por_linha.json'), 'r', encoding='utf-8') as f:
        metas_linhas_raw = json.load(f)

    metas_linha_map = {}
    for l in metas_linhas_raw:
        grp = clean_name(l['Desc_Grupo'])
        sub = clean_name(l['Desc_Subgrupo'])
        lin = clean_name(l['Desc_Linha'])
        key = (grp, sub, lin)
        metas_linha_map[key] = {
            'meta_mensal_total': l['Total_Digital'],
            'meta_mensal_app': l['App'],
            'meta_mensal_site': l['Site'],
            'meta_mensal_mkt': l['Marketplace'],
            'meta_mtd_total': round(l['Total_Digital'] * pct_acum_dmax, 2),
            'meta_mtd_app': round(l['App'] * pct_acum_dmax, 2),
            'meta_mtd_site': round(l['Site'] * pct_acum_dmax, 2),
            'meta_mtd_mkt': round(l['Marketplace'] * pct_acum_dmax, 2)
        }

    raw_hier = qlik_raw.get('hierarquia', [])
    real_linha_map = defaultdict(lambda: {
        'v26_total': 0.0, 'v26_app': 0.0, 'v26_site': 0.0, 'v26_mkt': 0.0,
        'v26_06_total': 0.0, 'v26_06_app': 0.0, 'v26_06_site': 0.0, 'v26_06_mkt': 0.0,
        'v25_total': 0.0, 'v25_app': 0.0, 'v25_site': 0.0, 'v25_mkt': 0.0
    })

    for r in raw_hier:
        canal = r[0]
        grp = clean_name(r[1])
        sub = clean_name(r[2])
        lin = clean_name(r[3])
        v26 = float(r[4] or 0.0)
        v26_06 = float(r[5] or 0.0)
        v25 = float(r[6] or 0.0)

        cat = map_channel_category(canal)
        if cat != 'outros':
            c_key = 'mkt' if cat == 'marketplace' else cat
            key = (grp, sub, lin)
            real_linha_map[key]['v26_total'] += v26
            real_linha_map[key][f'v26_{c_key}'] += v26
            real_linha_map[key]['v26_06_total'] += v26_06
            real_linha_map[key][f'v26_06_{c_key}'] += v26_06
            real_linha_map[key]['v25_total'] += v25
            real_linha_map[key][f'v25_{c_key}'] += v25

    all_keys = set(metas_linha_map.keys()).union(set(real_linha_map.keys()))
    tabela_linhas = []

    for key in all_keys:
        grp, sub, lin = key
        m = metas_linha_map.get(key, {
            'meta_mensal_total': 0.0, 'meta_mensal_app': 0.0, 'meta_mensal_site': 0.0, 'meta_mensal_mkt': 0.0,
            'meta_mtd_total': 0.0, 'meta_mtd_app': 0.0, 'meta_mtd_site': 0.0, 'meta_mtd_mkt': 0.0
        })
        rv = real_linha_map.get(key, {
            'v26_total': 0.0, 'v26_app': 0.0, 'v26_site': 0.0, 'v26_mkt': 0.0,
            'v26_06_total': 0.0, 'v26_06_app': 0.0, 'v26_06_site': 0.0, 'v26_06_mkt': 0.0,
            'v25_total': 0.0, 'v25_app': 0.0, 'v25_site': 0.0, 'v25_mkt': 0.0
        })

        # Função auxiliar para consolidar cada canal
        def build_metric_block(real, meta_mtd, meta_mes, v26_06, v25):
            gap_rs = round(real - meta_mtd, 2)
            ating_pct = calc_pct(real, meta_mtd)
            desvio_pct = calc_desvio_pct(real, meta_mtd)
            proj = round((real / pct_acum_dmax), 2) if pct_acum_dmax > 0 else 0.0
            mom_pct, mom_diff = calc_growth(real, v26_06)
            yoy_pct, yoy_diff = calc_growth(real, v25)
            return {
                'realizado_mtd': round(real, 2),
                'meta_mtd': round(meta_mtd, 2),
                'meta_mensal': round(meta_mes, 2),
                'gap_mtd': gap_rs,
                'desvio_pct': desvio_pct,
                'ating_mtd_pct': ating_pct,
                'projecao_fechamento': proj,
                'v26_06_mtd': round(v26_06, 2),
                'crescimento_mom_pct': mom_pct,
                'crescimento_mom_diff': mom_diff,
                'v25_mtd': round(v25, 2),
                'crescimento_yoy_pct': yoy_pct,
                'crescimento_yoy_diff': yoy_diff
            }

        canais_linha = {
            'total': build_metric_block(rv['v26_total'], m['meta_mtd_total'], m['meta_mensal_total'], rv['v26_06_total'], rv['v25_total']),
            'app': build_metric_block(rv['v26_app'], m['meta_mtd_app'], m['meta_mensal_app'], rv['v26_06_app'], rv['v25_app']),
            'site': build_metric_block(rv['v26_site'], m['meta_mtd_site'], m['meta_mensal_site'], rv['v26_06_site'], rv['v25_site']),
            'marketplace': build_metric_block(rv['v26_mkt'], m['meta_mtd_mkt'], m['meta_mensal_mkt'], rv['v26_06_mkt'], rv['v25_mkt'])
        }

        tabela_linhas.append({
            'grupo': grp,
            'subgrupo': sub,
            'linha': lin,
            'canais': canais_linha,
            # Flat attributes defaults (Total) for direct access
            'meta_mensal': canais_linha['total']['meta_mensal'],
            'meta_mtd': canais_linha['total']['meta_mtd'],
            'realizado_mtd': canais_linha['total']['realizado_mtd'],
            'realizado_app': canais_linha['app']['realizado_mtd'],
            'realizado_site': canais_linha['site']['realizado_mtd'],
            'realizado_mkt': canais_linha['marketplace']['realizado_mtd'],
            'gap_mtd': canais_linha['total']['gap_mtd'],
            'desvio_pct': canais_linha['total']['desvio_pct'],
            'ating_mtd_pct': canais_linha['total']['ating_mtd_pct'],
            'projecao_fechamento': canais_linha['total']['projecao_fechamento'],
            'crescimento_mom_pct': canais_linha['total']['crescimento_mom_pct'],
            'crescimento_mom_diff': canais_linha['total']['crescimento_mom_diff'],
            'crescimento_yoy_pct': canais_linha['total']['crescimento_yoy_pct'],
            'crescimento_yoy_diff': canais_linha['total']['crescimento_yoy_diff']
        })

    tabela_linhas.sort(key=lambda x: x['realizado_mtd'], reverse=True)
    print(f"Total de Linhas processadas: {len(tabela_linhas):,}")

    # 6. Agregações por Grupo com suporte a canais
    grupos_dict = defaultdict(lambda: {
        'total': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'app': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'site': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'marketplace': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'total_linhas': 0
    })

    for l in tabela_linhas:
        g = l['grupo']
        grupos_dict[g]['total_linhas'] += 1
        for ch in ['total', 'app', 'site', 'marketplace']:
            b = l['canais'][ch]
            grupos_dict[g][ch]['real'] += b['realizado_mtd']
            grupos_dict[g][ch]['meta_mtd'] += b['meta_mtd']
            grupos_dict[g][ch]['meta_mes'] += b['meta_mensal']
            grupos_dict[g][ch]['v26_06'] += b['v26_06_mtd']
            grupos_dict[g][ch]['v25'] += b['v25_mtd']

    tabela_grupos = []
    for g, val in grupos_dict.items():
        canais_grupo = {}
        for ch in ['total', 'app', 'site', 'marketplace']:
            r = val[ch]['real']
            m_mtd = val[ch]['meta_mtd']
            m_mes = val[ch]['meta_mes']
            v06 = val[ch]['v26_06']
            v25 = val[ch]['v25']
            
            gap_rs = round(r - m_mtd, 2)
            ating = calc_pct(r, m_mtd)
            desvio = calc_desvio_pct(r, m_mtd)
            proj = round(r / pct_acum_dmax, 2) if pct_acum_dmax > 0 else 0.0
            mom_pct, mom_diff = calc_growth(r, v06)
            yoy_pct, yoy_diff = calc_growth(r, v25)
            ch_total_real = kpis_executivos['canais'][ch]['venda_mtd']
            share = calc_pct(r, ch_total_real)

            canais_grupo[ch] = {
                'realizado_mtd': round(r, 2),
                'meta_mtd': round(m_mtd, 2),
                'meta_mensal': round(m_mes, 2),
                'gap_mtd': gap_rs,
                'desvio_pct': desvio,
                'ating_mtd_pct': ating,
                'projecao_fechamento': proj,
                'v26_06_mtd': round(v06, 2),
                'crescimento_mom_pct': mom_pct,
                'crescimento_mom_diff': mom_diff,
                'v25_mtd': round(v25, 2),
                'crescimento_yoy_pct': yoy_pct,
                'crescimento_yoy_diff': yoy_diff,
                'share_pct': share
            }

        tot = canais_grupo['total']
        tabela_grupos.append({
            'grupo': g,
            'total_linhas': val['total_linhas'],
            'canais': canais_grupo,
            # Flat attributes
            'realizado_mtd': tot['realizado_mtd'],
            'meta_mtd': tot['meta_mtd'],
            'meta_mensal': tot['meta_mensal'],
            'gap_mtd': tot['gap_mtd'],
            'desvio_pct': tot['desvio_pct'],
            'ating_mtd_pct': tot['ating_mtd_pct'],
            'projecao_fechamento': tot['projecao_fechamento'],
            'realizado_app': canais_grupo['app']['realizado_mtd'],
            'realizado_site': canais_grupo['site']['realizado_mtd'],
            'realizado_mkt': canais_grupo['marketplace']['realizado_mtd'],
            'crescimento_mom_pct': tot['crescimento_mom_pct'],
            'crescimento_mom_diff': tot['crescimento_mom_diff'],
            'crescimento_yoy_pct': tot['crescimento_yoy_pct'],
            'crescimento_yoy_diff': tot['crescimento_yoy_diff'],
            'share_pct': tot['share_pct']
        })

    tabela_grupos.sort(key=lambda x: x['realizado_mtd'], reverse=True)

    # 7. Agregações por Subgrupo com suporte a canais
    subgrupos_dict = defaultdict(lambda: {
        'grupo': '',
        'total': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'app': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'site': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'marketplace': {'real': 0.0, 'meta_mtd': 0.0, 'meta_mes': 0.0, 'v26_06': 0.0, 'v25': 0.0},
        'total_linhas': 0
    })

    for l in tabela_linhas:
        sub = l['subgrupo']
        grp = l['grupo']
        subgrupos_dict[sub]['grupo'] = grp
        subgrupos_dict[sub]['total_linhas'] += 1
        for ch in ['total', 'app', 'site', 'marketplace']:
            b = l['canais'][ch]
            subgrupos_dict[sub][ch]['real'] += b['realizado_mtd']
            subgrupos_dict[sub][ch]['meta_mtd'] += b['meta_mtd']
            subgrupos_dict[sub][ch]['meta_mes'] += b['meta_mensal']
            subgrupos_dict[sub][ch]['v26_06'] += b['v26_06_mtd']
            subgrupos_dict[sub][ch]['v25'] += b['v25_mtd']

    tabela_subgrupos = []
    for sub, val in subgrupos_dict.items():
        canais_sub = {}
        for ch in ['total', 'app', 'site', 'marketplace']:
            r = val[ch]['real']
            m_mtd = val[ch]['meta_mtd']
            m_mes = val[ch]['meta_mes']
            v06 = val[ch]['v26_06']
            v25 = val[ch]['v25']

            gap_rs = round(r - m_mtd, 2)
            ating = calc_pct(r, m_mtd)
            desvio = calc_desvio_pct(r, m_mtd)
            proj = round(r / pct_acum_dmax, 2) if pct_acum_dmax > 0 else 0.0
            mom_pct, mom_diff = calc_growth(r, v06)
            yoy_pct, yoy_diff = calc_growth(r, v25)
            ch_total_real = kpis_executivos['canais'][ch]['venda_mtd']
            share = calc_pct(r, ch_total_real)

            canais_sub[ch] = {
                'realizado_mtd': round(r, 2),
                'meta_mtd': round(m_mtd, 2),
                'meta_mensal': round(m_mes, 2),
                'gap_mtd': gap_rs,
                'desvio_pct': desvio,
                'ating_mtd_pct': ating,
                'projecao_fechamento': proj,
                'v26_06_mtd': round(v06, 2),
                'crescimento_mom_pct': mom_pct,
                'crescimento_mom_diff': mom_diff,
                'v25_mtd': round(v25, 2),
                'crescimento_yoy_pct': yoy_pct,
                'crescimento_yoy_diff': yoy_diff,
                'share_pct': share
            }

        tot = canais_sub['total']
        tabela_subgrupos.append({
            'grupo': val['grupo'],
            'subgrupo': sub,
            'total_linhas': val['total_linhas'],
            'canais': canais_sub,
            'realizado_mtd': tot['realizado_mtd'],
            'meta_mtd': tot['meta_mtd'],
            'meta_mensal': tot['meta_mensal'],
            'gap_mtd': tot['gap_mtd'],
            'desvio_pct': tot['desvio_pct'],
            'ating_mtd_pct': tot['ating_mtd_pct'],
            'projecao_fechamento': tot['projecao_fechamento'],
            'realizado_app': canais_sub['app']['realizado_mtd'],
            'realizado_site': canais_sub['site']['realizado_mtd'],
            'realizado_mkt': canais_sub['marketplace']['realizado_mtd'],
            'crescimento_mom_pct': tot['crescimento_mom_pct'],
            'crescimento_mom_diff': tot['crescimento_mom_diff'],
            'crescimento_yoy_pct': tot['crescimento_yoy_pct'],
            'crescimento_yoy_diff': tot['crescimento_yoy_diff'],
            'share_pct': tot['share_pct']
        })
    tabela_subgrupos.sort(key=lambda x: x['realizado_mtd'], reverse=True)
    print(f"Total de Subgrupos processados: {len(tabela_subgrupos):,}")

    # 8. Fornecedores / Laboratórios com suporte a canais
    with open(os.path.join(DATA_DIR, 'metas_por_laboratorio.json'), 'r', encoding='utf-8') as f:
        metas_labs_list = json.load(f)
    metas_labs_map = {clean_name(r['Laboratorio']): r for r in metas_labs_list}

    qlik_labs_file = os.path.join(DATA_DIR, 'qlik_laboratorios_raw.json')
    labs_raw = []
    if os.path.exists(qlik_labs_file):
        with open(qlik_labs_file, 'r', encoding='utf-8') as f:
            labs_raw = json.load(f)
    elif 'laboratorios' in qlik_raw:
        labs_raw = qlik_raw['laboratorios']

    # Estrutura acumulada de laboratórios
    lab_real = defaultdict(lambda: {
        'total': {'real': 0.0, 'v06': 0.0, 'v25': 0.0},
        'app': {'real': 0.0, 'v06': 0.0, 'v25': 0.0},
        'site': {'real': 0.0, 'v06': 0.0, 'v25': 0.0},
        'marketplace': {'real': 0.0, 'v06': 0.0, 'v25': 0.0}
    })

    for r in labs_raw:
        canal = r[0]
        lab = clean_name(r[1])
        v26 = float(r[2] or 0.0)
        v26_06 = float(r[3] or 0.0)
        v25 = float(r[4] or 0.0)
        cat = map_channel_category(canal)
        if cat != 'outros':
            lab_real[lab][cat]['real'] += v26
            lab_real[lab][cat]['v06'] += v26_06
            lab_real[lab][cat]['v25'] += v25
            lab_real[lab]['total']['real'] += v26
            lab_real[lab]['total']['v06'] += v26_06
            lab_real[lab]['total']['v25'] += v25

    # Distribuição Marketplace via SKU / Linha mapping
    parquet_path = os.path.join(DATA_DIR, 'metas_digital_completa.parquet')
    if os.path.exists(parquet_path):
        df_meta = pd.read_parquet(parquet_path)
        linha_lab_mkt = df_meta.groupby(['Desc_Linha', 'Laboratorio'])['Marketplace'].sum().reset_index()
        linha_tot_mkt = df_meta.groupby('Desc_Linha')['Marketplace'].sum().reset_index().rename(columns={'Marketplace': 'Tot_Mkt'})
        linha_weights = pd.merge(linha_lab_mkt, linha_tot_mkt, on='Desc_Linha')
        linha_weights['weight'] = linha_weights['Marketplace'] / linha_weights['Tot_Mkt']
        linha_weights = linha_weights[linha_weights['weight'] > 0]
        w_dict = defaultdict(dict)
        for _, row in linha_weights.iterrows():
            w_dict[clean_name(row['Desc_Linha'])][clean_name(row['Laboratorio'])] = row['weight']

        for r in raw_hier:
            c = map_channel_category(r[0])
            if c == 'marketplace':
                lin = clean_name(r[3])
                v26 = float(r[4] or 0.0)
                v26_06 = float(r[5] or 0.0)
                v25 = float(r[6] or 0.0)
                if lin in w_dict:
                    for lab, w in w_dict[lin].items():
                        lab_real[lab]['marketplace']['real'] += v26 * w
                        lab_real[lab]['marketplace']['v06'] += v26_06 * w
                        lab_real[lab]['marketplace']['v25'] += v25 * w
                        lab_real[lab]['total']['real'] += v26 * w
                        lab_real[lab]['total']['v06'] += v26_06 * w
                        lab_real[lab]['total']['v25'] += v25 * w

    all_labs_keys = set(metas_labs_map.keys()).union(set(lab_real.keys()))
    tabela_laboratorios = []
    meta_keys = {'total': 'Total_Digital', 'app': 'App', 'site': 'Site', 'marketplace': 'Marketplace'}
    
    for lab in all_labs_keys:
        m = metas_labs_map.get(lab, {'Total_Digital': 0.0, 'App': 0.0, 'Site': 0.0, 'Marketplace': 0.0})
        rv = lab_real.get(lab, {
            'total': {'real': 0.0, 'v06': 0.0, 'v25': 0.0},
            'app': {'real': 0.0, 'v06': 0.0, 'v25': 0.0},
            'site': {'real': 0.0, 'v06': 0.0, 'v25': 0.0},
            'marketplace': {'real': 0.0, 'v06': 0.0, 'v25': 0.0}
        })
        
        canais_lab = {}
        for ch in ['total', 'app', 'site', 'marketplace']:
            r = rv[ch]['real']
            m_mes = float(m.get(meta_keys[ch], 0.0) or 0.0)
            m_mtd = round(m_mes * pct_acum_dmax, 2)
            v06 = rv[ch]['v06']
            v25 = rv[ch]['v25']
            gap_rs = round(r - m_mtd, 2)
            ating = calc_pct(r, m_mtd)
            desvio = calc_desvio_pct(r, m_mtd)
            proj = round(r / pct_acum_dmax, 2) if pct_acum_dmax > 0 else 0.0
            mom_pct, mom_diff = calc_growth(r, v06)
            yoy_pct, yoy_diff = calc_growth(r, v25)
            ch_total_real = kpis_executivos['canais'][ch]['venda_mtd']
            share = calc_pct(r, ch_total_real)

            canais_lab[ch] = {
                'realizado_mtd': round(r, 2),
                'meta_mtd': round(m_mtd, 2),
                'meta_mensal': round(m_mes, 2),
                'gap_mtd': gap_rs,
                'desvio_pct': desvio,
                'ating_mtd_pct': ating,
                'projecao_fechamento': proj,
                'v26_06_mtd': round(v06, 2),
                'crescimento_mom_pct': mom_pct,
                'crescimento_mom_diff': mom_diff,
                'v25_mtd': round(v25, 2),
                'crescimento_yoy_pct': yoy_pct,
                'crescimento_yoy_diff': yoy_diff,
                'share_pct': share
            }

        tot = canais_lab['total']
        if tot['realizado_mtd'] > 0 or tot['meta_mtd'] > 0:
            tabela_laboratorios.append({
                'laboratorio': lab,
                'canais': canais_lab,
                'realizado_mtd': tot['realizado_mtd'],
                'meta_mtd': tot['meta_mtd'],
                'meta_mensal': tot['meta_mensal'],
                'gap_mtd': tot['gap_mtd'],
                'desvio_pct': tot['desvio_pct'],
                'ating_mtd_pct': tot['ating_mtd_pct'],
                'projecao_fechamento': tot['projecao_fechamento'],
                'realizado_app': canais_lab['app']['realizado_mtd'],
                'realizado_site': canais_lab['site']['realizado_mtd'],
                'realizado_mkt': canais_lab['marketplace']['realizado_mtd'],
                'crescimento_mom_pct': tot['crescimento_mom_pct'],
                'crescimento_mom_diff': tot['crescimento_mom_diff'],
                'crescimento_yoy_pct': tot['crescimento_yoy_pct'],
                'crescimento_yoy_diff': tot['crescimento_yoy_diff'],
                'share_pct': tot['share_pct']
            })
    tabela_laboratorios.sort(key=lambda x: x['realizado_mtd'], reverse=True)
    print(f"Total de Laboratórios processados: {len(tabela_laboratorios):,}")

    # 9. Top SKUs (500)
    with open(os.path.join(DATA_DIR, 'metas_top_skus.json'), 'r', encoding='utf-8') as f:
        top_skus_raw = json.load(f)

    top_skus_processados = []
    for sk in top_skus_raw[:500]:
        m_tot = sk.get('Total_Digital', 0.0)
        m_app = sk.get('App', 0.0)
        m_site = sk.get('Site', 0.0)
        m_mkt = sk.get('Marketplace', 0.0)

        top_skus_processados.append({
            'id': sk.get('Produto_ID'),
            'nome': sk.get('Desc_Produto'),
            'grupo': sk.get('Desc_Grupo'),
            'subgrupo': sk.get('Desc_Subgrupo'),
            'linha': sk.get('Desc_Linha'),
            'laboratorio': sk.get('Laboratorio'),
            # Total
            'meta_mensal': round(m_tot, 2),
            'meta_mtd': round(m_tot * pct_acum_dmax, 2),
            # App
            'meta_mensal_app': round(m_app, 2),
            'meta_mtd_app': round(m_app * pct_acum_dmax, 2),
            # Site
            'meta_mensal_site': round(m_site, 2),
            'meta_mtd_site': round(m_site * pct_acum_dmax, 2),
            # Marketplace
            'meta_mensal_mkt': round(m_mkt, 2),
            'meta_mtd_mkt': round(m_mkt * pct_acum_dmax, 2)
        })

    # 10. Diagnóstico de Causa-Raiz (Raio-X de Problemas vs Aceleradores por Canal)
    diagnostico_causas = {}
    for ch in ['total', 'app', 'site', 'marketplace']:
        # Fornecedores
        labs_validos = [l for l in tabela_laboratorios if l['canais'][ch]['meta_mtd'] > 500 or l['canais'][ch]['realizado_mtd'] > 500]
        det_labs = sorted(labs_validos, key=lambda x: x['canais'][ch]['gap_mtd'])[:15]
        acel_labs = sorted(labs_validos, key=lambda x: x['canais'][ch]['gap_mtd'], reverse=True)[:15]

        # Subgrupos
        subs_validos = [s for s in tabela_subgrupos if s['canais'][ch]['meta_mtd'] > 500 or s['canais'][ch]['realizado_mtd'] > 500]
        det_subs = sorted(subs_validos, key=lambda x: x['canais'][ch]['gap_mtd'])[:15]
        acel_subs = sorted(subs_validos, key=lambda x: x['canais'][ch]['gap_mtd'], reverse=True)[:15]

        # Linhas
        lins_validas = [l for l in tabela_linhas if l['canais'][ch]['meta_mtd'] > 500 or l['canais'][ch]['realizado_mtd'] > 500]
        det_lins = sorted(lins_validas, key=lambda x: x['canais'][ch]['gap_mtd'])[:15]
        acel_lins = sorted(lins_validas, key=lambda x: x['canais'][ch]['gap_mtd'], reverse=True)[:15]

        diagnostico_causas[ch] = {
            'detratores_laboratorios': [{
                'nome': x['laboratorio'],
                'realizado_mtd': x['canais'][ch]['realizado_mtd'],
                'meta_mtd': x['canais'][ch]['meta_mtd'],
                'gap_mtd': x['canais'][ch]['gap_mtd'],
                'desvio_pct': x['canais'][ch]['desvio_pct'],
                'ating_mtd_pct': x['canais'][ch]['ating_mtd_pct'],
                'crescimento_mom_pct': x['canais'][ch]['crescimento_mom_pct'],
                'crescimento_yoy_pct': x['canais'][ch]['crescimento_yoy_pct']
            } for x in det_labs],
            'aceleradores_laboratorios': [{
                'nome': x['laboratorio'],
                'realizado_mtd': x['canais'][ch]['realizado_mtd'],
                'meta_mtd': x['canais'][ch]['meta_mtd'],
                'gap_mtd': x['canais'][ch]['gap_mtd'],
                'desvio_pct': x['canais'][ch]['desvio_pct'],
                'ating_mtd_pct': x['canais'][ch]['ating_mtd_pct'],
                'crescimento_mom_pct': x['canais'][ch]['crescimento_mom_pct'],
                'crescimento_yoy_pct': x['canais'][ch]['crescimento_yoy_pct']
            } for x in acel_labs],
            'detratores_subgrupos': [{
                'nome': x['subgrupo'],
                'grupo': x['grupo'],
                'realizado_mtd': x['canais'][ch]['realizado_mtd'],
                'meta_mtd': x['canais'][ch]['meta_mtd'],
                'gap_mtd': x['canais'][ch]['gap_mtd'],
                'desvio_pct': x['canais'][ch]['desvio_pct'],
                'ating_mtd_pct': x['canais'][ch]['ating_mtd_pct'],
                'crescimento_mom_pct': x['canais'][ch]['crescimento_mom_pct'],
                'crescimento_yoy_pct': x['canais'][ch]['crescimento_yoy_pct']
            } for x in det_subs],
            'aceleradores_subgrupos': [{
                'nome': x['subgrupo'],
                'grupo': x['grupo'],
                'realizado_mtd': x['canais'][ch]['realizado_mtd'],
                'meta_mtd': x['canais'][ch]['meta_mtd'],
                'gap_mtd': x['canais'][ch]['gap_mtd'],
                'desvio_pct': x['canais'][ch]['desvio_pct'],
                'ating_mtd_pct': x['canais'][ch]['ating_mtd_pct'],
                'crescimento_mom_pct': x['canais'][ch]['crescimento_mom_pct'],
                'crescimento_yoy_pct': x['canais'][ch]['crescimento_yoy_pct']
            } for x in acel_subs],
            'detratores_linhas': [{
                'nome': x['linha'],
                'subgrupo': x['subgrupo'],
                'grupo': x['grupo'],
                'realizado_mtd': x['canais'][ch]['realizado_mtd'],
                'meta_mtd': x['canais'][ch]['meta_mtd'],
                'gap_mtd': x['canais'][ch]['gap_mtd'],
                'desvio_pct': x['canais'][ch]['desvio_pct'],
                'ating_mtd_pct': x['canais'][ch]['ating_mtd_pct'],
                'crescimento_mom_pct': x['canais'][ch]['crescimento_mom_pct'],
                'crescimento_yoy_pct': x['canais'][ch]['crescimento_yoy_pct']
            } for x in det_lins],
            'aceleradores_linhas': [{
                'nome': x['linha'],
                'subgrupo': x['subgrupo'],
                'grupo': x['grupo'],
                'realizado_mtd': x['canais'][ch]['realizado_mtd'],
                'meta_mtd': x['canais'][ch]['meta_mtd'],
                'gap_mtd': x['canais'][ch]['gap_mtd'],
                'desvio_pct': x['canais'][ch]['desvio_pct'],
                'ating_mtd_pct': x['canais'][ch]['ating_mtd_pct'],
                'crescimento_mom_pct': x['canais'][ch]['crescimento_mom_pct'],
                'crescimento_yoy_pct': x['canais'][ch]['crescimento_yoy_pct']
            } for x in acel_lins]
        }

    # 11. Opções de Filtros Globais Interativos
    filtro_grupos = sorted(list(set(l['grupo'] for l in tabela_linhas if l['grupo'] not in ('OUTROS', ''))))
    filtro_subgrupos = defaultdict(list)
    for l in tabela_linhas:
        g = l['grupo']
        s = l['subgrupo']
        if s not in filtro_subgrupos[g] and s not in ('OUTROS', ''):
            filtro_subgrupos[g].append(s)
    for g in filtro_subgrupos:
        filtro_subgrupos[g] = sorted(filtro_subgrupos[g])

    filtro_laboratorios = [l['laboratorio'] for l in tabela_laboratorios[:100] if l['laboratorio'] not in ('OUTROS', '')]

    # 12. Montar Pacote Consolidado Final
    dashboard_data = {
        'versao': '2.1.0',
        'gerado_em': time.strftime('%Y-%m-%d %H:%M:%S'),
        'kpis': kpis_executivos,
        'canais_tabela': canais_tabela,
        'curva_diaria': curva_grafico,
        'grupos': tabela_grupos,
        'subgrupos': tabela_subgrupos,
        'linhas': tabela_linhas[:500],
        'laboratorios': tabela_laboratorios[:250],
        'top_skus': top_skus_processados[:250],
        'destaques': diagnostico_causas['total'],
        'diagnostico_causas': diagnostico_causas,
        'filtros': {
            'grupos': filtro_grupos,
            'subgrupos': filtro_subgrupos,
            'laboratorios': filtro_laboratorios
        }
    }

    final_json_path = os.path.join(DATA_DIR, 'dashboard_digital_data.json')
    with open(final_json_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Pacote analítico consolidado gerado com sucesso em: {final_json_path}")
    print(f"   Tamanho do JSON final: {os.path.getsize(final_json_path) / 1024:.1f} KB")
    print(f"🎉 Pipeline analítico concluído em {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    main()
