import os, json

file_path = r"c:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\dashboard-acompanhamento-categorias\data\setembro\canais_summary.json"
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== VENDAS DIÁRIAS DOS CANAIS DIGITAIS (SET/2026) ===")
for c in data:
    name = c.get('canal', '')
    if any(k in name.upper() for k in ['APP', 'SITE', 'IFOOD', 'COMMERCE']):
        dias = c.get('d26_07', [])[:5] # Dias 1 a 5
        print(f"\nCanal: {name}")
        for idx, v in enumerate(dias, 1):
            if v > 0:
                print(f"  Dia {idx}: R$ {v:12,.2f}")
