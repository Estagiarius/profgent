# Importa a biblioteca 'requests' para fazer requisições HTTP (acessar sites).
import requests
# Importa a biblioteca 'BeautifulSoup' para fazer parsing (análise) de HTML e extrair informações.
from bs4 import BeautifulSoup
# Importa o decorador 'tool' para registrar a função como uma ferramenta de IA.
from app.core.tools.tool_decorator import tool

# Registra a função como uma ferramenta disponível para a IA.
@tool
def search_internet(query: str) -> str:
    """
    Realiza uma busca na web para uma determinada consulta e retorna um resumo do resultado principal.
    """
    # Bloco try/except para lidar com erros de rede ou de parsing.
    try:
        # Para este exemplo, usaremos o DuckDuckGo como motor de busca.
        # Uma implementação real poderia usar uma API de busca dedicada (ex: Tavily, Serper).
        # Define um cabeçalho 'User-Agent' para simular um navegador e evitar ser bloqueado.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        # Monta a URL de busca do DuckDuckGo com a consulta do usuário.
        url = f"https://html.duckduckgo.com/html/?q={query}"

        # Faz a requisição GET para a URL, com os cabeçalhos e um timeout de 5 segundos.
        response = requests.get(url, headers=headers, timeout=5)
        # Lança uma exceção se a resposta tiver um código de status de erro (ex: 404, 500).
        response.raise_for_status()

        # Cria um objeto BeautifulSoup para analisar o conteúdo HTML da resposta.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrai os "snippets" (resumos dos resultados) da página de resultados do DuckDuckGo.
        # A classe 'result__a' é específica da estrutura HTML do DuckDuckGo.
        snippets = soup.find_all('a', class_='result__a')

        # Se nenhum resultado for encontrado, retorna uma mensagem.
        if not snippets:
            return "Nenhum resultado de busca encontrado."

        # Por simplicidade, vamos apenas resumir os primeiros snippets.
        summary = ""
        # Itera sobre os 3 primeiros resultados encontrados.
        for i, snippet in enumerate(snippets[:3]):
            # Adiciona o texto do resultado ao resumo.
            summary += f"Resultado {i+1}: {snippet.get_text(strip=True)}\n"

        # Retorna o resumo se ele não estiver vazio.
        return summary if summary else "Não foi possível extrair um resumo dos resultados da busca."

    # Captura erros relacionados a requisições de rede (ex: sem conexão, timeout).
    except requests.RequestException as e:
        return f"Erro durante a busca na web: {e}"
    # Captura qualquer outro erro inesperado.
    except Exception as e:
        return f"Ocorreu um erro inesperado durante a busca: {e}"
