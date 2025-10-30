# src/logger.py
import logging
import os

# Cria a pasta de logs se não existir
os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/app.log"

# Define o formato do log, incluindo os metadados (user e operation)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | user=%(user)s | op=%(operation)s | %(message)s"
)

# Configuração do Logger principal
logger = logging.getLogger("seguro")
logger.setLevel(logging.INFO)

# Handler para o arquivo de log
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Handler para o console (terminal)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


# Função para obter um logger contextualizado (com usuário e operação)
def get_logger(user_context="Sistema", operation=""):
    """Retorna um logger customizado com informações de contexto."""
    # O LoggerAdapter injeta as variáveis 'user' e 'operation'
    extra = {"user": user_context or "Desconhecido", "operation": operation or "-"}
    return logging.LoggerAdapter(logger, extra)
