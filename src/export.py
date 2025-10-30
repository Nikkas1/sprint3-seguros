import csv
import os
import sys
from datetime import datetime

# Adiciona o diretório raiz do projeto ao path para que as importações relativas funcionem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa o logger
from .logger import get_logger

# Configuração
EXPORT_DIR = "exports"
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

# Inicializa o logger para o módulo de exportação
logger = get_logger("Sistema", "EXPORT")


def export_to_csv(data: list[dict], filename_prefix: str, user_id: str):
    """
    Exporta uma lista de dicionários para um arquivo CSV.
    Cria um nome de arquivo único baseado no prefixo e timestamp.

    Args:
        data (list[dict]): A lista de dicionários a ser exportada.
        filename_prefix (str): Prefixo descritivo para o nome do arquivo.
        user_id (str): ID do usuário que solicitou a exportação (para fins de auditoria).

    Returns:
        str or None: O caminho completo do arquivo CSV criado em caso de sucesso, ou None em caso de falha.
    """
    if not data:
        print("Nenhum dado para exportar.")
        logger.warning(
            f"Tentativa de exportar CSV vazia: {filename_prefix} por {user_id}"
        )
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(EXPORT_DIR, f"{filename_prefix}_{timestamp}.csv")

    # Obtém as chaves do primeiro dicionário para usar como cabeçalho
    fieldnames = list(data[0].keys())

    try:
        # Usamos 'w', newline='' e encoding='utf-8' para compatibilidade e evitar linhas em branco
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            # Delimitador ';' é melhor para compatibilidade com Excel em português
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

            writer.writeheader()
            writer.writerows(data)

        logger.info(
            f"Relatório '{filename_prefix}' exportado com sucesso para '{filepath}' por {user_id}."
        )
        return filepath
    except Exception as e:
        print(f"Erro ao exportar para CSV: {e}")
        logger.error(f"Falha ao exportar CSV '{filename_prefix}': {e}", exc_info=True)
        return None
