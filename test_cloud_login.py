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
        await page.goto(QLIK_CLOUD_URL, timeout=60000)
        
        # Verifica se caiu ou está indo para o Keycloak SSO aguardando o input #username
        print("Verificando necessidade de login SSO...")
        try:
            user_input = await page.wait_for_selector('#username', timeout=15000)
            if user_input:
                print("Identificado formulário do Keycloak SSO. Preenchendo credenciais...")
                await page.fill('#username', USERNAME)
                await page.fill('#password', PASSWORD)
                await page.click('#kc-login')
                print("Credenciais enviadas. Aguardando retorno ao Qlik Cloud...")
                await page.wait_for_url("**/analytics/**", timeout=60000)
                print("✅ Login SSO concluído com sucesso!")
        except Exception as e:
            print("Formulário de login não solicitado ou já logado:", e)

        print("Aguardando estabilização da página do Qlik Cloud...")
        await page.wait_for_timeout(5000)
        print("URL final:", page.url)
        
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
