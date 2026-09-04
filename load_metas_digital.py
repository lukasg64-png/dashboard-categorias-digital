"""
load_metas_digital.py — Processa o arquivo 'Metas Digital.xlsx' e aplica a curva de
diarização oficial dos 30 dias de Setembro/2026.
Gera tabelas e resumos de metas estruturados por Canal e Hierarquia (Grupo, Subgrupo, Linha, Lab, SKU).
"""
import os, sys, json, shutil, time
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

EXCEL_FILE = os.path.join(BASE_DIR, 'Metas Digital.xlsx')
TEMP_EXCEL = os.path.join(DATA_DIR, 'temp_metas_digital.xlsx')
CURVA_FILE = os.path.join(BASE_DIR, 'curva_diarizacao_setembro.json')

def load_curva():
    """Carrega a curva diária oficial com 30 dias e calcula o acumulado."""
    with open(CURVA_FILE, 'r', encoding='utf-8') as f:
        curva = json.load(f)
    
    total_pct = sum(c['pct_mes'] for c in curva)
    total_meta = sum(c['meta_dia'] for c in curva)
    
    acum_pct = 0.0
    acum_meta = 0.0
    for c in curva:
        acum_pct += c['pct_mes']
        acum_meta += c['meta_dia']
        c['pct_acum'] = round(acum_pct, 6)
        c['meta_acum'] = acum_meta
        
    return curva, total_pct, total_meta

def get_dataframe():
    """Lê o Excel com segurança contra locks do OneDrive/Excel."""
    try:
        shutil.copy2(EXCEL_FILE, TEMP_EXCEL)
        target = TEMP_EXCEL
    except Exception:
        target = EXCEL_FILE
        
    print(f"Lendo base de metas: {os.path.basename(target)}...")
    df = pd.read_excel(target)
    
    # Tratamento de colunas e nulos
    df['Desc_Grupo'] = df['Desc_Grupo'].fillna('OUTROS').astype(str).str.strip()
    df['Desc_Subgrupo'] = df['Desc_Subgrupo'].fillna('OUTROS').astype(str).str.strip()
    df['Desc_Linha'] = df['Desc_Linha'].fillna('OUTROS').astype(str).str.strip()
    df['Laboratorio'] = df['Laboratorio'].fillna('OUTROS').astype(str).str.strip()
    df['Desc_Produto'] = df['Desc_Produto'].fillna('NÃO INFORMADO').astype(str).str.strip()
    df['Produto_ID'] = df['Produto_ID'].fillna(0).astype(int)
    
    for c in ['App', 'Site', 'Marketplace']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
        
    df['Total_Digital'] = df['App'] + df['Site'] + df['Marketplace']
    return df

def main():
    t0 = time.time()
    print("=" * 70)
    print("  PROCESSAMENTO DE METAS DIGITAL & CURVA DE DIARIZAÇÃO (SET/2026)")
    print("=" * 70)
    
    curva, soma_pct, soma_meta_curva = load_curva()
    print(f"Curva Diária carregada: 30 dias | Soma Pct: {soma_pct*100:.2f}% | Meta Total: R$ {soma_meta_curva:,.2f}")
    
    df = get_dataframe()
    total_skus = len(df)
    
    meta_app = float(df['App'].sum())
    meta_site = float(df['Site'].sum())
    meta_mkt = float(df['Marketplace'].sum())
    meta_total = float(df['Total_Digital'].sum())
    
    print("\n--- TOTAIS MENSAIS DAS METAS ---")
    print(f"  📱 App:         R$ {meta_app:14,.2f} ({meta_app/meta_total*100:.2f}%)")
    print(f"  💻 Site:        R$ {meta_site:14,.2f} ({meta_site/meta_total*100:.2f}%)")
    print(f"  🛍️ Marketplace: R$ {meta_mkt:14,.2f} ({meta_mkt/meta_total*100:.2f}%)")
    print(f"  🌐 TOTAL GERAL: R$ {meta_total:14,.2f} (100.00%)")
    print(f"  Total de SKUs cadastrados: {total_skus:,}")

    # 1. Salvar Resumo Geral
    resumo = {
        'mes': 'Setembro/2026',
        'dias_mes': 30,
        'total_skus': total_skus,
        'metas': {
            'total': round(meta_total, 2),
            'app': round(meta_app, 2),
            'site': round(meta_site, 2),
            'marketplace': round(meta_mkt, 2)
        },
        'shares': {
            'app': round(meta_app / meta_total * 100, 2),
            'site': round(meta_site / meta_total * 100, 2),
            'marketplace': round(meta_mkt / meta_total * 100, 2)
        },
        'atualizado_em': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(os.path.join(DATA_DIR, 'metas_resumo.json'), 'w', encoding='utf-8') as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    # 2. Curva diária completa com desdobramento por canal
    curva_detalhada = []
    for c in curva:
        pct = c['pct_mes']
        curva_detalhada.append({
            'dia': c['dia'],
            'dow': c['dow'],
            'data': c['data'],
            'pct_mes': round(pct, 6),
            'pct_acum': round(c['pct_acum'], 6),
            'meta_dia_total': round(meta_total * pct, 2),
            'meta_acum_total': round(meta_total * c['pct_acum'], 2),
            'meta_dia_app': round(meta_app * pct, 2),
            'meta_acum_app': round(meta_app * c['pct_acum'], 2),
            'meta_dia_site': round(meta_site * pct, 2),
            'meta_acum_site': round(meta_site * c['pct_acum'], 2),
            'meta_dia_mkt': round(meta_mkt * pct, 2),
            'meta_acum_mkt': round(meta_mkt * c['pct_acum'], 2)
        })
    with open(os.path.join(DATA_DIR, 'curva_diaria_digital.json'), 'w', encoding='utf-8') as f:
        json.dump(curva_detalhada, f, ensure_ascii=False, indent=2)

    # 3. Agregações Hierárquicas
    # Nível Grupo
    grp_df = df.groupby('Desc_Grupo')[['App', 'Site', 'Marketplace', 'Total_Digital']].sum().reset_index()
    grp_list = grp_df.to_dict(orient='records')
    for g in grp_list:
        for k in ['App', 'Site', 'Marketplace', 'Total_Digital']:
            g[k] = round(g[k], 2)
    with open(os.path.join(DATA_DIR, 'metas_por_grupo.json'), 'w', encoding='utf-8') as f:
        json.dump(grp_list, f, ensure_ascii=False, indent=2)

    # Nível Subgrupo
    sub_df = df.groupby(['Desc_Grupo', 'Desc_Subgrupo'])[['App', 'Site', 'Marketplace', 'Total_Digital']].sum().reset_index()
    sub_list = sub_df.to_dict(orient='records')
    for s in sub_list:
        for k in ['App', 'Site', 'Marketplace', 'Total_Digital']:
            s[k] = round(s[k], 2)
    with open(os.path.join(DATA_DIR, 'metas_por_subgrupo.json'), 'w', encoding='utf-8') as f:
        json.dump(sub_list, f, ensure_ascii=False, indent=2)

    # Nível Linha
    linha_df = df.groupby(['Desc_Grupo', 'Desc_Subgrupo', 'Desc_Linha'])[['App', 'Site', 'Marketplace', 'Total_Digital']].sum().reset_index()
    linha_list = linha_df.to_dict(orient='records')
    for l in linha_list:
        for k in ['App', 'Site', 'Marketplace', 'Total_Digital']:
            l[k] = round(l[k], 2)
    with open(os.path.join(DATA_DIR, 'metas_por_linha.json'), 'w', encoding='utf-8') as f:
        json.dump(linha_list, f, ensure_ascii=False, indent=2)

    # Nível Laboratório
    lab_df = df.groupby(['Laboratorio'])[['App', 'Site', 'Marketplace', 'Total_Digital']].sum().reset_index().sort_values(by='Total_Digital', ascending=False)
    lab_list = lab_df.to_dict(orient='records')
    for lb in lab_list:
        for k in ['App', 'Site', 'Marketplace', 'Total_Digital']:
            lb[k] = round(lb[k], 2)
    with open(os.path.join(DATA_DIR, 'metas_por_laboratorio.json'), 'w', encoding='utf-8') as f:
        json.dump(lab_list, f, ensure_ascii=False, indent=2)

    # 4. Top SKUs (para renderização rápida no dashboard)
    top_skus = df.sort_values(by='Total_Digital', ascending=False).head(1000).to_dict(orient='records')
    for sk in top_skus:
        for k in ['App', 'Site', 'Marketplace', 'Total_Digital']:
            sk[k] = round(sk[k], 2)
    with open(os.path.join(DATA_DIR, 'metas_top_skus.json'), 'w', encoding='utf-8') as f:
        json.dump(top_skus, f, ensure_ascii=False, indent=2)

    # 5. Salvar base tratada completa em Parquet para consultas ultra-rápidas
    parquet_path = os.path.join(DATA_DIR, 'metas_digital_completa.parquet')
    df.to_parquet(parquet_path, index=False)
    print(f"\n✅ Base completa de {len(df):,} SKUs salva em Parquet: {parquet_path}")
    print(f"🎉 Processamento de metas concluído em {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    main()
