import os, sys, asyncio, json, time
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

QLIK_URL = "https://sense.farmaciassaojoao.com.br"
APP_ID = "671fa4f4-eb7d-418f-b4c9-936e87d8011d"
SHEET_ID = "ddd70c77-1a06-40d9-aff2-efa4b6b67b24"
SHEET_URL = f"{QLIK_URL}/sense/app/{APP_ID}/sheet/{SHEET_ID}/state/analysis"
USERNAME = "lucas.alves6"
PASSWORD = "Eloise2025*"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            http_credentials={'username': USERNAME, 'password': PASSWORD},
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        print("1. Conectando ao Qlik Sense...", flush=True)
        await page.goto(SHEET_URL, timeout=60000)
        await page.wait_for_timeout(8000)
        
        print("2. Testando canais e dimensões no Qlik...", flush=True)
        t0 = time.time()
        result = await page.evaluate('''async () => {
            const wsUrl = `wss://${window.location.host}/app/${window.location.pathname.split('/app/')[1].split('/')[0]}`;
            
            return new Promise((resolve) => {
                const ws = new WebSocket(wsUrl);
                let docHandle = null;
                let sessionHandle = null;
                
                ws.onopen = () => {
                    ws.send(JSON.stringify({
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "OpenDoc",
                        "handle": -1,
                        "params": [window.location.pathname.split('/app/')[1].split('/')[0]]
                    }));
                };
                
                ws.onmessage = async (event) => {
                    const msg = JSON.parse(event.data);
                    
                    if (msg.id === 1 && msg.result) {
                        docHandle = msg.result.qReturn.qHandle;
                        
                        // 1. Hypercube de Canais x Venda Set/26 e Ago/26
                        ws.send(JSON.stringify({
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "CreateSessionObject",
                            "handle": docHandle,
                            "params": [{
                                "qInfo": { "qType": "canais_test" },
                                "qHyperCubeDef": {
                                    "qDimensions": [
                                        { "qDef": { "qFieldDefs": ["Canal"] } }
                                    ],
                                    "qMeasures": [
                                        { "qDef": { "qDef": "Sum({1<[Ano-Mes]={'2026-09'}>} [Receita Líquida])", "qLabel": "Venda_Set_26" } },
                                        { "qDef": { "qDef": "Sum({1<[Ano-Mes]={'2026-08'}>} [Receita Líquida])", "qLabel": "Venda_Ago_26" } },
                                        { "qDef": { "qDef": "Sum({1<[Ano-Mes]={'2025-09'}>} [Receita Líquida])", "qLabel": "Venda_Set_25" } }
                                    ],
                                    "qInitialDataFetch": [{
                                        "qTop": 0, "qLeft": 0, "qHeight": 50, "qWidth": 4
                                    }],
                                    "qSuppressZero": false
                                }
                            }]
                        }));
                    } else if (msg.id === 2 && msg.result) {
                        sessionHandle = msg.result.qReturn.qHandle;
                        
                        ws.send(JSON.stringify({
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "GetLayout",
                            "handle": sessionHandle,
                            "params": []
                        }));
                    } else if (msg.id === 3 && msg.result) {
                        const layout = msg.result.qLayout;
                        const hc = layout.qHyperCube;
                        const rows = (hc.qDataPages[0]?.qMatrix || []).map(row => ({
                            canal: row[0].qText,
                            vSet26: row[1].qNum !== 'NaN' && typeof row[1].qNum === 'number' ? row[1].qNum : 0,
                            vAgo26: row[2].qNum !== 'NaN' && typeof row[2].qNum === 'number' ? row[2].qNum : 0,
                            vSet25: row[3].qNum !== 'NaN' && typeof row[3].qNum === 'number' ? row[3].qNum : 0
                        }));
                        
                        resolve({ canais: rows });
                        ws.close();
                    } else if (msg.error) {
                        resolve({ error: msg.error });
                        ws.close();
                    }
                };
                
                ws.onerror = (e) => resolve({ error: 'ws error' });
                setTimeout(() => resolve({ error: 'timeout' }), 25000);
            });
        }''')
        
        print(f"✅ Executado em {time.time() - t0:.2f}s!", flush=True)
        await browser.close()
        return result

if __name__ == '__main__':
    res = asyncio.run(main())
    print("\nRESULTADO CANAIS:")
    if 'canais' in res:
        for c in res['canais']:
            print(f"  {c['canal']:30s} | Set/26: R$ {c['vSet26']:12,.2f} | Ago/26: R$ {c['vAgo26']:12,.2f} | Set/25: R$ {c['vSet25']:12,.2f}")
    else:
        print(res)
