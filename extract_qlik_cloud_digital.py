"""
extract_qlik_cloud_digital.py — Extrai dados dos Canais Digitais (App, Site e Marketplace)
do QLIK CLOUD (fsj.us.qlikcloud.com / Vendas Análise - Analítico).

Substitui a extração legada On-Premises conectando via WebSocket QIX Engine API
com autenticação resiliente via Keycloak SSO e preservação de sessão.

Extrai:
1. Vendas diárias por canal (Dia Venda × Canal Detalhado: APP, SITE, iFood, etc.)
2. Vendas por hierarquia (Canal Detalhado × Desc_Grupo × Desc_Subgrupo × Desc_Linha)
3. Vendas por laboratório (Canal Detalhado × Laboratorio)
4. Vendas diárias por linha (Canal Detalhado × Desc_Linha × Dia Venda)
5. Vendas diárias por laboratório (Canal Detalhado × Laboratorio × Dia Venda)
6. 3 períodos comparativos: Set/26 (atual), Ago/26 (M-1), Set/25 (SPLY YoY)
"""
import os
import sys
import time
import json
import asyncio

if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

STORAGE_STATE_PATH = os.path.join(DATA_DIR, 'qlik_cloud_storage_state.json')

QLIK_CLOUD_HOST = "fsj.us.qlikcloud.com"
APP_ID = "dcfc3ede-5eab-407c-a9ce-12b546eb5bdf"  # Vendas Análise - Analítico
HOME_URL = f"https://{QLIK_CLOUD_HOST}/analytics/home"

USERNAME = "lucas.alves6"
PASSWORD = "Eloise2025*"

DIGITAL_CHANNELS_FILTER = "'APP', 'APP Tele Entrega', 'APP TELE ENTREGA', 'SITE', 'SITE Tele Entrega', 'SITE TELE ENTREGA', 'iFood', 'IFOOD', 'e_Commerce', 'E_COMMERCE', 'E-COMMERCE', 'RAPPI', 'Rappi', 'MERCADO LIVRE', 'Mercado Livre', 'Figital', 'FIGITAL'"

async def fetch_qlik_cloud_data():
    t0 = time.time()
    print("=" * 70)
    print("  EXTRAÇÃO DE CANAIS DIGITAIS — QLIK CLOUD (SaaS)")
    print("=" * 70)

    results = {}

    try:
        print("1/3 Conectando ao Qlik Cloud via Playwright...", flush=True)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Reutiliza estado de sessão se existir
            context_args = {
                'viewport': {'width': 1280, 'height': 800},
                'ignore_https_errors': True
            }
            if os.path.exists(STORAGE_STATE_PATH):
                try:
                    context = await browser.new_context(storage_state=STORAGE_STATE_PATH, **context_args)
                except Exception:
                    context = await browser.new_context(**context_args)
            else:
                context = await browser.new_context(**context_args)

            page = await context.new_page()
            print(f"Navegando para o Qlik Cloud ({HOME_URL})...", flush=True)
            await page.goto(HOME_URL, timeout=60000)

            # Aguarda eventual redirecionamento para o Keycloak SSO
            try:
                await page.wait_for_url(lambda u: "idp.farmaciassaojoao.com.br" in u or f"{QLIK_CLOUD_HOST}/analytics" in u, timeout=20000)
            except Exception:
                pass
            await page.wait_for_timeout(2000)

            if "idp.farmaciassaojoao.com.br" in page.url:
                print("Identificado Keycloak SSO. Autenticando com credenciais de rede...", flush=True)
                await page.fill('#username', USERNAME)
                await page.fill('#password', PASSWORD)
                await page.click('#kc-login')
                print("Aguardando retorno para o Qlik Cloud...", flush=True)
                await page.wait_for_url(f"**{QLIK_CLOUD_HOST}/analytics/**", timeout=60000)
                await page.wait_for_timeout(3000)
                print("Autenticação no Keycloak concluída com sucesso!", flush=True)
                await context.storage_state(path=STORAGE_STATE_PATH)

            print("2/3 Executando consultas no QIX Engine API via WebSocket...", flush=True)
            queries_js = f"""async () => {{
                const appId = "{APP_ID}";
                const csrfRes = await fetch('/api/v1/csrf-token');
                const csrfToken = csrfRes.headers.get('qlik-csrf-token');
                const wsUrl = `wss://${{window.location.host}}/app/${{encodeURIComponent(appId)}}?qlik-csrf-token=${{csrfToken}}`;

                return new Promise((resolve, reject) => {{
                    const ws = new WebSocket(wsUrl);
                    let docHandle = null;
                    const resData = {{}};
                    let msgId = 1;
                    const pending = {{}};

                    function send(method, handle, params) {{
                        return new Promise((res, rej) => {{
                            const id = msgId++;
                            pending[id] = {{ res, rej }};
                            ws.send(JSON.stringify({{ "jsonrpc": "2.0", "id": id, "method": method, "handle": handle, "params": params }}));
                        }});
                    }}

                    async function fetchAllHyperCubeRows(objHandle, totalRows, qWidth, pageSize) {{
                        let rows = [];
                        let top = 0;
                        while (top < totalRows) {{
                            const height = Math.min(pageSize, totalRows - top);
                            const pageRes = await send("GetHyperCubeData", objHandle, ["/qHyperCubeDef", [{{ "qTop": top, "qLeft": 0, "qHeight": height, "qWidth": qWidth }}]]);
                            const matrix = pageRes.result.qDataPages[0]?.qMatrix || [];
                            if (matrix.length === 0) break;
                            matrix.forEach(r => rows.push(r.map(c => c.qNum !== 'NaN' && typeof c.qNum === 'number' ? c.qNum : c.qText)));
                            top += matrix.length;
                        }}
                        return rows;
                    }}

                    ws.onopen = async () => {{
                        try {{
                            const openRes = await send("OpenDoc", -1, [appId]);
                            docHandle = openRes.result.qReturn.qHandle;

                            // 1. Canais Digitais x Dia (Set/26, Ago/26, Set/25)
                            const c1 = await send("CreateSessionObject", docHandle, [{{
                                "qInfo": {{ "qType": "q_digital_canais_dia" }},
                                "qHyperCubeDef": {{
                                    "qDimensions": [
                                        {{ "qDef": {{ "qFieldDefs": ["Canal Detalhado"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Dia Venda"] }} }}
                                    ],
                                    "qMeasures": [
                                        {{ "qDef": {{ "qDef": "Sum({{1<[Ano-Mês Venda]={{'2026-09'}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])", "qLabel": "v26_09" }} }},
                                        {{ "qDef": {{ "qDef": "Sum({{1<[Ano-Mês Venda]={{'2026-08'}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])", "qLabel": "v26_08" }} }},
                                        {{ "qDef": {{ "qDef": "Sum({{1<[Ano-Mês Venda]={{'2025-09'}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])", "qLabel": "v25_09" }} }}
                                    ],
                                    "qInitialDataFetch": [{{ "qTop": 0, "qLeft": 0, "qHeight": 1000, "qWidth": 5 }}],
                                    "qSuppressZero": true, "qSuppressMissing": true
                                }}
                            }}]);
                            const h1 = c1.result.qReturn.qHandle;
                            const l1 = await send("GetLayout", h1, []);
                            resData.canais_dia = (l1.result.qLayout.qHyperCube.qDataPages[0]?.qMatrix || []).map(r => r.map(c => c.qNum !== 'NaN' && typeof c.qNum === 'number' ? c.qNum : c.qText));

                            // Descobrir max dia com venda
                            const diasComVenda = new Set();
                            resData.canais_dia.forEach(r => {{
                                if (typeof r[2] === 'number' && r[2] > 0) diasComVenda.add(Number(r[1]));
                            }});
                            const rawMaxDia = diasComVenda.size > 0 ? Math.max(...Array.from(diasComVenda)) : 1;
                            const today = new Date().getDate();
                            const d_minus_1 = today > 1 ? today - 1 : 1;
                            const maxDia = Math.max(1, Math.min(rawMaxDia, d_minus_1));
                            const dayFilter = `[Dia Venda]={{"<=${{maxDia}}"}}`;
                            resData.maxDia = maxDia;

                            // Zera qualquer venda de 2026 para dias > maxDia (dias parciais/incompletos)
                            resData.canais_dia.forEach(r => {{
                                if (Number(r[1]) > maxDia) {{
                                    r[2] = 0;
                                }}
                            }});

                            // 2. Hierarquia Digital (Canal x Grupo x Subgrupo x Linha MTD)
                            const c2 = await send("CreateSessionObject", docHandle, [{{
                                "qInfo": {{ "qType": "q_digital_hierarquia" }},
                                "qHyperCubeDef": {{
                                    "qDimensions": [
                                        {{ "qDef": {{ "qFieldDefs": ["Canal Detalhado"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Desc_Grupo"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Desc_Subgrupo"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Desc_Linha"] }} }}
                                    ],
                                    "qMeasures": [
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2026-09'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v26" }} }},
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2026-08'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v26_06" }} }},
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2025-09'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v25" }} }}
                                    ],
                                    "qInitialDataFetch": [{{ "qTop": 0, "qLeft": 0, "qHeight": 1000, "qWidth": 7 }}],
                                    "qSuppressZero": true, "qSuppressMissing": true
                                }}
                            }}]);
                            const h2 = c2.result.qReturn.qHandle;
                            const l2 = await send("GetLayout", h2, []);
                            const totalRows2 = l2.result.qLayout.qHyperCube.qSize.qcy;
                            resData.hierarquia = await fetchAllHyperCubeRows(h2, totalRows2, 7, 1000);

                            // 3. Laboratórios / Fornecedores Digital (Canal x Laboratorio MTD)
                            const c3 = await send("CreateSessionObject", docHandle, [{{
                                "qInfo": {{ "qType": "q_digital_labs" }},
                                "qHyperCubeDef": {{
                                    "qDimensions": [
                                        {{ "qDef": {{ "qFieldDefs": ["Canal Detalhado"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Laboratorio"] }} }}
                                    ],
                                    "qMeasures": [
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2026-09'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v26" }} }},
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2026-08'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v26_06" }} }},
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2025-09'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v25" }} }}
                                    ],
                                    "qInitialDataFetch": [{{ "qTop": 0, "qLeft": 0, "qHeight": 1000, "qWidth": 5 }}],
                                    "qSuppressZero": true, "qSuppressMissing": true
                                }}
                            }}]);
                            const h3 = c3.result.qReturn.qHandle;
                            const l3 = await send("GetLayout", h3, []);
                            const totalRows3 = l3.result.qLayout.qHyperCube.qSize.qcy;
                            resData.laboratorios = await fetchAllHyperCubeRows(h3, totalRows3, 5, 1000);

                            // 4. Hierarquia Diária (Canal x Linha x Dia)
                            const c4 = await send("CreateSessionObject", docHandle, [{{
                                "qInfo": {{ "qType": "q_digital_linhas_dia" }},
                                "qHyperCubeDef": {{
                                    "qDimensions": [
                                        {{ "qDef": {{ "qFieldDefs": ["Canal Detalhado"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Desc_Linha"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Dia Venda"] }} }}
                                    ],
                                    "qMeasures": [
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2026-09'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v26_dia" }} }}
                                    ],
                                    "qInitialDataFetch": [{{ "qTop": 0, "qLeft": 0, "qHeight": 1000, "qWidth": 4 }}],
                                    "qSuppressZero": true, "qSuppressMissing": true
                                }}
                            }}]);
                            const h4 = c4.result.qReturn.qHandle;
                            const l4 = await send("GetLayout", h4, []);
                            const totalRows4 = l4.result.qLayout.qHyperCube.qSize.qcy;
                            resData.linhas_dia = await fetchAllHyperCubeRows(h4, totalRows4, 4, 1000);

                            // 5. Fornecedores / Laboratórios Diários (Canal x Laboratório x Dia)
                            const c5 = await send("CreateSessionObject", docHandle, [{{
                                "qInfo": {{ "qType": "q_digital_labs_dia" }},
                                "qHyperCubeDef": {{
                                    "qDimensions": [
                                        {{ "qDef": {{ "qFieldDefs": ["Canal Detalhado"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Laboratorio"] }} }},
                                        {{ "qDef": {{ "qFieldDefs": ["Dia Venda"] }} }}
                                    ],
                                    "qMeasures": [
                                        {{ "qDef": {{ "qDef": `Sum({{1<[Ano-Mês Venda]={{'2026-09'}}, ${{dayFilter}}, [Canal Detalhado]={{{DIGITAL_CHANNELS_FILTER}}}>}} [Vl_Mercadoria])`, "qLabel": "v26_dia" }} }}
                                    ],
                                    "qInitialDataFetch": [{{ "qTop": 0, "qLeft": 0, "qHeight": 1000, "qWidth": 4 }}],
                                    "qSuppressZero": true, "qSuppressMissing": true
                                }}
                            }}]);
                            const h5 = c5.result.qReturn.qHandle;
                            const l5 = await send("GetLayout", h5, []);
                            const totalRows5 = l5.result.qLayout.qHyperCube.qSize.qcy;
                            resData.laboratorios_dia = await fetchAllHyperCubeRows(h5, totalRows5, 4, 1000);

                            ws.close();
                            resolve(resData);
                        }} catch (e) {{
                            ws.close();
                            reject(new Error(e.message || String(e)));
                        }}
                    }};

                    ws.onmessage = (event) => {{
                        const msg = JSON.parse(event.data);
                        if (msg.id && pending[msg.id]) {{
                            const {{ res, rej }} = pending[msg.id];
                            delete pending[msg.id];
                            if (msg.error) rej(new Error(JSON.stringify(msg.error)));
                            else res(msg);
                        }}
                    }};

                    setTimeout(() => {{
                        try {{ ws.close(); }} catch(e) {{}}
                        resolve(null);
                    }}, 90000);
                }});
            }};"""

            results = await page.evaluate(queries_js)
            await browser.close()

            if results and 'canais_dia' in results:
                results['origem'] = 'Qlik Cloud Engine (Sincronizado)'
                print(f"✅ Extração direta Qlik Cloud concluída em {time.time() - t0:.2f}s!", flush=True)
            else:
                print("⚠️ Retorno vazio ou timeout no WebSocket. Ativando sincronizador resiliente...", flush=True)
                results = load_fallback_data()

    except Exception as e:
        print(f"⚠️ Nota de conexão com Qlik Cloud: {e}")
        print("Ativando sincronizador resiliente...", flush=True)
        results = load_fallback_data()

    # Salva os dados brutos extraídos
    output_path = os.path.join(DATA_DIR, 'qlik_digital_raw.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ Dados Qlik Cloud brutos salvos em: {output_path}")
    return results

def load_fallback_data():
    """Carrega dados da extração recente para garantir continuidade em caso de indisponibilidade."""
    fallback_hier = r"c:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\dashboard-acompanhamento-categorias\data\setembro\canais_by_hierarquia.json"
    fallback_canais = r"c:\Users\lucas.alves6\OneDrive - Farmácias São João\Documentos\ANTIGRAVITI\dashboard-acompanhamento-categorias\data\setembro\canais_summary.json"

    digital_canais_set = {'APP', 'APP TELE ENTREGA', 'SITE', 'SITE TELE ENTREGA', 'IFOOD', 'RAPPI', 'E_COMMERCE', 'E-COMMERCE'}
    
    hier_rows = []
    if os.path.exists(fallback_hier):
        with open(fallback_hier, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        for r in raw:
            c = str(r.get('canal', '')).strip().upper()
            if c in digital_canais_set:
                hier_rows.append([
                    r.get('canal'),
                    r.get('grupo'),
                    r.get('subgrupo'),
                    r.get('linha'),
                    float(r.get('v26', 0) or 0),
                    float(r.get('v26_06', 0) or 0),
                    float(r.get('v25', 0) or 0)
                ])

    canais_dia_rows = []
    if os.path.exists(fallback_canais):
        with open(fallback_canais, 'r', encoding='utf-8') as f:
            cdata = json.load(f)
        for c in cdata:
            name = str(c.get('canal', '')).strip().upper()
            if name in digital_canais_set:
                d26 = c.get('d26_07', [])
                d26_06 = c.get('d26_06', [])
                d25 = c.get('d25', [])
                for d_idx in range(len(d26)):
                    v26 = d26[d_idx] if d_idx < len(d26) else 0.0
                    v26_06 = d26_06[d_idx] if d_idx < len(d26_06) else 0.0
                    v25_val = d25[d_idx] if d_idx < len(d25) else 0.0
                    if v26 > 0 or v26_06 > 0 or v25_val > 0:
                        canais_dia_rows.append([c.get('canal'), d_idx + 1, v26, v26_06, v25_val])

    import datetime
    today = datetime.datetime.now().day
    d_minus_1 = today - 1 if today > 1 else 1

    dias_com_venda = [r[1] for r in canais_dia_rows if float(r[2] or 0) > 0 and r[1] <= d_minus_1]
    raw_max = max(dias_com_venda) if dias_com_venda else d_minus_1
    computed_max = min(raw_max, d_minus_1)

    for row in canais_dia_rows:
        if row[1] > computed_max:
            row[2] = 0.0

    return {
        'canais_dia': canais_dia_rows,
        'hierarquia': hier_rows,
        'maxDia': computed_max,
        'origem': 'Data Lake Local (Fallback)'
    }

if __name__ == '__main__':
    asyncio.run(fetch_qlik_cloud_data())
