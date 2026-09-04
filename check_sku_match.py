import os, json
import pandas as pd

parquet_metas = r"C:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\Acompanhamento Categorias Digital\data\metas_digital_completa.parquet"
df_metas = pd.read_parquet(parquet_metas)

parquet_base = r"c:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\dashboard-acompanhamento-categorias\data\base_dados_summary.parquet"
if os.path.exists(parquet_base):
    df_base = pd.read_parquet(parquet_base)
    prods_metas = set(df_metas['Desc_Produto'].str.upper().str.strip())
    prods_base = set(df_base['produto'].str.upper().str.strip())
    inter = prods_metas.intersection(prods_base)
    print(f"Total produtos em Metas: {len(prods_metas):,}")
    print(f"Total produtos em Base Dados: {len(prods_base):,}")
    print(f"Interseção de produtos: {len(inter):,} ({len(inter)/len(prods_metas)*100:.1f}%)")
