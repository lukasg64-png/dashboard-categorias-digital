import asyncio
import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

USERNAME = "lucas.alves6"
PASSWORD = "Eloise2025*"
QLIK_CLOUD_URL = "https://fsj.us.qlikcloud.com/analytics/home"

async def test_login():
    print("Iniciando teste de login Playwright no Qlik Cloud...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        print("Navegando para:", QLIK_CLOUD_URL)
        resp = await page.goto(QLIK_CLOUD_URL, timeout=60000)
        print("Aguardando carregamento da SPA / redirecionamento...")
        try:
            await page.wait_for_url(lambda u: "idp.farmaciassaojoao.com.br" in u or "/analytics/" in u, timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(3000)
        print("URL após carregamento inicial:", page.url)
        print("Título após carregamento:", await page.title())
        
        # Verifica se caiu no Keycloak SSO
        if "idp.farmaciassaojoao.com.br" in page.url:
            print("Identificado Keycloak SSO. Preenchendo credenciais...")
            await page.fill('#username', USERNAME)
            await page.fill('#password', PASSWORD)
            await page.click('#kc-login')
            
            print("Aguardando retorno para o Qlik Cloud...")
            await page.wait_for_url("**/analytics/**", timeout=60000)
            print("✅ Login concluído! URL pós-login:", page.url)
        else:
            print("Já autenticado ou redirecionamento direto:", page.url)
            
        # Testar obtenção do token CSRF
        csrf_token = await page.evaluate("""async () => {
            const r = await fetch('/api/v1/csrf-token');
            return r.headers.get('qlik-csrf-token');
        }""")
        print("✅ CSRF Token obtido com sucesso:", csrf_token)
        
        # Salvar estado para futuras execuções ultra-rápidas
        await context.storage_state(path="data/qlik_cloud_storage_state.json")
        print("✅ Estado da sessão salvo em data/qlik_cloud_storage_state.json!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())
