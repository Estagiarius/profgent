# Importa ABC (Abstract Base Class) e abstractmethod para criar uma classe base abstrata.
from abc import ABC, abstractmethod
# Importa dataclass para criar classes de dados de forma concisa.
from dataclasses import dataclass
# Importa tipos para anotações de tipo.
from typing import List, Dict, Any

# O decorador @dataclass cria automaticamente métodos especiais como __init__ e __repr__.
@dataclass
class AssistantResponse:
    """
    Uma estrutura de dados padronizada para as respostas do assistente.
    Isso garante que, independentemente do provedor de LLM usado, a resposta
    sempre terá o mesmo formato, facilitando o manuseio pelo AssistantService.
    """
    # Conteúdo textual da resposta do assistente (a mensagem em si).
    content: str
    # Uma lista de chamadas de ferramenta solicitadas pelo modelo, se houver. O padrão é None.
    tool_calls: List[Dict[str, Any]] | None = None

# Define a classe base abstrata para todos os provedores de LLM.
# Herdar de ABC (Abstract Base Class) permite o uso de métodos abstratos.
class LLMProvider(ABC):
    """
    Uma classe base abstrata que define o contrato (a interface) para todos os provedores de LLM.
    Qualquer classe de provedor (OpenAI, Ollama, etc.) DEVE implementar os métodos
    marcados com @abstractmethod.
    """

    # Define uma propriedade abstrata.
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Retorna o nome do provedor (ex: 'OpenAI').
        """
        # A implementação real deve estar nas classes filhas.
        pass

    # Define um método assíncrono abstrato.
    @abstractmethod
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        Obtém de forma assíncrona uma resposta de chat do modelo.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        Recupera de forma assíncrona uma lista de nomes de modelos disponíveis do provedor.
        """
        pass

    # Define um método assíncrono que não é abstrato, mas pode ser sobrescrito.
    async def close(self):
        """
        Fecha de forma assíncrona quaisquer recursos abertos, como clientes de rede.
        As classes filhas que usam clientes de rede (como httpx) devem implementar este método.
        """
        pass
