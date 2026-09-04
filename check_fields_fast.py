import os, sys, asyncio, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

QLIK_URL = "https://sense.farmaciassaojoao.com.br"
APP_ID = "671fa4f4-eb7d-418f-b4c9-936e87d8011d"
SHEET_ID = "ddd70c77-1a06-40d9-aff2-efa4b6b67b24"
SHEET_URL = f"{QLIK_URL}/sense/app/{APP_ID}/sheet/{SHEET_ID}/state/analysis"
USERNAME = "lucas.alves6"
PASSWORD = "Eloise2025*"

async def check_fields():
    async with async_playwright() as p:
        print("1. Conectando ao Qlik Sense...", flush=True)
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            http_credentials={'username': USERNAME, 'password': PASSWORD},
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        await page.goto(SHEET_URL, timeout=45000)
        try:
            await page.wait_for_selector('.qv-panel-sheet', timeout=30000)
        except Exception:
            await page.wait_for_timeout(8000)
        await page.wait_for_timeout(4000)
        
        print("2. Consultando lista de campos (GetFieldList)...", flush=True)
        res = await page.evaluate('''async () => {
            const appId = "671fa4f4-eb7d-418f-b4c9-936e87d8011d";
            const wsUrl = `wss://${window.location.host}/app/${encodeURIComponent(appId)}?reloadUri=https://${window.location.host}/`;
            return new Promise((resolve, reject) => {
                const ws = new WebSocket(wsUrl);
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
                        const openRes = await send("OpenDoc", -1, [appId]);
                        const docHandle = openRes.result.qReturn.qHandle;
                        
                        // Obter lista rápida de campos via CreateSessionObject com FieldList
                        const flObj = await send("CreateSessionObject", docHandle, [{
                            "qInfo": { "qType": "FieldList" },
                            "qFieldListDef": { "qShowSystem": false, "qShowHidden": true }
                        }]);
                        const flHandle = flObj.result.qReturn.qHandle;
                        const flLayout = await send("GetLayout", flHandle, []);
                        const fields = (flLayout.result.qLayout.qFieldList.qItems || []).map(f => f.qName);
                        
                        // Também testar Canais únicos com venda em Set/26
                        const cCanal = await send("CreateSessionObject", docHandle, [{
                            "qInfo": { "qType": "q_canais" },
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

                        ws.close();
                        resolve({ fields, canais });
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
        }''')
        await browser.close()
        return res

if __name__ == '__main__':
    data = asyncio.run(check_fields())
    fields = data['fields']
    print(f"\n✅ Total de campos no App ({len(fields)}):")
    print(sorted(fields))
    print("\n✅ Canais no App:")
    for c in data['canais']:
        print(f"  - {c['canal']:30s} | Set/26: R$ {c['v26_09']:15,.2f} | Ago/26: R$ {c['v26_08']:15,.2f}")
