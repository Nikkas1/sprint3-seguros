import datetime

from pymongo import MongoClient

# --- CONFIGURAÇÕES DE CONEXÃO ---
# URI deve ser mantida como variável global ou de ambiente
URI = "mongodb+srv://carlos:adminadmin@cluster0.k4pby9m.mongodb.net/?appName=Cluster0"
DB_NAME = "Cluster0"
LOG_COLLECTION_NAME = "logs"


def get_mongo_collection(collection_name=LOG_COLLECTION_NAME):
    """
    Estabelece a conexão e retorna uma coleção específica do MongoDB.
    """
    try:
        # Tenta criar o cliente e retornar a coleção
        cliente = MongoClient(URI)
        db = cliente[DB_NAME]
        return db[collection_name]
    except Exception as e:
        print(f"❌ Erro ao conectar ou selecionar a coleção '{collection_name}': {e}")
        # Retorna None em caso de falha de conexão
        return None


def log_operacao(usuario: str, acao: str, status: str, detalhes: dict = None):
    """
    Insere um registro detalhado de log no MongoDB.
    """
    colecao = get_mongo_collection(LOG_COLLECTION_NAME)

    if colecao is not None:
        log_registro = {
            "usuario": usuario,
            "acao": acao,
            "status": status,
            "detalhes": detalhes if detalhes else {},
            "timestamp": datetime.datetime.now(),  # Registra o tempo da operação
        }
        colecao.insert_one(log_registro)
        print(f"Log de operação '{acao}' inserido no MongoDB com sucesso.")
    else:
        # Esta mensagem só aparece se houver falha no get_mongo_collection
        print("Falha na persistência do log devido à falha de conexão.")


# --- Bloco de Teste Local (Opcional, para garantir que o arquivo funciona) ---
if __name__ == "__main__":
    print("\n--- Teste Rápido de Conexão (Refatorado) ---")
    log_operacao(
        usuario="system_check",
        acao="TESTE_REFATORACAO",
        status="OK",
        detalhes={"versao": "Sprint4"},
    )
