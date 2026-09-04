"""
process_digital_analytics.py — Motor Analítico de Consolidação Digital (Set/2026).
Cruza as Metas Diarizadas oficiais com o Realizado do Qlik Sense.
Calcula Desvios (Atingimento % e GAP R$), Evolução (Curva Diária), Crescimento (YoY e MoM),
Projeções de Fechamento e Curva ABC por Hierarquia e SKU.
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

def calc_growth(cur, prev):
    diff = cur - prev
    pct = (diff / prev * 100.0) if prev and prev > 0 else 0.0
    return round(pct, 2), round(diff, 2)

def main():
    t0 = time.time()
    print("=" * 70)
    print("  PROCESSAMENTO ANALÍTICO: METAS X REALIZADO DIGITAL (SET/2026)")
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
    # canais_dia: [canal, dia, v26, v26_06, v25]
    raw_canais_dia = qlik_raw.get('canais_dia', [])
    
    # Estrutura por Dia: total, app, site, marketplace
    daily_sales = defaultdict(lambda: {
        'total': 0.0, 'app': 0.0, 'site': 0.0, 'marketplace': 0.0,
        'v26_06_total': 0.0, 'v25_total': 0.0
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
            'ating_acum_total': calc_pct(real_acum_total, m_acum_tot) if is_realizado else None
        })

    # 4. Totais Executivos MTD & Projeção
    meta_total_mtd = meta_total_mensal * pct_acum_dmax
    meta_app_mtd = meta_app_mensal * pct_acum_dmax
    meta_site_mtd = meta_site_mensal * pct_acum_dmax
    meta_mkt_mtd = meta_mkt_mensal * pct_acum_dmax

    # Histórico comparativo MTD
    v26_06_mtd_tot = sum(daily_sales[d]['v26_06_total'] for d in range(1, max_dia + 1))
    v25_mtd_tot = sum(daily_sales[d]['v25_total'] for d in range(1, max_dia + 1))

    # Projeção de Fechamento (Run Rate ponderado pela curva de diarização)
    proj_total = (real_acum_total / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0
    proj_app = (real_acum_app / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0
    proj_site = (real_acum_site / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0
    proj_mkt = (real_acum_mkt / pct_acum_dmax) if pct_acum_dmax > 0 else 0.0

    # Crescimentos
    yoy_pct, yoy_diff = calc_growth(real_acum_total, v25_mtd_tot)
    mom_pct, mom_diff = calc_growth(real_acum_total, v26_06_mtd_tot)

    kpis_executivos = {
        'data_corte': f"01 a {max_dia:02d}/09/2026 (D-1)",
        'max_dia': max_dia,
        'pct_tempo_mes': round(max_dia / 30 * 100, 1),
        'pct_curva_acum': round(pct_acum_dmax * 100, 2),
        'canais': {
            'total': {
                'nome': 'Total Digital',
                'venda_mtd': round(real_acum_total, 2),
                'meta_mtd': round(meta_total_mtd, 2),
                'meta_mensal': round(meta_total_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_total, meta_total_mtd),
                'gap_mtd': round(real_acum_total - meta_total_mtd, 2),
                'ating_mensal_pct': calc_pct(real_acum_total, meta_total_mensal),
                'projecao_fechamento': round(proj_total, 2),
                'ating_proj_pct': calc_pct(proj_total, meta_total_mensal),
                'gap_projecao': round(proj_total - meta_total_mensal, 2),
                'share_realizado_pct': 100.0,
                'share_meta_pct': 100.0,
                'crescimento_yoy_pct': yoy_pct,
                'crescimento_yoy_diff': yoy_diff,
                'crescimento_mom_pct': mom_pct,
                'crescimento_mom_diff': mom_diff
            },
            'app': {
                'nome': 'App',
                'icone': '📱',
                'venda_mtd': round(real_acum_app, 2),
                'meta_mtd': round(meta_app_mtd, 2),
                'meta_mensal': round(meta_app_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_app, meta_app_mtd),
                'gap_mtd': round(real_acum_app - meta_app_mtd, 2),
                'ating_mensal_pct': calc_pct(real_acum_app, meta_app_mensal),
                'projecao_fechamento': round(proj_app, 2),
                'ating_proj_pct': calc_pct(proj_app, meta_app_mensal),
                'gap_projecao': round(proj_app - meta_app_mensal, 2),
                'share_realizado_pct': calc_pct(real_acum_app, real_acum_total),
                'share_meta_pct': metas_resumo['shares']['app']
            },
            'site': {
                'nome': 'Site',
                'icone': '💻',
                'venda_mtd': round(real_acum_site, 2),
                'meta_mtd': round(meta_site_mtd, 2),
                'meta_mensal': round(meta_site_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_site, meta_site_mtd),
                'gap_mtd': round(real_acum_site - meta_site_mtd, 2),
                'ating_mensal_pct': calc_pct(real_acum_site, meta_site_mensal),
                'projecao_fechamento': round(proj_site, 2),
                'ating_proj_pct': calc_pct(proj_site, meta_site_mensal),
                'gap_projecao': round(proj_site - meta_site_mensal, 2),
                'share_realizado_pct': calc_pct(real_acum_site, real_acum_total),
                'share_meta_pct': metas_resumo['shares']['site']
            },
            'marketplace': {
                'nome': 'Marketplace',
                'icone': '🛍️',
                'venda_mtd': round(real_acum_mkt, 2),
                'meta_mtd': round(meta_mkt_mtd, 2),
                'meta_mensal': round(meta_mkt_mensal, 2),
                'ating_mtd_pct': calc_pct(real_acum_mkt, meta_mkt_mtd),
                'gap_mtd': round(real_acum_mkt - meta_mkt_mtd, 2),
                'ating_mensal_pct': calc_pct(real_acum_mkt, meta_mkt_mensal),
                'projecao_fechamento': round(proj_mkt, 2),
                'ating_proj_pct': calc_pct(proj_mkt, meta_mkt_mensal),
                'gap_projecao': round(proj_mkt - meta_mkt_mensal, 2),
                'share_realizado_pct': calc_pct(real_acum_mkt, real_acum_total),
                'share_meta_pct': metas_resumo['shares']['marketplace']
            }
        }
    }

    print("\n--- RESUMO DE PERFORMANCE MTD (01 a {:02d}/09) ---".format(max_dia))
    for k, v in kpis_executivos['canais'].items():
        print(f"  {v['nome']:15s}: Realizado: R$ {v['venda_mtd']:11,.2f} | Meta MTD: R$ {v['meta_mtd']:11,.2f} | Ating: {v['ating_mtd_pct']:6.1f}% | GAP: R$ {v['gap_mtd']:11,.2f}")

    # 5. Processar Hierarquia: Linhas x Categorias x Metas
    # Carregar metas de linhas
    with open(os.path.join(DATA_DIR, 'metas_por_linha.json'), 'r', encoding='utf-8') as f:
        metas_linhas_raw = json.load(f)

    # Dicionário de metas por Linha
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

    # Agregar realizado por Linha a partir do Qlik
    raw_hier = qlik_raw.get('hierarquia', [])
    # Formato: [canal, grupo, subgrupo, linha, v26, v26_06, v25]
    real_linha_map = defaultdict(lambda: {
        'v26_total': 0.0, 'v26_app': 0.0, 'v26_site': 0.0, 'v26_mkt': 0.0,
        'v26_06_total': 0.0, 'v25_total': 0.0
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
            real_linha_map[key]['v25_total'] += v25

    # Unificar todas as linhas (com meta ou com venda)
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
            'v26_06_total': 0.0, 'v25_total': 0.0
        })

        v26_tot = round(rv['v26_total'], 2)
        m_mtd_tot = round(m['meta_mtd_total'], 2)
        m_mes_tot = round(m['meta_mensal_total'], 2)

        gap_mtd = round(v26_tot - m_mtd_tot, 2)
        ating_mtd = calc_pct(v26_tot, m_mtd_tot)
        proj_lin = round((v26_tot / pct_acum_dmax), 2) if pct_acum_dmax > 0 else 0.0

        yoy_l_pct, yoy_l_diff = calc_growth(v26_tot, rv['v25_total'])
        mom_l_pct, mom_l_diff = calc_growth(v26_tot, rv['v26_06_total'])

        tabela_linhas.append({
            'grupo': grp,
            'subgrupo': sub,
            'linha': lin,
            # Metas
            'meta_mensal': m_mes_tot,
            'meta_mtd': m_mtd_tot,
            'meta_mtd_app': m['meta_mtd_app'],
            'meta_mtd_site': m['meta_mtd_site'],
            'meta_mtd_mkt': m['meta_mtd_mkt'],
            # Realizado
            'realizado_mtd': v26_tot,
            'realizado_app': round(rv['v26_app'], 2),
            'realizado_site': round(rv['v26_site'], 2),
            'realizado_mkt': round(rv['v26_mkt'], 2),
            # Desvios
            'gap_mtd': gap_mtd,
            'ating_mtd_pct': ating_mtd,
            'projecao_fechamento': proj_lin,
            'ating_proj_pct': calc_pct(proj_lin, m_mes_tot),
            # Crescimento
            'v25_mtd': round(rv['v25_total'], 2),
            'crescimento_yoy_pct': yoy_l_pct,
            'v26_06_mtd': round(rv['v26_06_total'], 2),
            'crescimento_mom_pct': mom_l_pct
        })

    # Ordenar por maior venda MTD
    tabela_linhas.sort(key=lambda x: x['realizado_mtd'], reverse=True)
    print(f"Total de Linhas processadas com Metas e Realizado: {len(tabela_linhas):,}")

    # 6. Agregações por Grupo para o dashboard
    grupos_agg = defaultdict(lambda: {
        'meta_mensal': 0.0, 'meta_mtd': 0.0, 'realizado_mtd': 0.0,
        'realizado_app': 0.0, 'realizado_site': 0.0, 'realizado_mkt': 0.0,
        'v25_mtd': 0.0, 'v26_06_mtd': 0.0, 'total_linhas': 0
    })

    for l in tabela_linhas:
        g = l['grupo']
        grupos_agg[g]['meta_mensal'] += l['meta_mensal']
        grupos_agg[g]['meta_mtd'] += l['meta_mtd']
        grupos_agg[g]['realizado_mtd'] += l['realizado_mtd']
        grupos_agg[g]['realizado_app'] += l['realizado_app']
        grupos_agg[g]['realizado_site'] += l['realizado_site']
        grupos_agg[g]['realizado_mkt'] += l['realizado_mkt']
        grupos_agg[g]['v25_mtd'] += l['v25_mtd']
        grupos_agg[g]['v26_06_mtd'] += l['v26_06_mtd']
        grupos_agg[g]['total_linhas'] += 1

    tabela_grupos = []
    for g, v in grupos_agg.items():
        v26_g = round(v['realizado_mtd'], 2)
        m_mtd_g = round(v['meta_mtd'], 2)
        m_mes_g = round(v['meta_mensal'], 2)
        proj_g = round(v26_g / pct_acum_dmax, 2) if pct_acum_dmax > 0 else 0.0
        yoy_g_pct, _ = calc_growth(v26_g, v['v25_mtd'])
        mom_g_pct, _ = calc_growth(v26_g, v['v26_06_mtd'])

        tabela_grupos.append({
            'grupo': g,
            'meta_mensal': m_mes_g,
            'meta_mtd': m_mtd_g,
            'realizado_mtd': v26_g,
            'realizado_app': round(v['realizado_app'], 2),
            'realizado_site': round(v['realizado_site'], 2),
            'realizado_mkt': round(v['realizado_mkt'], 2),
            'gap_mtd': round(v26_g - m_mtd_g, 2),
            'ating_mtd_pct': calc_pct(v26_g, m_mtd_g),
            'projecao_fechamento': proj_g,
            'ating_proj_pct': calc_pct(proj_g, m_mes_g),
            'crescimento_yoy_pct': yoy_g_pct,
            'crescimento_mom_pct': mom_g_pct,
            'share_venda_pct': calc_pct(v26_g, real_acum_total),
            'total_linhas': v['total_linhas']
        })
    tabela_grupos.sort(key=lambda x: x['realizado_mtd'], reverse=True)

    # 7. Top SKUs (28.857 SKUs)
    with open(os.path.join(DATA_DIR, 'metas_top_skus.json'), 'r', encoding='utf-8') as f:
        top_skus_raw = json.load(f)

    # Enriquecer os top SKUs com meta MTD e ordenação
    top_skus_processados = []
    for sk in top_skus_raw[:500]:
        m_tot = sk.get('Total_Digital', 0.0)
        m_mtd = round(m_tot * pct_acum_dmax, 2)
        top_skus_processados.append({
            'id': sk.get('Produto_ID'),
            'nome': sk.get('Desc_Produto'),
            'grupo': sk.get('Desc_Grupo'),
            'subgrupo': sk.get('Desc_Subgrupo'),
            'linha': sk.get('Desc_Linha'),
            'laboratorio': sk.get('Laboratorio'),
            'meta_mensal': m_tot,
            'meta_mtd': m_mtd,
            'meta_app': sk.get('App', 0.0),
            'meta_site': sk.get('Site', 0.0),
            'meta_mkt': sk.get('Marketplace', 0.0)
        })

    # 8. Curva ABC e Destaques (Top 5 Aceleradores e Top 5 Detratores)
    linhas_com_meta = [l for l in tabela_linhas if l['meta_mtd'] > 5000]
    top_aceleradores = sorted(linhas_com_meta, key=lambda x: x['gap_mtd'], reverse=True)[:5]
    top_detratores = sorted(linhas_com_meta, key=lambda x: x['gap_mtd'])[:5]

    # 9. Montar Pacote Consolidado Final
    dashboard_data = {
        'versao': '1.0.0',
        'gerado_em': time.strftime('%Y-%m-%d %H:%M:%S'),
        'kpis': kpis_executivos,
        'curva_diaria': curva_grafico,
        'grupos': tabela_grupos,
        'linhas': tabela_linhas[:300], # Top 300 linhas para fluidez instantânea
        'top_skus': top_skus_processados[:200],
        'destaques': {
            'aceleradores': top_aceleradores,
            'detratores': top_detratores
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
