# services.py (VERSÃO CORRIGIDA, NA RAIZ DO PROJETO)

# Importa as funções específicas dos arquivos de persistência.
# Isso resolve o erro de 'cannot import name'
from datetime import date  # Necessário para o if __name__ == "__main__":

from database.db_mongo import log_operacao
from database.db_mysql import insert_apolice


# --- Camada de Serviço: Orquestração Híbrida ---
def emitir_apolice_hibrida(dados_apolice: dict, usuario_acao: str):
    """
    Função que orquestra a emissão de uma apólice,
    garantindo a gravação relacional e o log de auditoria.
    """
    apolice_id = None

    try:
        # 1. Ação Principal (MySQL REAL)
        print(
            f"-> Tentando inserir Apólice REAL no MySQL para o cliente {dados_apolice.get('cliente_id')}..."
        )

        # 🛑 CHAMA A FUNÇÃO REAL do db_mysql 🛑
        apolice_id = insert_apolice(
            cliente_id=int(dados_apolice.get("cliente_id")),
            tipo=dados_apolice.get("tipo", "PADRAO"),
            valor=dados_apolice.get("valor"),
            data_inicio=dados_apolice.get("data_inicio"),
        )

        # 2. Ação Secundária (MongoDB - Log)
        if apolice_id and apolice_id > 0:
            log_operacao(  # Chama a função específica
                usuario=usuario_acao,
                acao="EMISSAO_APOLICE",
                status="SUCESSO",
                detalhes={
                    "apolice_id_mysql": apolice_id,
                    "dados_recebidos": dados_apolice,
                },
            )
            return f"Apólice emitida com sucesso! ID MySQL: {apolice_id}"
        else:
            # Se o MySQL falhar, registra a falha no log
            log_operacao(
                usuario=usuario_acao,
                acao="EMISSAO_APOLICE",
                status="FALHA_MYSQL",
                detalhes={"dados_recebidos": dados_apolice},
            )
            return "❌ Erro: Falha ao inserir a apólice no MySQL."

    except Exception as e:
        # Trata qualquer erro inesperado durante a orquestração
        log_operacao(
            usuario=usuario_acao,
            acao="EMISSAO_APOLICE",
            status="ERRO_INESPERADO",
            detalhes={"erro": str(e), "dados_recebidos": dados_apolice},
        )
        return f"❌ Erro Crítico durante a emissão: {str(e)}"


# --- Exemplo de como usar o serviço ---
if __name__ == "__main__":
    print("\n--- Teste Rápido de Emissão Híbrida REAL ---")
    dados_teste = {
        "cliente_id": 1,
        "tipo": "RESIDENCIAL",
        "valor": 50000.00,
        "data_inicio": str(date.today()),
    }

    resultado = emitir_apolice_hibrida(dados_teste, "user_cli_01")
    print(f"\nResultado da Operação Híbrida: {resultado}")
