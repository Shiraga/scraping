import requests
from bs4 import BeautifulSoup

# URL base com suporte a paginação
base_url = "https://www.dfimoveis.com.br/venda/df/brasilia/imoveis"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Inicialização
pagina = 1
dados_imoveis = []

while True:
    # URL da página atual
    url = f"{base_url}?pagina={pagina}"
    print(f"Coletando dados da página {pagina}...")

    # Fazer a requisição HTTP
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Localizar os contêineres dos imóveis (ajuste o seletor ao analisar a página)
    imoveis = soup.find_all("a", class_="new-card")

    # Interrompe se não encontrar imóveis (fim das páginas)
    if not imoveis:
        print("Não há mais imóveis para coletar.")
    break

    # Extrair dados
    for imovel in imoveis:
        titulo = imovel.find("h2", class_="new-title phrase")
        desc1 = imovel.find("div", class_="new-text phrase") # descricao completa
        desc2 = imovel.find("h3", class_="new-desc phrase") # descricao pequena / ruim
        desc3 = imovel.find("h3", class_="new-simple phrase") # descricao simples
        preco = imovel.find("div", class_="new-price")

        # Evitar NoneType se algum elemento estiver ausente
        titulo_text = titulo.text.strip() if titulo else "Título não encontrado"
        preco_text = preco.text.strip() if preco else "Preço não encontrado"
        desc1_text = desc1.text.strip() if desc1 else "Descrição não encontrada"
        
        dados_imoveis.append({
            "Título": titulo_text,
            "Preço": preco_text,
            "Descrição": desc1_text
        })

    # Incrementar para a próxima página
    pagina += 1

# Exibir os dados coletados
print(f"Total de imóveis coletados: {len(dados_imoveis)}")
for dado in dados_imoveis:
    print(dado)