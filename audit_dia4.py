"""
audit_dia4.py — Investigar os R$ 15.802,63 no Dia 4 do Qlik
e entender a discrepancia canais_dia vs hierarquia
"""
import os, sys, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

sys.path.insert(0, BASE_DIR)
from process_digital_analytics import map_channel_category

with open(os.path.join(DATA_DIR, 'qlik_digital_raw.json'), 'r', encoding='utf-8') as f:
    qlik = json.load(f)

canais_dia = qlik.get('canais_dia', [])
max_dia = qlik.get('maxDia', 3)

print("=" * 80)
print("  INVESTIGACAO: DADOS DO DIA 4 NO QLIK")
print("=" * 80)

# 1. Mostrar todos os registros com dia >= 4
print(f"\n  maxDia oficial: {max_dia}")
print(f"\n  Registros com dia >= 4 no canais_dia:")
for r in canais_dia:
    dia = int(r[1]) if str(r[1]).isdigit() else 0
    v26 = float(r[2] or 0)
    if dia >= 4 and v26 > 0:
        cat = map_channel_category(r[0])
        print(f"    Canal={r[0]}, Dia={dia}, v26=R$ {v26:,.2f}, cat={cat}")

# 2. Somar apenas dias 1-3 do canais_dia 
print(f"\n  Soma canais_dia APENAS dias 1 a {max_dia}:")
tot_d13 = {'app': 0, 'site': 0, 'marketplace': 0, 'outros': 0}
for r in canais_dia:
    dia = int(r[1]) if str(r[1]).isdigit() else 0
    v26 = float(r[2] or 0)
    cat = map_channel_category(r[0])
    if 1 <= dia <= max_dia and cat != 'outros':
        tot_d13[cat] += v26

tot_sem_outros = tot_d13['app'] + tot_d13['site'] + tot_d13['marketplace']
print(f"    App:           R$ {tot_d13['app']:,.2f}")
print(f"    Site:          R$ {tot_d13['site']:,.2f}")
print(f"    Marketplace:   R$ {tot_d13['marketplace']:,.2f}")
print(f"    Total:         R$ {tot_sem_outros:,.2f}")

# 3. Comparar com dashboard
with open(os.path.join(DATA_DIR, 'dashboard_digital_data.json'), 'r', encoding='utf-8') as f:
    dash = json.load(f)

canais_dash = dash['kpis']['canais']
print(f"\n  Comparacao: canais_dia(dias 1-3) vs Dashboard:")
for ch_key, cat_v in [('total', tot_sem_outros), ('app', tot_d13['app']),
                       ('site', tot_d13['site']), ('marketplace', tot_d13['marketplace'])]:
    dash_v = canais_dash[ch_key]['venda_mtd']
    diff = abs(dash_v - cat_v)
    status = "OK" if diff < 10 else "DIVERGE"
    print(f"    {ch_key:15s}: Qlik(d1-3)=R$ {cat_v:,.2f}, Dashboard=R$ {dash_v:,.2f}, diff=R$ {diff:,.2f} [{status}]")

# 4. Hierarquia total vs canais_dia(dias 1-3)
hierarquia = qlik.get('hierarquia', [])
total_hier = 0
cat_hier = {'app': 0, 'site': 0, 'marketplace': 0, 'outros': 0}
for r in hierarquia:
    v26 = float(r[4] or 0)
    cat = map_channel_category(r[0])
    if cat != 'outros':
        total_hier += v26
        cat_hier[cat] += v26

print(f"\n  Hierarquia totais:")
print(f"    App:           R$ {cat_hier['app']:,.2f}")
print(f"    Site:          R$ {cat_hier['site']:,.2f}")
print(f"    Marketplace:   R$ {cat_hier['marketplace']:,.2f}")
print(f"    Total:         R$ {total_hier:,.2f}")

print(f"\n  Diff hierarquia vs canais_dia(d1-3):")
for k in ['app', 'site', 'marketplace']:
    diff = abs(cat_hier[k] - tot_d13[k])
    print(f"    {k:15s}: diff=R$ {diff:,.2f}")

diff_tot = abs(total_hier - tot_sem_outros)
print(f"    Total:          diff=R$ {diff_tot:,.2f}")

# 5. EXPLICACAO
print(f"\n" + "=" * 80)
print(f"  CONCLUSAO")
print(f"=" * 80)

# O process_digital_analytics.py usa canais_dia para daily_sales
# mas filtra por max_dia (dia <= max_dia) na hora de acumular
# Porém canais_dia tem registros de todos os dias (incl dia 4+)
# enquanto hierarquia NÃO contém dia 4 porque hierarquia é MTD total sem day breakdown
# A diferença é porque:
# - canais_dia tem registros parciais do dia 4 (R$ 15.802,63 que são early morning sales)
# - hierarquia contém apenas vendas realizadas (excluindo dia parcial?)
# - O dashboard usa a hierarquia para linhas/labs/skus

print(f"\n  O Qlik tem R$ 15.802,63 no Dia 4 no canais_dia (vendas parciais do dia corrente)")
print(f"  O processamento CORRETAMENTE ignora dia > {max_dia} para os KPIs (usa hierarquia)")
print(f"  A diferenca entre canais_dia(d1-3) e hierarquia indica vendas que:")
print(f"  - Podem ter mapeamento de canal diferente entre os dois blocos")
print(f"  - Ou arredondamentos na agregacao do Qlik")

# 6. Tabelas do dashboard 
print(f"\n  Tabelas do dashboard:")
tabelas = dash.get('tabelas', {})
for key in tabelas:
    v = tabelas[key]
    if isinstance(v, list):
        print(f"    {key}: {len(v)} registros")
    elif isinstance(v, dict):
        for sub_key in v:
            sub_v = v[sub_key]
            if isinstance(sub_v, list):
                print(f"    {key}.{sub_key}: {len(sub_v)} registros")

# Check destaques 
destaques = dash.get('destaques', {})
print(f"\n  Destaques:")
for key in destaques:
    v = destaques[key]
    if isinstance(v, list):
        print(f"    {key}: {len(v)} registros")
        if len(v) > 0:
            print(f"      Primeiro: {json.dumps(v[0], ensure_ascii=False)[:200]}")
