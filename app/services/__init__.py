# Importa a classe DataService do arquivo data_service.py, que está no mesmo diretório.
from .data_service import DataService

# Cria uma instância única e compartilhada do DataService.
# Esta instância será importada por outras partes da aplicação (por exemplo, as 'tools' da IA)
# para garantir que todos usem o mesmo objeto de serviço.
# Isso ajuda a manter um estado consistente e a gerenciar as conexões com o banco de dados de forma centralizada.
data_service = DataService()
