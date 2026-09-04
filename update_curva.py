"""
update_curva.py — Atualiza a curva oficial de diarização de Setembro/2026
conforme tabela oficial fornecida pelo usuário.
"""
import os, sys, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURVA_FILE = os.path.join(BASE_DIR, 'curva_diarizacao_setembro.json')

RAW_TABLE = """
1	Ter	01/09/2026	1.921.923,03	3,51%
2	Qua	02/09/2026	2.004.040,90	3,66%
3	Qui	03/09/2026	1.949.295,65	3,56%
4	Sex	04/09/2026	2.064.260,67	3,77%
5	Sab	05/09/2026	1.850.754,22	3,38%
6	Dom	06/09/2026	1.571.553,47	2,87%
7	Seg	07/09/2026	1.560.604,42	2,85%
8	Ter	08/09/2026	2.119.005,91	3,87%
9	Qua	09/09/2026	2.053.311,62	3,75%
10	Qui	10/09/2026	1.987.617,33	3,63%
11	Sex	11/09/2026	1.976.668,28	3,61%
12	Sab	12/09/2026	1.746.738,25	3,19%
13	Dom	13/09/2026	1.358.047,02	2,48%
14	Seg	14/09/2026	1.943.821,13	3,55%
15	Ter	15/09/2026	1.976.668,28	3,61%
16	Qua	16/09/2026	1.938.346,61	3,54%
17	Qui	17/09/2026	1.932.872,08	3,53%
18	Sex	18/09/2026	1.921.923,03	3,51%
19	Sab	19/09/2026	1.642.722,29	3,00%
20	Dom	20/09/2026	1.308.776,30	2,39%
21	Seg	21/09/2026	1.845.279,69	3,37%
22	Ter	22/09/2026	1.856.228,74	3,39%
23	Qua	23/09/2026	1.872.652,31	3,42%
24	Qui	24/09/2026	1.889.075,89	3,45%
25	Sex	25/09/2026	1.839.805,17	3,36%
26	Sab	26/09/2026	1.642.722,29	3,00%
27	Dom	27/09/2026	1.336.148,92	2,44%
28	Seg	28/09/2026	1.878.126,84	3,43%
29	Ter	29/09/2026	1.889.075,89	3,45%
30	Qua	30/09/2026	1.867.177,79	3,41%
""".strip()

lines = RAW_TABLE.split('\n')
curva = []
total_meta = 0.0

for line in lines:
    parts = [p.strip() for p in line.split('\t')]
    dia = int(parts[0])
    dow = parts[1]
    data = parts[2]
    meta_dia = float(parts[3].replace('.', '').replace(',', '.'))
    total_meta += meta_dia
    curva.append({
        'dia': dia,
        'dow': dow,
        'data': data,
        'meta_dia': meta_dia
    })

print(f"Total Meta da Curva fornecida: R$ {total_meta:,.2f}")

for c in curva:
    # Proporção exata em relação ao total mensal
    c['pct_mes'] = round(c['meta_dia'] / total_meta, 8)

with open(CURVA_FILE, 'w', encoding='utf-8') as f:
    json.dump(curva, f, ensure_ascii=False, indent=2)

print(f"✅ Curva oficial salva em: {CURVA_FILE}")
print(f"   Dias 1 a 3 soma meta: R$ {sum(c['meta_dia'] for c in curva[:3]):,.2f}")
print(f"   Dias 1 a 3 soma %: {sum(c['pct_mes'] for c in curva[:3])*100:.4f}%")
