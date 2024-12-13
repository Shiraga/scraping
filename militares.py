import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from PIL import Image

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter as variáveis do ambiente
INITIAL_URL = os.getenv('INITIAL_URL')
CPF = os.getenv('CPF')
SENHA = os.getenv('SENHA')

async def capture_captcha_image(page, captcha_selector):
    # Captura a imagem do CAPTCHA
    captcha_image_path = "captcha_image.png"
    await page.locator(captcha_selector).screenshot(path=captcha_image_path)
    print(f"CAPTCHA image saved as {captcha_image_path}")
    return captcha_image_path

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

        # Capturar a imagem do CAPTCHA
        captcha_image_path = await capture_captcha_image(page, 'img[src^="/captcha/"]')

        # Exibir a imagem para o usuário
        print(f"Please solve the CAPTCHA in the image below: {captcha_image_path}")

        # Solicitar que o usuário insira o texto do CAPTCHA
        captcha_text = input("Enter the CAPTCHA text: ")

        # Inserir o texto do CAPTCHA no campo correspondente
        await page.fill("input[name='captcha[input]']", captcha_text)

        # Clicar no botão de login (descomentado se necessário)
        await page.click("input[type='submit']")

        # Aguarde para verificar o resultado
        await page.wait_for_timeout(10000)

        # Fechar o navegador
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
