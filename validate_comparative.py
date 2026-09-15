import subprocess
import json

out = subprocess.check_output(['git', 'show', 'HEAD:data/qlik_digital_raw.json'], text=True, encoding='utf-8')
old_data = json.loads(out)

with open('data/qlik_digital_raw.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)

print('=' * 105)
print('          VALIDAÇÃO MATEMÁTICA: QLIK SENSE ON-PREMISE (ANTIGO) vs QLIK CLOUD (NOVO)')
print('=' * 105)

# 1. TOTAL POR CANAL DETALHADO (canais_dia)
# r format: [Canal, Dia, v26, v26_06, v25]
old_tc = {}
for r in old_data.get('canais_dia', []):
    c = r[0]
    v = float(r[2] or 0)
    old_tc[c] = old_tc.get(c, 0.0) + v

new_tc = {}
for r in new_data.get('canais_dia', []):
    c = r[0]
    v = float(r[2] or 0)
    new_tc[c] = new_tc.get(c, 0.0) + v

all_ch = sorted(set(list(old_tc.keys()) + list(new_tc.keys())))
tot_old = sum(old_tc.values())
tot_new = sum(new_tc.values())
tot_new_sem_fig = sum(v for k, v in new_tc.items() if 'FIGITAL' not in k.upper())

print(f"\n{'Canal Detalhado':25s} | {'On-Prem (Antigo)':18s} | {'Qlik Cloud (Novo)':18s} | {'Diferença (R$)':16s} | {'Diferença (%)':14s}")
print('-' * 105)
for c in all_ch:
    vo = old_tc.get(c, 0.0)
    vn = new_tc.get(c, 0.0)
    diff = vn - vo
    diff_pct = (diff / vo * 100) if vo > 0 else (100.0 if vn > 0 else 0.0)
    print(f"{c:25s} | R$ {vo:15,.2f} | R$ {vn:15,.2f} | R$ {diff:+13,.2f} | {diff_pct:+12.4f}%")

print('-' * 105)
diff_sem = tot_new_sem_fig - tot_old
pct_sem = (diff_sem / tot_old * 100) if tot_old > 0 else 0.0
print(f"{'TOTAL (SEM FIGITAL)':25s} | R$ {tot_old:15,.2f} | R$ {tot_new_sem_fig:15,.2f} | R$ {diff_sem:+13,.2f} | {pct_sem:+12.4f}%")

diff_com = tot_new - tot_old
pct_com = (diff_com / tot_old * 100) if tot_old > 0 else 0.0
print(f"{'TOTAL (COM FIGITAL)':25s} | R$ {tot_old:15,.2f} | R$ {tot_new:15,.2f} | R$ {diff_com:+13,.2f} | {pct_com:+12.4f}%")


# 2. COMPARATIVO DIÁRIO (01 a 14/09)
print('\n' + '=' * 105)
print('                        COMPARAÇÃO DIÁRIA (01 A 14/09/2026)')
print('=' * 105)
old_daily = {}
for r in old_data.get('canais_dia', []):
    dia = int(r[1]) if str(r[1]).isdigit() else 0
    old_daily[dia] = old_daily.get(dia, 0.0) + float(r[2] or 0)

new_daily_sem_fig = {}
new_daily_fig = {}
for r in new_data.get('canais_dia', []):
    dia = int(r[1]) if str(r[1]).isdigit() else 0
    c = r[0].upper()
    v = float(r[2] or 0)
    if 'FIGITAL' in c:
        new_daily_fig[dia] = new_daily_fig.get(dia, 0.0) + v
    else:
        new_daily_sem_fig[dia] = new_daily_sem_fig.get(dia, 0.0) + v

print(f"{'Dia':8s} | {'On-Prem':16s} | {'Cloud (s/ Figital)':20s} | {'Diff (R$)':14s} | {'Figital (R$)':16s} | {'Cloud (c/ Figital)':20s}")
print('-' * 105)
for d in sorted(set(list(old_daily.keys()) + list(new_daily_sem_fig.keys()))):
    if d == 0: continue
    vo = old_daily.get(d, 0.0)
    v_sf = new_daily_sem_fig.get(d, 0.0)
    vf = new_daily_fig.get(d, 0.0)
    diff = v_sf - vo
    print(f"Dia {d:02d}   | R$ {vo:13,.2f} | R$ {v_sf:17,.2f} | R$ {diff:+11,.2f} | R$ {vf:13,.2f} | R$ {(v_sf+vf):17,.2f}")
