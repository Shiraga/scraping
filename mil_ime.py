import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import pandas as pd

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter as variáveis do ambiente
INITIAL_URL = os.getenv('INITIAL_URL')
CPF = os.getenv('CPF')
SENHA = os.getenv('SENHA')
REDIRECT_URL = os.getenv('REDIRECT_URL')
CURSO_DESEJADO = os.getenv('CURSO_DESEJADO')

async def selecionar_opcao(page, seletor, valor):
    try:
        await page.select_option(seletor, valor)
        print(f"Selecionada a opção {valor} para o seletor {seletor}")
    except Exception as e:
        print(f"Erro ao selecionar opção: {e}")

async def mudar_paginacao(page, tabela_nome):
    try:
        dropdown_selector = f"select[name='{tabela_nome}_length']"
        await page.select_option(dropdown_selector, "100")
        print(f"Alterada a paginação para 100 resultados em {tabela_nome}")
    except Exception as e:
        print(f"Erro ao alterar paginação: {e}")

async def extrair_dados(page, tabela_id, situacao):
    try:
        rows = await page.query_selector_all(f"#{tabela_id} tbody tr")
        dados = []
        for row in rows:
            cols = await row.query_selector_all("td")
            col_values = [await col.inner_text() for col in cols]
            col_values.append(situacao)
            dados.append(col_values)
        return dados
    except Exception as e:
        print(f"Erro ao extrair dados da tabela {tabela_id}: {e}")
        return []

async def obter_anos_disponiveis(page):
    try:
        options = await page.query_selector_all("#ano option")
        anos = [await option.get_attribute("value") for option in options if await option.get_attribute("value")]
        print(f"Anos disponíveis: {anos}")
        return anos
    except Exception as e:
        print(f"Erro ao obter anos disponíveis: {e}")
        return []

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

        # Resolver CAPTCHA se necessário
        await page.wait_for_selector('img[src^="/captcha/"]', timeout=15000)
        captcha_image_path = "captcha_image.png"
        await page.locator('img[src^="/captcha/"]').screenshot(path=captcha_image_path)
        print(f"CAPTCHA image saved as {captcha_image_path}")
        captcha_text = input("Enter the CAPTCHA text: ")
        await page.fill("input[name='captcha[input]']", captcha_text)
        await page.click("input[type='submit']")

        # Redirecionar manualmente
        await page.goto(REDIRECT_URL)

        # Obter os anos disponíveis no seletor de anos
        anos_disponiveis = await obter_anos_disponiveis(page)

        # DataFrame para consolidar os dados
        all_data = []
        falhas_consecutivas = 0

        for ano in anos_disponiveis:
            #if ano == "2024" or int(ano) < 1990:
            if ano == "2024" or int(ano) < 2022:
                print(f"Pulando o ano: {ano}")
                continue

            print(f"Iniciando extração para o ano: {ano}")

            try:
                # Passo 1: Selecionar o ano
                await selecionar_opcao(page, "#ano", ano)

                # Passo 2: Selecionar o curso
                await selecionar_opcao(page, "#curso", CURSO_DESEJADO)

                # Passo 3: Clicar no botão de procurar
                await page.click("input[type='submit']")
                await page.wait_for_selector("#listTable", timeout=15000)

                # Passo 4: Alterar paginação para 100 resultados na tabela 'Ativa'
                await mudar_paginacao(page, "listTable")

                # Passo 5: Alterar paginação para 100 resultados na tabela 'Excluídos'
                await mudar_paginacao(page, "listTable3")

                # Passo 6: Extrair dados das tabelas
                dados_ativa = await extrair_dados(page, "listTable", "Ativa")
                dados_excluidos = await extrair_dados(page, "listTable3", "Excluído")

                # Adicionar uma coluna com o ano
                for linha in dados_ativa:
                    linha.append(ano)
                for linha in dados_excluidos:
                    linha.append(ano)

                # Consolidar os dados
                all_data.extend(dados_ativa)
                all_data.extend(dados_excluidos)

                falhas_consecutivas = 0  # Resetar contador de falhas em caso de sucesso

            except Exception as e:
                print(f"Erro ao processar o ano {ano}: {e}")
                falhas_consecutivas += 1

                if falhas_consecutivas > 3:
                    print("Falhas consecutivas excederam o limite. Interrompendo o código.")
                    break

        colunas = ["Posto/Graduação", "Nome", "OM/Data", "Email/Motivo", "Situação", "Ano"]
        df = pd.DataFrame(all_data, columns=colunas)

        #print(df.sample(n=5))

        # Dividir a coluna "OM/Data" em "OM" e "Data" com base na Situação
        df["OM"] = df.apply(lambda row: row["OM/Data"] if row["Situação"] == "Ativa" else "", axis=1)
        df["Data"] = df.apply(lambda row: row["OM/Data"] if row["Situação"] == "Excluído" else "", axis=1)
        df.drop(columns=["OM/Data"], inplace=True)

        # Dividir a coluna "Email/Motivo" em "Email" e "Motivo" com base na Situação
        df["Email"] = df.apply(lambda row: row["Email/Motivo"] if row["Situação"] == "Ativa" else "", axis=1)
        df["Motivo"] = df.apply(lambda row: row["Email/Motivo"] if row["Situação"] == "Excluído" else "", axis=1)
        df.drop(columns=["Email/Motivo"], inplace=True)

        # Salvar o DataFrame final em um arquivo Excel
        df.to_excel("dados_militares_todos_anos.xlsx", index=False)
        print("Dados salvos em 'dados_militares_todos_anos.xlsx'.")

        # Fechar o navegador
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
