# B:\sprint3\main_sprint4.py (NOVO ARQUIVO NA RAIZ)

# O import funciona perfeitamente aqui, pois services.py está na mesma pasta.
from datetime import date

from services import emitir_apolice_hibrida


def main():
    """Menu principal simplificado para testar o fluxo HÍBRIDO."""
    print("=========================================")
    print("====== SPRINT 4: TESTE DE FLUXO HÍBRIDO (CLI NA RAIZ) ======")
    print("=========================================")

    while True:
        print("\n--- Menu ---")
        print("1. Emitir Nova Apólice Híbrida")
        print("2. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            emitir_nova_apolice()
        elif escolha == "2":
            print("Saindo da aplicação. Tchau!")
            break
        else:
            print("Opção inválida. Tente novamente.")


def emitir_nova_apolice():
    """Coleta dados e chama a camada de serviço."""
    print("\n--- Nova Emissão de Apólice ---")

    try:
        # Coleta de dados
        # IMPORTANTE: Use um ID de cliente que exista na sua tabela 'clientes' do RDS.
        cliente_id = int(input("ID do Cliente (Real do MySQL): "))
        tipo = input("Tipo de Apólice (ex: AUTO, RESIDENCIAL): ")
        valor = float(input("Valor do Prêmio: "))

        # Dados do sistema
        data_inicio = str(date.today())
        usuario_acao = "MAIN_CLI_S4"

        dados_apolice = {
            "cliente_id": cliente_id,
            "tipo": tipo,
            "valor": valor,
            "data_inicio": data_inicio,
        }

        # Chamada à Camada de Serviço Híbrida
        print("\nProcessando...")
        resultado = emitir_apolice_hibrida(dados_apolice, usuario_acao)
        print(f"\n[ Resultado ] {resultado}")

    except ValueError:
        print("❌ Erro: Por favor, insira um número válido para ID e Valor.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
