import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from PIL import Image
import pytesseract

# Configurar o caminho do executável do Tesseract (ajuste conforme necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\mathe\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter as variáveis do ambiente
INITIAL_URL = os.getenv('INITIAL_URL')
CPF = os.getenv('CPF')
SENHA = os.getenv('SENHA')

async def solve_captcha(page, captcha_selector):
    # Captura a imagem do CAPTCHA
    captcha_image_path = "captcha_image.png"
    await page.locator(captcha_selector).screenshot(path=captcha_image_path)

    # Usar o Tesseract OCR para extrair o texto
    captcha_image = Image.open(captcha_image_path)
    captcha_text = pytesseract.image_to_string(captcha_image, config="--psm 8")

    # Exibir o texto extraído
    print(f"CAPTCHA Resolvido: {captcha_text}")
    return captcha_text.strip()

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navegar para a URL inicial
        await page.goto(INITIAL_URL)

        # Preencher CPF e senha
        await page.fill("input[name='cpf']", CPF)
        await page.fill("input[name='senha']", SENHA)

        # Esperar até 15 segundos para o CAPTCHA ser carregado
        await page.wait_for_selector('img[src^="/captcha/"]', timeout=15000)

        # Resolver o CAPTCHA
        captcha_text = await solve_captcha(page, 'img[src^="/captcha/"]')

        # Inserir o texto do CAPTCHA no campo correspondente
        await page.fill("input[name='captcha[input]']", captcha_text)

        # Clicar no botão de login
        #await page.click("button[type='submit']")

        # Aguarde para verificar o resultado
        await page.wait_for_timeout(10000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
