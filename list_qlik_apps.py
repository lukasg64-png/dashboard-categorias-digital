import os, sys, asyncio, json
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

QLIK_URL = "https://sense.farmaciassaojoao.com.br"
USERNAME = "lucas.alves6"
PASSWORD = "Eloise2025*"

async def list_apps():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            http_credentials={'username': USERNAME, 'password': PASSWORD},
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        print("Conectando ao Qlik Hub...", flush=True)
        await page.goto(f"{QLIK_URL}/hub/", timeout=60000)
        try:
            await page.wait_for_selector('.hub-stream', timeout=20000)
        except Exception:
            await page.wait_for_timeout(8000)
        
        apps = await page.evaluate('''async () => {
            const wsUrl = `wss://${window.location.host}/app/%3Ftransient%3D?reloadUri=https://${window.location.host}/`;
            return new Promise((resolve) => {
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
                        const docListRes = await send("GetDocList", -1, []);
                        ws.close();
                        resolve(docListRes.result.qDocList || []);
                    } catch(e) {
                        ws.close();
                        resolve({ error: e.toString() });
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
                setTimeout(() => { ws.close(); resolve({ error: 'timeout' }); }, 15000);
            });
        }''')
        await browser.close()
        return apps

if __name__ == '__main__':
    doc_list = asyncio.run(list_apps())
    print(f"Total apps encontrados: {len(doc_list) if isinstance(doc_list, list) else doc_list}")
    if isinstance(doc_list, list):
        for app in sorted(doc_list, key=lambda x: x.get('qTitle', '')):
            title = app.get('qTitle', '')
            app_id = app.get('qDocId', '')
            if any(k in title.lower() for k in ['dig', 'venda', 'cat', 'ecommerce', 'e-comm', 'app', 'site', 'market', 'sku']):
                print(f"  ⭐ {title:45s} | ID: {app_id}")
            else:
                print(f"     {title:45s} | ID: {app_id}")
