import pandas as pd
import numpy as np

file_path = r"C:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\Acompanhamento Categorias Digital\Metas Digital.xlsx"
df = pd.read_excel(file_path)

print("=== INFORMAÇÕES GERAIS DAS METAS DIGITAL ===")
print("Shape:", df.shape)
print("Colunas:", df.columns.tolist())
print("\nTipos de dados:\n", df.dtypes)
print("\nValores nulos por coluna:\n", df.isnull().sum())

print("\n=== TOTALIZADORES DE METAS POR CANAL ===")
for col in ['App', 'Site', 'Marketplace']:
    total = df[col].sum()
    positivos = (df[col] > 0).sum()
    print(f"{col:12s}: R$ {total:14,.2f} | SKUs com meta > 0: {positivos:6d} ({positivos/len(df)*100:.1f}%)")

total_geral = df['App'].sum() + df['Site'].sum() + df['Marketplace'].sum()
print(f"{'TOTAL GERAL':12s}: R$ {total_geral:14,.2f}")

print("\n=== CARDEALIDADE DAS HIERARQUIAS ===")
print("Grupos únicos:      ", df['Desc_Grupo'].nunique())
print("Subgrupos únicos:   ", df['Desc_Subgrupo'].nunique())
print("Linhas únicas:      ", df['Desc_Linha'].nunique())
print("Laboratórios únicos:", df['Laboratorio'].nunique())
print("Produtos únicos:    ", df['Produto_ID'].nunique())

print("\n=== TOP 5 GRUPOS POR META DIGITAL ===")
df['Total_Digital'] = df['App'] + df['Site'] + df['Marketplace']
grp = df.groupby('Desc_Grupo')[['App', 'Site', 'Marketplace', 'Total_Digital']].sum().sort_values(by='Total_Digital', ascending=False)
grp['% Part'] = (grp['Total_Digital'] / total_geral) * 100
print(grp.head(10).to_string())

print("\n=== TOP 5 PRODUTOS (SKUs) POR META DIGITAL ===")
top_skus = df.sort_values(by='Total_Digital', ascending=False)[['Produto_ID', 'Desc_Produto', 'Desc_Linha', 'App', 'Site', 'Marketplace', 'Total_Digital']].head(10)
print(top_skus.to_string())
