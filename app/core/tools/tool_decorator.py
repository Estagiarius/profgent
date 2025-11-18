# Importa o módulo 'inspect' para obter informações sobre objetos Python, como funções (assinaturas, docstrings).
import inspect
# Importa o módulo 'json' para trabalhar com o formato JSON.
import json
# Importa 'wraps' de 'functools' para criar decoradores que preservam os metadados da função original.
from functools import wraps

# Define o decorador 'tool'.
def tool(func):
    """
    Um decorador que inspeciona uma função e gera um esquema JSON
    para ser usado com a API de 'function calling' da OpenAI.
    """
    # `@wraps(func)` garante que a função `wrapper` mantenha o nome, a docstring, etc.,
    # da função original (`func`) que está sendo decorada.
    @wraps(func)
    def wrapper(*args, **kwargs):
        # A função wrapper simplesmente executa a função original.
        # O principal objetivo deste decorador é anexar o esquema a ela.
        return func(*args, **kwargs)

    # --- Geração do Esquema (Schema) ---
    # Obtém a assinatura da função (informações sobre seus parâmetros).
    func_sig = inspect.signature(func)
    # Obtém a docstring da função.
    docstring = inspect.getdoc(func)

    # Cria a estrutura básica do esquema JSON, seguindo o padrão da OpenAI.
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }

    # Extrai a descrição da função a partir da primeira linha da docstring.
    if docstring:
        schema["function"]["description"] = docstring.strip().split('\n')[0]

    # Mapeia tipos de dados do Python para tipos de esquema JSON.
    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
    }

    # Extrai os parâmetros da função para preencher o esquema.
    # Itera sobre o nome e o objeto de cada parâmetro na assinatura da função.
    for name, param in func_sig.parameters.items():
        # Define 'string' como o tipo padrão se nenhuma anotação de tipo for encontrada.
        param_type = "string"
        # Verifica se o parâmetro tem uma anotação de tipo (ex: `name: str`) e se o tipo está no nosso mapeamento.
        if param.annotation is not inspect.Parameter.empty and param.annotation.__name__ in type_mapping:
            param_type = type_mapping[param.annotation.__name__]

        # Adiciona a propriedade do parâmetro ao esquema.
        schema["function"]["parameters"]["properties"][name] = {
            "type": param_type,
            # Em uma implementação mais avançada, a docstring poderia ser analisada
            # para extrair descrições de parâmetros individuais.
            "description": f"O(a) {name} para a função."
        }

        # Verifica se o parâmetro não tem um valor padrão.
        if param.default is inspect.Parameter.empty:
            # Se não houver valor padrão, o parâmetro é considerado obrigatório.
            schema["function"]["parameters"]["required"].append(name)

    # Anexa o esquema gerado como um atributo `.schema` na função wrapper.
    # O ToolRegistry acessará este atributo para obter o esquema de cada ferramenta.
    wrapper.schema = schema
    # Retorna a função wrapper, que agora tem o esquema anexado.
    return wrapper
