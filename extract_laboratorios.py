"""
extract_laboratorios.py — Extrai vendas por Canal × Laboratório do Qlik Sense
Para alimentar a visão de Fornecedores / Laboratórios com MTD, MoM e YoY.
"""
import os, sys, time, json, asyncio
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

USERNAME = 'lucas.alves6'
PASSWORD = 'Eloise2025*'
APP_ID = '671fa4f4-eb7d-418f-b4c9-936e87d8011d'
SHEET_ID = 'ddd70c77-1a06-40d9-aff2-efa4b6b67b24'
SHEET_URL = f'https://sense.farmaciassaojoao.com.br/sense/app/{APP_ID}/sheet/{SHEET_ID}/state/analysis'

async def fetch_labs():
    t0 = time.time()
    print("1/2 Conectando ao Qlik Sense para extrair Laboratórios...", flush=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(ignore_https_errors=True, http_credentials={'username': USERNAME, 'password': PASSWORD})
        page = await context.new_page()
        await page.goto(SHEET_URL, timeout=50000)
        try:
            await page.wait_for_selector('.qv-panel-sheet', timeout=30000)
        except Exception:
            await page.wait_for_timeout(8000)
        await page.wait_for_timeout(3000)
        
        print("2/2 Consultando Canal x Laboratorio via QIX WebSocket...", flush=True)
        js = """async () => {
            const appId = '671fa4f4-eb7d-418f-b4c9-936e87d8011d';
            const wsUrl = `wss://${window.location.host}/app/${encodeURIComponent(appId)}?reloadUri=https://${window.location.host}/`;
            return new Promise((resolve, reject) => {
                const ws = new WebSocket(wsUrl);
                let id = 1;
                const pending = {};
                function send(m, h, p) {
                    return new Promise((res, rej) => {
                        const mid = id++;
                        pending[mid] = { res, rej };
                        ws.send(JSON.stringify({ jsonrpc: '2.0', id: mid, method: m, handle: h, params: p }));
                    });
                }
                async function fetchAllRows(h, total, w, size) {
                    let rows = [];
                    let top = 0;
                    while (top < total) {
                        const hgt = Math.min(size, total - top);
                        const r = await send('GetHyperCubeData', h, ['/qHyperCubeDef', [{ qTop: top, qLeft: 0, qHeight: hgt, qWidth: w }]]);
                        const matrix = r.result.qDataPages[0]?.qMatrix || [];
                        if (matrix.length === 0) break;
                        matrix.forEach(row => rows.push(row.map(c => c.qNum !== 'NaN' && typeof c.qNum === 'number' ? c.qNum : c.qText)));
                        top += matrix.length;
                    }
                    return rows;
                }
                ws.onopen = async () => {
                    try {
                        const openRes = await send('OpenDoc', -1, [appId]);
                        const docH = openRes.result.qReturn.qHandle;
                        const dayFilter = '[Dia]={"<=3"}';
                        const canalFilter = "[Canal]={'APP','APP Tele Entrega','SITE','SITE Tele Entrega','iFood','e_Commerce','Rappi'}";
                        console.log('Criando objeto q_labs...');
                        const c = await send('CreateSessionObject', docH, [{
                            qInfo: { qType: 'q_labs' },
                            qHyperCubeDef: {
                                qDimensions: [
                                    { qDef: { qFieldDefs: ['Canal'] } },
                                    { qDef: { qFieldDefs: ['Laboratorio'] } }
                                ],
                                qMeasures: [
                                    { qDef: { qDef: `Sum({1<[Ano-Mes]={'2026-09'}, ${dayFilter}, ${canalFilter}>} [Receita Líquida])` } },
                                    { qDef: { qDef: `Sum({1<[Ano-Mes]={'2026-08'}, ${dayFilter}, ${canalFilter}>} [Receita Líquida])` } },
                                    { qDef: { qDef: `Sum({1<[Ano-Mes]={'2025-09'}, ${dayFilter}, ${canalFilter}>} [Receita Líquida])` } }
                                ],
                                qInitialDataFetch: [{ qTop: 0, qLeft: 0, qHeight: 1000, qWidth: 5 }],
                                qSuppressZero: true, qSuppressMissing: true
                            }
                        }]);
                        const h = c.result.qReturn.qHandle;
                        const l = await send('GetLayout', h, []);
                        const total = l.result.qLayout.qHyperCube.qSize.qcy;
                        console.log('Total rows qcy:', total);
                        const rows = await fetchAllRows(h, total, 5, 1000);
                        ws.close();
                        resolve({ total, rows });
                    } catch(e) {
                        console.error('Erro:', e);
                        ws.close();
                        reject(e.toString());
                    }
                };
                ws.onmessage = (e) => {
                    const m = JSON.parse(e.data);
                    if (m.id && pending[m.id]) {
                        const { res, rej } = pending[m.id];
                        delete pending[m.id];
                        if (m.error) rej(m.error);
                        else res(m);
                    }
                };
            });
        }"""
        res = await page.evaluate(js)
        await browser.close()
        print(f"Extração de laboratórios finalizada em {time.time() - t0:.2f}s!")
        return res

if __name__ == '__main__':
    data = asyncio.run(fetch_labs())
    rows = data.get('rows', []) if isinstance(data, dict) else []
    print(f"✅ Total de linhas de Laboratório extraídas: {len(rows)}")
    if rows:
        out_file = os.path.join(DATA_DIR, 'qlik_laboratorios_raw.json')
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print(f"✅ Salvo em: {out_file}")
