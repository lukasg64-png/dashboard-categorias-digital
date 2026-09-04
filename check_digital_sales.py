import os, json
from collections import defaultdict

file_path = r"c:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\dashboard-acompanhamento-categorias\data\setembro\canais_by_hierarquia.json"
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

totais = defaultdict(lambda: {'v26': 0.0, 'v26_06': 0.0, 'v25': 0.0})
for r in data:
    c = str(r.get('canal', '')).strip()
    totais[c]['v26'] += float(r.get('v26', 0) or 0)
    totais[c]['v26_06'] += float(r.get('v26_06', 0) or 0)
    totais[c]['v25'] += float(r.get('v25', 0) or 0)

print(f"{'CANAL':30s} | {'SET/26 MTD':14s} | {'AGO/26 MTD':14s} | {'SET/25 MTD':14s}")
print("-" * 80)
for c, vals in sorted(totais.items(), key=lambda x: x[1]['v26'], reverse=True):
    print(f"{c:30s} | R$ {vals['v26']:11,.2f} | R$ {vals['v26_06']:11,.2f} | R$ {vals['v25']:11,.2f}")
