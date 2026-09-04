import asyncio, json
from playwright.async_api import async_playwright

USERNAME = "lucas.alves6"
PASSWORD = "Eloise2025*"
QLIK_URL = "https://sense.farmaciassaojoao.com.br"
APP_ID = "671fa4f4-eb7d-418f-b4c9-936e87d8011d"
SHEET_ID = "ddd70c77-1a06-40d9-aff2-efa4b6b67b24"
SHEET_URL = f"{QLIK_URL}/sense/app/{APP_ID}/sheet/{SHEET_ID}/state/analysis"

async def test_qlik_schema():
    async with async_playwright() as p:
        print("1. Conectando ao Qlik Sense...")
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            http_credentials={'username': USERNAME, 'password': PASSWORD},
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        await page.goto(SHEET_URL, timeout=60000)
        try:
            await page.wait_for_selector('.qv-panel-sheet', timeout=30000)
        except Exception:
            await page.wait_for_timeout(8000)
        await page.wait_for_timeout(3000)

        print("2. Consultando campos e canais...")
        js_code = """async () => {
            const wsUrl = `wss://${window.location.host}/app/${encodeURIComponent('""" + APP_ID + """')}?reloadUri=https://${window.location.host}/`;
            return new Promise((resolve, reject) => {
                const ws = new WebSocket(wsUrl);
                let docHandle = null;
                let msgId = 1;
                const pending = {};
                function send(method, handle, params) {
                    return new Promise((res, rej) => {
                        const id = msgId++;
                        pending[id] = { res, rej };
                        ws.send(JSON.stringify({ "jsonrpc": "2.0", "id": id, "method": method, "handle": handle, "params": params }));
                    });
                }
                ws.onopen = async () => {
                    try {
                        const openRes = await send("OpenDoc", -1, [\"""" + APP_ID + """\"]);
                        docHandle = openRes.result.qReturn.qHandle;
                        
                        // Obter lista de campos
                        const fieldsRes = await send("GetTablesAndKeys", docHandle, [{"qcx": 0, "qcy": 0}, {"qcx": 0, "qcy": 0}, 0, false, false]);
                        
                        // Obter valores distintos de Canal e vendas em Set/26 e Ago/26
                        const cCanal = await send("CreateSessionObject", docHandle, [{
                            "qInfo": { "qType": "q_canal_test" },
                            "qHyperCubeDef": {
                                "qDimensions": [{ "qDef": { "qFieldDefs": ["Canal"] } }],
                                "qMeasures": [
                                    { "qDef": { "qDef": "Sum({1<[Ano-Mes]={'2026-09'}>} [Receita Líquida])" } },
                                    { "qDef": { "qDef": "Sum({1<[Ano-Mes]={'2026-08'}>} [Receita Líquida])" } }
                                ],
                                "qInitialDataFetch": [{ "qTop": 0, "qLeft": 0, "qHeight": 50, "qWidth": 3 }],
                                "qSuppressZero": false
                            }
                        }]);
                        const hCanal = cCanal.result.qReturn.qHandle;
                        const lCanal = await send("GetLayout", hCanal, []);
                        const mCanal = lCanal.result.qLayout.qHyperCube.qDataPages[0]?.qMatrix || [];
                        const canais = mCanal.map(r => ({
                            canal: r[0].qText,
                            v26_09: r[1].qNum !== 'NaN' && typeof r[1].qNum === 'number' ? r[1].qNum : 0,
                            v26_08: r[2].qNum !== 'NaN' && typeof r[2].qNum === 'number' ? r[2].qNum : 0
                        }));

                        // Checar dias com venda em Set/26
                        const cDias = await send("CreateSessionObject", docHandle, [{
                            "qInfo": { "qType": "q_dias_test" },
                            "qHyperCubeDef": {
                                "qDimensions": [{ "qDef": { "qFieldDefs": ["Dia"] } }],
                                "qMeasures": [
                                    { "qDef": { "qDef": "Sum({1<[Ano-Mes]={'2026-09'}>} [Receita Líquida])" } }
                                ],
                                "qInitialDataFetch": [{ "qTop": 0, "qLeft": 0, "qHeight": 40, "qWidth": 2 }],
                                "qSuppressZero": true
                            }
                        }]);
                        const hDias = cDias.result.qReturn.qHandle;
                        const lDias = await send("GetLayout", hDias, []);
                        const mDias = lDias.result.qLayout.qHyperCube.qDataPages[0]?.qMatrix || [];
                        const dias = mDias.map(r => ({
                            dia: r[0].qText,
                            venda: r[1].qNum !== 'NaN' && typeof r[1].qNum === 'number' ? r[1].qNum : 0
                        }));

                        ws.close();
                        resolve({
                            tables: fieldsRes.result.qtr.map(t => ({ name: t.qName, rows: t.qNoOfRows, fields: t.qFields.map(f => f.qName) })),
                            canais: canais,
                            dias: dias
                        });
                    } catch(e) {
                        ws.close();
                        reject(e.toString());
                    }
                };
                ws.onmessage = (event) => {
                    const msg = JSON.parse(event.data);
                    if (msg.id && pending[msg.id]) {
                        const { res, rej } = pending[msg.id];
                        delete pending[msg.id];
                        if (msg.error) rej(msg.error);
                        else res(msg);
                    }
                };
            });
        }"""
        data = await page.evaluate(js_code)
        await browser.close()
        return data

if __name__ == "__main__":
    result = asyncio.run(test_qlik_schema())
    print("\n=== TABELAS E CAMPOS NO QLIK ===")
    for t in result['tables']:
        print(f"\n📊 Tabela: {t['name']} ({t['rows']} linhas)")
        sku_fields = [f for f in t['fields'] if any(k in f.lower() for k in ['prod', 'sku', 'item', 'desc', 'lab', 'marca', 'grupo', 'linha'])]
        print(f"   Campos relevantes: {sku_fields}")
        if len(t['fields']) < 25:
            print(f"   Todos os campos: {t['fields']}")

    print("\n=== CANAIS E VENDAS NO QLIK ===")
    for c in result['canais']:
        print(f"  {c['canal']:30s} | Set/26: R$ {c['v26_09']:15,.2f} | Ago/26: R$ {c['v26_08']:15,.2f}")

    print("\n=== DIAS COM VENDA EM SETEMBRO/2026 ===")
    for d in sorted(result['dias'], key=lambda x: int(x['dia']) if x['dia'].isdigit() else 0):
        print(f"  Dia {d['dia']:2s}: R$ {d['venda']:15,.2f}")
