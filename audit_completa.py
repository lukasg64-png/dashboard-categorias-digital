"""
audit_completa.py — Auditoria Completa do Pipeline de Dados do Dashboard Digital
Valida:
1. Curva de Diarização (curva_diarizacao_setembro.json vs curva_diaria_digital.json)
2. Metas Mensais (metas_resumo.json vs Excel vs diarização)
3. Dados do Qlik Sense (qlik_digital_raw.json)
4. Dashboard final (dashboard_digital_data.json)
5. Cruzamento e consistência de todos os dados
"""
import os, sys, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

errors = []
warnings = []
info = []

def ERR(msg):
    errors.append(msg)
    print(f"  ❌ ERRO: {msg}")

def WARN(msg):
    warnings.append(msg)
    print(f"  ⚠️  WARN: {msg}")

def OK(msg):
    info.append(msg)
    print(f"  ✅ OK: {msg}")

def fmt(v):
    return f"R$ {v:,.2f}"

def pct(v):
    return f"{v:.4f}%"

print("=" * 80)
print("  AUDITORIA COMPLETA DO PIPELINE DE DADOS — DASHBOARD DIGITAL SET/2026")
print("=" * 80)

# 1. CURVA DE DIARIZAÇÃO
print("\n" + "=" * 80)
print("  1. CURVA DE DIARIZAÇÃO (curva_diarizacao_setembro.json)")
print("=" * 80)

with open(os.path.join(BASE_DIR, 'curva_diarizacao_setembro.json'), 'r', encoding='utf-8') as f:
    curva_raw = json.load(f)

print(f"\n  Dias na curva: {len(curva_raw)}")
if len(curva_raw) != 30:
    ERR(f"Curva tem {len(curva_raw)} dias, deveria ter 30")
else:
    OK("Curva com 30 dias")

soma_pct = sum(c['pct_mes'] for c in curva_raw)
print(f"  Soma dos pct_mes: {soma_pct:.8f} (esperado: 1.00000000)")
if abs(soma_pct - 1.0) > 0.001:
    ERR(f"Soma dos % da curva = {soma_pct:.8f}, deveria ser ~1.0")
else:
    OK(f"Soma dos % = {soma_pct:.8f} ≈ 1.0")

soma_meta_curva = sum(c['meta_dia'] for c in curva_raw)
print(f"  Soma dos meta_dia na curva: {fmt(soma_meta_curva)}")

print(f"\n  Primeiros 3 dias da curva oficial:")
for c in curva_raw[:3]:
    print(f"    Dia {c['dia']} ({c['dow']}): {fmt(c['meta_dia'])} -> {pct(c['pct_mes']*100)}")

# 2. METAS
print("\n" + "=" * 80)
print("  2. METAS MENSAIS (metas_resumo.json)")
print("=" * 80)

with open(os.path.join(DATA_DIR, 'metas_resumo.json'), 'r', encoding='utf-8') as f:
    metas = json.load(f)

meta_total = metas['metas']['total']
meta_app = metas['metas']['app']
meta_site = metas['metas']['site']
meta_mkt = metas['metas']['marketplace']

print(f"\n  Meta Total Digital:   {fmt(meta_total)}")
print(f"  Meta App:             {fmt(meta_app)}")
print(f"  Meta Site:            {fmt(meta_site)}")
print(f"  Meta Marketplace:     {fmt(meta_mkt)}")
soma_canais = meta_app + meta_site + meta_mkt
print(f"  Soma canais:          {fmt(soma_canais)}")
diff_meta = abs(meta_total - soma_canais)
if diff_meta > 1.0:
    ERR(f"Meta Total ({fmt(meta_total)}) != Soma canais ({fmt(soma_canais)}), diff = {fmt(diff_meta)}")
else:
    OK(f"Meta Total = Soma Canais (diff = {fmt(diff_meta)})")

share_app = metas['shares']['app']
share_site = metas['shares']['site']
share_mkt = metas['shares']['marketplace']
print(f"\n  Shares oficiais: App={share_app}%, Site={share_site}%, Mkt={share_mkt}%, Soma={share_app+share_site+share_mkt:.2f}%")

share_app_calc = round(meta_app / meta_total * 100, 2)
share_site_calc = round(meta_site / meta_total * 100, 2)
share_mkt_calc = round(meta_mkt / meta_total * 100, 2)
print(f"  Shares recalculadas: App={share_app_calc}%, Site={share_site_calc}%, Mkt={share_mkt_calc}%")

# 3. CURVA DIÁRIA DIGITAL
print("\n" + "=" * 80)
print("  3. CURVA DIÁRIA DIGITAL (curva_diaria_digital.json)")
print("=" * 80)

with open(os.path.join(DATA_DIR, 'curva_diaria_digital.json'), 'r', encoding='utf-8') as f:
    curva_digital = json.load(f)

print(f"\n  Dias na curva digital: {len(curva_digital)}")

soma_meta_dia_total = sum(c['meta_dia_total'] for c in curva_digital)
soma_meta_dia_app = sum(c['meta_dia_app'] for c in curva_digital)
soma_meta_dia_site = sum(c['meta_dia_site'] for c in curva_digital)
soma_meta_dia_mkt = sum(c['meta_dia_mkt'] for c in curva_digital)

print(f"\n  Soma meta_dia por canal vs meta mensal:")
for nm, soma, meta in [("Total", soma_meta_dia_total, meta_total), ("App", soma_meta_dia_app, meta_app),
                         ("Site", soma_meta_dia_site, meta_site), ("Mkt", soma_meta_dia_mkt, meta_mkt)]:
    diff = abs(soma - meta)
    print(f"    {nm:12s}: Soma diarizada={fmt(soma)}, Meta mensal={fmt(meta)}, diff={fmt(diff)}")
    if diff > 100:
        ERR(f"Meta diarizada {nm}: soma = {fmt(soma)}, meta mensal = {fmt(meta)}, DIFERENCA = {fmt(diff)}")
    else:
        OK(f"Meta diarizada {nm}: soma ~= meta mensal (diff = {fmt(diff)})")

ultimo_dia = curva_digital[-1]
print(f"\n  Meta acumulada ultimo dia (30):")
for nm, acum, meta in [("Total", ultimo_dia['meta_acum_total'], meta_total),
                         ("App", ultimo_dia['meta_acum_app'], meta_app),
                         ("Site", ultimo_dia['meta_acum_site'], meta_site),
                         ("Mkt", ultimo_dia['meta_acum_mkt'], meta_mkt)]:
    diff = abs(acum - meta)
    print(f"    {nm:12s}: Acum={fmt(acum)}, Meta={fmt(meta)}, diff={fmt(diff)}")
    if diff > 100:
        ERR(f"Meta acumulada dia 30 {nm}: {fmt(acum)} != meta mensal {fmt(meta)}, diff = {fmt(diff)}")
    else:
        OK(f"Meta acum dia 30 {nm} = meta mensal (diff = {fmt(diff)})")

print(f"\n  pct_acum dia 1: {curva_digital[0]['pct_acum']}")
print(f"  pct_acum dia 3: {curva_digital[2]['pct_acum']}")
print(f"  pct_acum dia 30: {curva_digital[-1]['pct_acum']}")
if abs(curva_digital[-1]['pct_acum'] - 1.0) > 0.01:
    ERR(f"pct_acum dia 30 = {curva_digital[-1]['pct_acum']:.6f}, esperado ~1.0")
else:
    OK(f"pct_acum dia 30 ~= 1.0")

# Comparar pct_mes
divergentes = 0
for i in range(30):
    co = curva_raw[i]
    cd = curva_digital[i]
    diff_pct = abs(co['pct_mes'] - cd['pct_mes'])
    if diff_pct > 0.001:
        WARN(f"Dia {i+1}: curva_oficial pct_mes={co['pct_mes']:.6f}, curva_digital pct_mes={cd['pct_mes']:.6f}, diff={diff_pct:.6f}")
        divergentes += 1
if divergentes == 0:
    OK("Todos os pct_mes da curva oficial = curva digital")

# Diarização por canal
print(f"\n  Diarizacao por Canal (amostra 5 primeiros dias):")
for i in range(min(5, 30)):
    cd = curva_digital[i]
    p = cd['pct_mes']
    e_t = round(p * meta_total, 2)
    e_a = round(p * meta_app, 2)
    e_s = round(p * meta_site, 2)
    e_m = round(p * meta_mkt, 2)
    print(f"  Dia {i+1} (pct={p:.6f}): Tot={fmt(cd['meta_dia_total'])}(calc={fmt(e_t)}), App={fmt(cd['meta_dia_app'])}(calc={fmt(e_a)}), Site={fmt(cd['meta_dia_site'])}(calc={fmt(e_s)}), Mkt={fmt(cd['meta_dia_mkt'])}(calc={fmt(e_m)})")

# 4. DADOS DO QLIK
print("\n" + "=" * 80)
print("  4. DADOS DO QLIK SENSE (qlik_digital_raw.json)")
print("=" * 80)

with open(os.path.join(DATA_DIR, 'qlik_digital_raw.json'), 'r', encoding='utf-8') as f:
    qlik = json.load(f)

max_dia = qlik.get('maxDia', 0)
print(f"\n  maxDia (corte D-1): {max_dia}")
print(f"  Chaves no JSON: {list(qlik.keys())}")

canais_dia = qlik.get('canais_dia', [])
print(f"  canais_dia: {len(canais_dia)} registros")

sys.path.insert(0, BASE_DIR)
from process_digital_analytics import map_channel_category

if canais_dia:
    canais_unicos = sorted(set(r[0] for r in canais_dia))
    print(f"  Canais unicos no Qlik: {canais_unicos}")

    categorias_total = {'app': 0, 'site': 0, 'marketplace': 0, 'outros': 0}
    total_por_canal_v26 = {}
    for r in canais_dia:
        canal = r[0]
        v26 = float(r[2] or 0)
        cat = map_channel_category(canal)
        categorias_total[cat] += v26
        total_por_canal_v26[canal] = total_por_canal_v26.get(canal, 0) + v26

    print(f"\n  Totais por Canal:")
    for canal in sorted(total_por_canal_v26.keys()):
        v = total_por_canal_v26[canal]
        cat = map_channel_category(canal)
        print(f"    {canal:25s}: {fmt(v):>17s}  ->  {cat}")

    print(f"\n  Totais Consolidados:")
    print(f"    App:           {fmt(categorias_total['app'])}")
    print(f"    Site:          {fmt(categorias_total['site'])}")
    print(f"    Marketplace:   {fmt(categorias_total['marketplace'])}")
    print(f"    Outros:        {fmt(categorias_total['outros'])}")
    total_sem_outros = categorias_total['app'] + categorias_total['site'] + categorias_total['marketplace']
    print(f"    Total (sem outros): {fmt(total_sem_outros)}")

    if categorias_total['outros'] > 0:
        WARN(f"Existem {fmt(categorias_total['outros'])} em canais 'outros' que NAO entram no dashboard")

    # Vendas por dia
    vendas_por_dia = {}
    for r in canais_dia:
        canal = r[0]
        dia = int(r[1]) if str(r[1]).isdigit() else 0
        v26 = float(r[2] or 0)
        cat = map_channel_category(canal)
        if cat != 'outros' and dia > 0:
            vendas_por_dia[dia] = vendas_por_dia.get(dia, 0) + v26

    print(f"\n  Vendas por Dia (Total Digital):")
    for d in sorted(vendas_por_dia.keys()):
        print(f"    Dia {d}: {fmt(vendas_por_dia[d])}")
    total_vendas_qlik = sum(vendas_por_dia.values())
    print(f"    TOTAL MTD: {fmt(total_vendas_qlik)}")
else:
    total_vendas_qlik = 0
    categorias_total = {'app': 0, 'site': 0, 'marketplace': 0, 'outros': 0}
    total_sem_outros = 0

# Hierarquia
hierarquia = qlik.get('hierarquia', [])
print(f"\n  hierarquia: {len(hierarquia)} registros")
if hierarquia:
    total_hier_v26 = 0
    for r in hierarquia:
        v26 = float(r[4] or 0)
        cat = map_channel_category(r[0])
        if cat != 'outros':
            total_hier_v26 += v26
    print(f"  Total v26 hierarquia (sem outros): {fmt(total_hier_v26)}")
    diff_h = abs(total_vendas_qlik - total_hier_v26)
    print(f"  Diff vs canais_dia: {fmt(diff_h)}")
    if diff_h > 1000:
        WARN(f"Total hierarquia ({fmt(total_hier_v26)}) != canais_dia ({fmt(total_vendas_qlik)}), diff={fmt(diff_h)}")

# 5. DASHBOARD FINAL
print("\n" + "=" * 80)
print("  5. DASHBOARD FINAL (dashboard_digital_data.json)")
print("=" * 80)

with open(os.path.join(DATA_DIR, 'dashboard_digital_data.json'), 'r', encoding='utf-8') as f:
    dash = json.load(f)

kpis = dash['kpis']
canais_dash = kpis['canais']

print(f"\n  Data de corte: {kpis['data_corte']}")
print(f"  max_dia: {kpis['max_dia']}")
print(f"  pct_curva_acum: {kpis['pct_curva_acum']}%")

for ch_key in ['total', 'app', 'site', 'marketplace']:
    c = canais_dash[ch_key]
    print(f"\n    === {c['nome'].upper()} ===")
    print(f"    Venda MTD:    {fmt(c['venda_mtd'])}")
    print(f"    Meta MTD:     {fmt(c['meta_mtd'])}")
    print(f"    Meta Mensal:  {fmt(c['meta_mensal'])}")
    print(f"    Ating:        {c['ating_mtd_pct']}%")
    print(f"    GAP:          {fmt(c['gap_mtd'])}")
    print(f"    Desvio:       {c['desvio_pct']}%")
    print(f"    Projecao:     {fmt(c['projecao_fechamento'])}")
    print(f"    MoM:          {c['crescimento_mom_pct']}% ({fmt(c['crescimento_mom_diff'])})")
    print(f"    YoY:          {c['crescimento_yoy_pct']}% ({fmt(c['crescimento_yoy_diff'])})")
    print(f"    Run Rate:     Nec={fmt(c.get('diaria_necessaria',0))}, Atual={fmt(c.get('media_diaria_atual',0))}, Diff={fmt(c.get('ritmo_diff',0))}")

    gap_calc = round(c['venda_mtd'] - c['meta_mtd'], 2)
    if abs(gap_calc - c['gap_mtd']) > 1:
        ERR(f"{c['nome']}: GAP MTD = {fmt(c['gap_mtd'])} mas venda-meta = {fmt(gap_calc)}")
    ating_calc = round(c['venda_mtd'] / c['meta_mtd'] * 100, 2) if c['meta_mtd'] > 0 else 0
    if abs(ating_calc - c['ating_mtd_pct']) > 0.1:
        ERR(f"{c['nome']}: Atingimento = {c['ating_mtd_pct']}% mas calculado = {ating_calc}%")

# Soma canais = total
venda_soma = canais_dash['app']['venda_mtd'] + canais_dash['site']['venda_mtd'] + canais_dash['marketplace']['venda_mtd']
diff_venda = abs(canais_dash['total']['venda_mtd'] - venda_soma)
print(f"\n  Total venda_mtd: {fmt(canais_dash['total']['venda_mtd'])}, Soma canais: {fmt(venda_soma)}, diff: {fmt(diff_venda)}")
if diff_venda > 1:
    ERR(f"Total venda != soma canais, diff = {fmt(diff_venda)}")
else:
    OK(f"Total venda = soma canais")

# Cruzar vs Qlik bruto
print(f"\n  Cruzar Dashboard vs Qlik Bruto:")
for ch_key, cat_v in [('total', total_sem_outros), ('app', categorias_total['app']),
                       ('site', categorias_total['site']), ('marketplace', categorias_total['marketplace'])]:
    dash_v = canais_dash[ch_key]['venda_mtd']
    diff = abs(dash_v - cat_v)
    print(f"    {ch_key:15s}: Dashboard={fmt(dash_v)}, Qlik={fmt(cat_v)}, diff={fmt(diff)}")
    if diff > 100:
        ERR(f"{ch_key}: Dashboard ({fmt(dash_v)}) != Qlik bruto ({fmt(cat_v)}), diff = {fmt(diff)}")
    else:
        OK(f"{ch_key}: Dashboard = Qlik bruto (diff={fmt(diff)})")

# 6. CURVA DIÁRIA NO DASHBOARD
print("\n" + "=" * 80)
print("  6. CURVA DIARIA NO DASHBOARD")
print("=" * 80)

curva_dash = dash.get('curva_diaria', [])
print(f"  Registros na curva: {len(curva_dash)}")
dias_real = [c for c in curva_dash if c.get('is_realizado')]
print(f"  Dias com realizado: {len(dias_real)}")

soma_real_total = sum(c.get('real_dia_total', 0) or 0 for c in dias_real)
soma_real_app = sum(c.get('real_dia_app', 0) or 0 for c in dias_real)
soma_real_site = sum(c.get('real_dia_site', 0) or 0 for c in dias_real)
soma_real_mkt = sum(c.get('real_dia_mkt', 0) or 0 for c in dias_real)

for nm, sv, kv in [("Total", soma_real_total, canais_dash['total']['venda_mtd']),
                    ("App", soma_real_app, canais_dash['app']['venda_mtd']),
                    ("Site", soma_real_site, canais_dash['site']['venda_mtd']),
                    ("Mkt", soma_real_mkt, canais_dash['marketplace']['venda_mtd'])]:
    diff = abs(sv - kv)
    print(f"  {nm}: Soma curva={fmt(sv)}, KPI={fmt(kv)}, diff={fmt(diff)}")
    if diff > 1:
        ERR(f"Curva realizado {nm}: soma = {fmt(sv)}, KPI = {fmt(kv)}, diff = {fmt(diff)}")
    else:
        OK(f"Curva realizado {nm} = KPI venda_mtd")

# Desvio % por dia
print(f"\n  Desvio % por dia:")
for c in dias_real:
    real = c.get('real_dia_total', 0) or 0
    meta = c.get('meta_dia_total', 0) or 0
    desvio = c.get('desvio_dia_total')
    desvio_calc = round((real / meta - 1) * 100, 2) if meta > 0 else 0
    print(f"    Dia {c['dia']}: Real={fmt(real)}, Meta={fmt(meta)}, Desvio={desvio}%, Calc={desvio_calc}%")

# 7. TABELAS
print("\n" + "=" * 80)
print("  7. TABELAS DE DETALHAMENTO")
print("=" * 80)

tabelas = dash.get('tabelas', {})
for tab_name in ['canais', 'linhas', 'laboratorios', 'top_skus']:
    data = tabelas.get(tab_name, [])
    print(f"  Tabela '{tab_name}': {len(data)} registros")
    if data and isinstance(data, list) and len(data) > 0:
        total_tab = sum(r.get('realizado_mtd', 0) or r.get('venda_mtd', 0) or 0 for r in data)
        total_meta_tab = sum(r.get('meta_mtd', 0) or 0 for r in data)
        print(f"    Soma realizado_mtd: {fmt(total_tab)}")
        print(f"    Soma meta_mtd:      {fmt(total_meta_tab)}")

# 8. MoM e YoY
print("\n" + "=" * 80)
print("  8. VALIDACAO CRESCIMENTO MoM E YoY")
print("=" * 80)

for ch_key in ['total', 'app', 'site', 'marketplace']:
    c = canais_dash[ch_key]
    v_real = c['venda_mtd']
    v_mom = c['v26_06_mtd']
    v_yoy = c['v25_mtd']
    mom_calc = round((v_real / v_mom - 1) * 100, 2) if v_mom > 0 else 0
    yoy_calc = round((v_real / v_yoy - 1) * 100, 2) if v_yoy > 0 else 0
    print(f"\n  {c['nome']}: Real={fmt(v_real)}, Ago={fmt(v_mom)} MoM={c['crescimento_mom_pct']}%(calc={mom_calc}%), Set25={fmt(v_yoy)} YoY={c['crescimento_yoy_pct']}%(calc={yoy_calc}%)")
    if abs(mom_calc - c['crescimento_mom_pct']) > 0.5:
        ERR(f"{c['nome']}: MoM% dash={c['crescimento_mom_pct']}% vs calc={mom_calc}%")
    if abs(yoy_calc - c['crescimento_yoy_pct']) > 0.5:
        ERR(f"{c['nome']}: YoY% dash={c['crescimento_yoy_pct']}% vs calc={yoy_calc}%")

# RESUMO
print("\n" + "=" * 80)
print("  RESUMO DA AUDITORIA")
print("=" * 80)
print(f"\n  Validacoes OK: {len(info)}")
print(f"  Warnings:      {len(warnings)}")
print(f"  Erros:         {len(errors)}")

if warnings:
    print(f"\n  WARNINGS:")
    for w in warnings:
        print(f"    - {w}")
if errors:
    print(f"\n  ERROS:")
    for e in errors:
        print(f"    - {e}")
else:
    print(f"\n  NENHUM ERRO ENCONTRADO!")

print()
