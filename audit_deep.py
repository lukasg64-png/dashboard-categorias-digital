"""
audit_deep.py - Validação profunda de todas as camadas de dados
"""
import json, sys, os
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def fmt(v):
    return "R$ {:,.2f}".format(v)

with open(os.path.join(DATA_DIR, 'metas_resumo.json'), 'r', encoding='utf-8') as f:
    resumo = json.load(f)
with open(os.path.join(DATA_DIR, 'metas_por_grupo.json'), 'r', encoding='utf-8') as f:
    grupos = json.load(f)
with open(os.path.join(DATA_DIR, 'metas_por_linha.json'), 'r', encoding='utf-8') as f:
    linhas = json.load(f)
with open(os.path.join(DATA_DIR, 'metas_por_laboratorio.json'), 'r', encoding='utf-8') as f:
    labs = json.load(f)
with open(os.path.join(DATA_DIR, 'dashboard_digital_data.json'), 'r', encoding='utf-8') as f:
    dash = json.load(f)

meta_t = resumo['metas']['total']
meta_a = resumo['metas']['app']
meta_s = resumo['metas']['site']
meta_m = resumo['metas']['marketplace']

print("=" * 80)
print("  VALIDACAO METAS POR GRUPO vs RESUMO")
print("=" * 80)

sg_a = sum(g['App'] for g in grupos)
sg_s = sum(g['Site'] for g in grupos)
sg_m = sum(g['Marketplace'] for g in grupos)
sg_t = sum(g['Total_Digital'] for g in grupos)

print("  Grupo App:    {} vs Resumo: {} -> diff={}".format(fmt(sg_a), fmt(meta_a), fmt(abs(sg_a - meta_a))))
print("  Grupo Site:   {} vs Resumo: {} -> diff={}".format(fmt(sg_s), fmt(meta_s), fmt(abs(sg_s - meta_s))))
print("  Grupo Mkt:    {} vs Resumo: {} -> diff={}".format(fmt(sg_m), fmt(meta_m), fmt(abs(sg_m - meta_m))))
print("  Grupo Total:  {} vs Resumo: {} -> diff={}".format(fmt(sg_t), fmt(meta_t), fmt(abs(sg_t - meta_t))))

print("\n" + "=" * 80)
print("  VALIDACAO METAS POR LINHA vs RESUMO")
print("=" * 80)

sl_a = sum(l['App'] for l in linhas)
sl_s = sum(l['Site'] for l in linhas)
sl_m = sum(l['Marketplace'] for l in linhas)
sl_t = sum(l['Total_Digital'] for l in linhas)
print("  Linha App:    {} vs Resumo: {} -> diff={}".format(fmt(sl_a), fmt(meta_a), fmt(abs(sl_a - meta_a))))
print("  Linha Site:   {} vs Resumo: {} -> diff={}".format(fmt(sl_s), fmt(meta_s), fmt(abs(sl_s - meta_s))))
print("  Linha Mkt:    {} vs Resumo: {} -> diff={}".format(fmt(sl_m), fmt(meta_m), fmt(abs(sl_m - meta_m))))
print("  Linha Total:  {} vs Resumo: {} -> diff={}".format(fmt(sl_t), fmt(meta_t), fmt(abs(sl_t - meta_t))))
print("  Total linhas: {}".format(len(linhas)))

print("\n" + "=" * 80)
print("  VALIDACAO METAS POR LABORATORIO vs RESUMO")
print("=" * 80)

slab_t = sum(l['Total_Digital'] for l in labs)
slab_a = sum(l['App'] for l in labs)
slab_s = sum(l['Site'] for l in labs)
slab_m = sum(l['Marketplace'] for l in labs)
print("  Lab Total:    {} vs Resumo: {} -> diff={}".format(fmt(slab_t), fmt(meta_t), fmt(abs(slab_t - meta_t))))
print("  Lab App:      {} vs Resumo: {} -> diff={}".format(fmt(slab_a), fmt(meta_a), fmt(abs(slab_a - meta_a))))
print("  Lab Site:     {} vs Resumo: {} -> diff={}".format(fmt(slab_s), fmt(meta_s), fmt(abs(slab_s - meta_s))))
print("  Lab Mkt:      {} vs Resumo: {} -> diff={}".format(fmt(slab_m), fmt(meta_m), fmt(abs(slab_m - meta_m))))
print("  Total labs:   {}".format(len(labs)))

print("\n" + "=" * 80)
print("  ESTRUTURA DO DASHBOARD")
print("=" * 80)

for key in dash:
    v = dash[key]
    if isinstance(v, list):
        print("  {}: {} registros".format(key, len(v)))
    elif isinstance(v, dict):
        sub_keys = list(v.keys())[:10]
        print("  {}: dict com chaves {}".format(key, sub_keys))
    else:
        print("  {}: {}".format(key, v))

# Linhas no dashboard
if 'linhas' in dash and len(dash['linhas']) > 0:
    sdlr = sum(l.get('realizado_mtd', 0) for l in dash['linhas'])
    sdlm = sum(l.get('meta_mensal', 0) for l in dash['linhas'])
    kpi_real = dash['kpis']['canais']['total']['venda_mtd']
    print("\n  LINHAS NO DASHBOARD:")
    print("    Total linhas: {}".format(len(dash['linhas'])))
    print("    Soma realizado: {} vs KPI Total: {} -> diff={}".format(fmt(sdlr), fmt(kpi_real), fmt(abs(sdlr - kpi_real))))
    print("    Soma meta_mensal: {} vs Meta: {} -> diff={}".format(fmt(sdlm), fmt(meta_t), fmt(abs(sdlm - meta_t))))

# Labs no dashboard
if 'laboratorios' in dash and len(dash['laboratorios']) > 0:
    sdlabr = sum(l.get('realizado_mtd', 0) for l in dash['laboratorios'])
    sdlabm = sum(l.get('meta_mensal', 0) for l in dash['laboratorios'])
    print("\n  LABS NO DASHBOARD:")
    print("    Total labs: {}".format(len(dash['laboratorios'])))
    print("    Soma realizado: {} vs KPI Total: {} -> diff={}".format(fmt(sdlabr), fmt(kpi_real), fmt(abs(sdlabr - kpi_real))))
    print("    Soma meta_mensal: {} vs Meta: {} -> diff={}".format(fmt(sdlabm), fmt(meta_t), fmt(abs(sdlabm - meta_t))))

# Destaques
if 'destaques' in dash:
    print("\n  DESTAQUES (Total Digital):")
    for grp in dash['destaques']:
        items = dash['destaques'][grp]
        total_gap = sum(i.get('gap_mtd', 0) for i in items)
        print("    {}: {} items, soma GAP = {}".format(grp, len(items), fmt(total_gap)))

# Diagnostico por canal
if 'diagnostico_causas' in dash:
    print("\n  DIAGNOSTICO POR CANAL:")
    for ch in dash['diagnostico_causas']:
        dc = dash['diagnostico_causas'][ch]
        det_l_gap = sum(i.get('gap_mtd', 0) for i in dc.get('detratores_laboratorios', []))
        acel_l_gap = sum(i.get('gap_mtd', 0) for i in dc.get('aceleradores_laboratorios', []))
        det_s_gap = sum(i.get('gap_mtd', 0) for i in dc.get('detratores_subgrupos', []))
        acel_s_gap = sum(i.get('gap_mtd', 0) for i in dc.get('aceleradores_subgrupos', []))
        det_lin_gap = sum(i.get('gap_mtd', 0) for i in dc.get('detratores_linhas', []))
        acel_lin_gap = sum(i.get('gap_mtd', 0) for i in dc.get('aceleradores_linhas', []))
        print("    {}: Det Labs GAP={}, Acel Labs GAP={}".format(ch, fmt(det_l_gap), fmt(acel_l_gap)))
        print("    {}: Det Subs GAP={}, Acel Subs GAP={}".format(ch, fmt(det_s_gap), fmt(acel_s_gap)))
        print("    {}: Det Lins GAP={}, Acel Lins GAP={}".format(ch, fmt(det_lin_gap), fmt(acel_lin_gap)))

# Grupos no dashboard
if 'grupos' in dash and len(dash['grupos']) > 0:
    print("\n  GRUPOS NO DASHBOARD:")
    for g in dash['grupos']:
        print("    {}: Real={}, Meta MTD={}, Ating={}%, Gap={}".format(
            g['grupo'], fmt(g['realizado_mtd']), fmt(g['meta_mtd']),
            g['ating_mtd_pct'], fmt(g['gap_mtd'])))
    
    soma_grp_real = sum(g['realizado_mtd'] for g in dash['grupos'])
    soma_grp_meta = sum(g['meta_mensal'] for g in dash['grupos'])
    print("\n    Soma Real grupos: {} vs KPI: {} -> diff={}".format(
        fmt(soma_grp_real), fmt(kpi_real), fmt(abs(soma_grp_real - kpi_real))))
    print("    Soma Meta grupos: {} vs Meta: {} -> diff={}".format(
        fmt(soma_grp_meta), fmt(meta_t), fmt(abs(soma_grp_meta - meta_t))))

print()
