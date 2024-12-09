from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import csv

### Configuração do Selenium
driver_path = "C:/Users/mathe/chromedriver-win64/chromedriver.exe"
driver = webdriver.Chrome(service=Service(driver_path))

### URL base
base_url = "https://www.dfimoveis.com.br/venda/df/brasilia/imoveis"
#https://www.dfimoveis.com.br/venda/df/brasilia/asa-norte/imoveis
#https://www.dfimoveis.com.br/venda/df/brasilia/asa-sul/imoveis
#https://www.dfimoveis.com.br/venda/df/brasilia/lago-norte/imoveis
#https://www.dfimoveis.com.br/venda/df/brasilia/lago-sul/imoveis
#https://www.dfimoveis.com.br/venda/df/brasilia/noroeste/imoveis
#https://www.dfimoveis.com.br/venda/df/brasilia/park-sul/imoveis
#https://www.dfimoveis.com.br/venda/df/brasilia/sudoeste/imoveis

### Inicialização
pagina = 1
dados_imoveis = []

#while True:
while pagina <= 3:
    # Abrir a URL com paginação
    url = f"{base_url}?pagina={pagina}"
    print(f"Coletando dados da página {pagina}...")
    driver.get(url)
    
    ### Aguardar carregamento da página
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "new-card"))
        )
    except Exception as e:
        print(f"Erro ao carregar a página {pagina}: {e}")
        break

    ### Extrair o HTML renderizado
    soup = BeautifulSoup(driver.page_source, "html.parser")

    ### Encontrar os contêineres de imóveis
    imoveis = soup.find_all("div", class_="new-info")
    # Buscar separadamente
    #cards = soup.find_all("a", class_="new-card") # São um subconjunto de cards. Não são necessários.
    #infos = soup.find_all("div", class_="new-info")
    # Combinar os resultados
    #imoveis = cards + infos  # Junta as listas encontradas

    
    # Parar se não encontrar imóveis (fim das páginas)
    if not imoveis:
        print("Não há mais imóveis para coletar.")
        break

    # Extrair dados
    for imovel in imoveis:
        titulo = imovel.find("h2", class_="new-title phrase")
        desc1 = imovel.find("h3", class_="new-simple phrase")  # descrição simples
        desc2 = imovel.find("div", class_="new-text phrase") # descricao completa
        desc3 = imovel.find("h3", class_="new-desc phrase") # descricao ruim
        preco = imovel.find("div", class_="new-price")
        area = imovel.find("li", class_="m-area")
        details = imovel.find("ul", class_="new-details-ul") # contem info da area

        titulo_text = titulo.text.strip() if titulo else "Título não encontrado"
        preco_text = preco.text.strip() if preco else "Preço não encontrado"
        desc1_text = desc1.text.strip() if desc1 else "Descrição não encontrada"
        desc2_text = desc2.text.strip() if desc2 else "Descrição não encontrada"
        desc3_text = desc3.text.strip() if desc3 else "Descrição não encontrada"
        area_text = desc3.text.strip() if desc3 else "Área não encontrada"
        details_text = details.text.strip() if details else "Detalhes não encontrada"

        '''# Limpar o campo "Preço"
        if preco_text != "Preço não encontrado":
            preco_text = preco_text.split("\n")[0].strip()  # Pega apenas a primeira linha (o valor total)
        '''
        # Usar regex para extrair apenas os números (removendo R$, textos, etc.)
        preco_numerico = re.search(r"(\d[\d\.\,]*)", preco_text)
        preco_text = preco_numerico.group(1).replace(".", "").replace(",", ".") if preco_numerico else ""

        area_numerica = re.search(r"(\d[\d\.\,]*)", area_text)
        area_text = area_numerica.group(1).replace(".", "").replace(",", ".") if area_numerica else ""

        dados_imoveis.append({
            "Título": titulo_text,
            "Preço": preco_text,
            "Área": area_text,
            "Detalhes": details_text,
            "Descrição 1": desc1_text,
            "Descrição 2": desc2_text,
            "Descrição 3": desc3_text
        })

    # Ir para a próxima página
    pagina += 1
    time.sleep(2)  # Aguarde um pouco entre as requisições

# Fechar o navegador
driver.quit()

# Exibir os dados coletados
#for dado in dados_imoveis:
#    print(dado)
print(f"Total de imóveis coletados: {len(dados_imoveis)}")

arquivo_csv = "imoveis_dados.csv"
with open(arquivo_csv, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Título", "Preço", "Área", "Detalhes", "Descrição 1", "Descrição 2", "Descrição 3"])
    writer.writeheader()  # Escreve o cabeçalho
    writer.writerows(dados_imoveis)  # Escreve os dados

print(f"Dados salvos em {arquivo_csv}")