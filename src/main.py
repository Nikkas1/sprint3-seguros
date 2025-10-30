# src/main.py (VERSÃO CORRIGIDA PARA O SPRINT 4 HÍBRIDO)

# Importa o módulo services da raiz do projeto (um nível acima de src)
import os
import sys

# Adiciona o diretório pai (raiz do sprint3) ao caminho de busca do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date  # Para usar a data atual

from services import emitir_apolice_hibrida

# from src.database import create_schema, get_db # Removido: Não é mais persistência local
from src.exceptions import BusinessError
from src.sistema import SistemaSeguros

# --- DADOS DE TESTE DE LOGIN ---
# NOTE: O login real deve ser adaptado, mas para este teste, vamos simplificar
# assumindo que a parte do login ainda funciona se o DAO for mantido.


def main():
    # Remover chamadas de persistência antiga
    # create_schema()
    # db = next(get_db())
    # try:
    #     init_admin(db)
    # finally:
    #     db.close()

    sis = SistemaSeguros()
    print("=== Sistema de Seguros Sompo HÍBRIDO ===")

    # Se você não precisar mais da autenticação complexa, pode simular o login:
    ok, tipo = True, "admin"  # SIMULANDO LOGIN DE ADMIN PARA ACESSO FÁCIL

    if not ok:
        print("Login inválido!")
        return

    while True:
        if tipo == "admin":
            print(
                """
--- MENU ADMIN (SPRINT 4) ---
1. Cadastrar Cliente (Ainda usa a lógica antiga)
2. Atualizar Cliente (Ainda usa a lógica antiga)
3. EMITIR APÓLICE HÍBRIDA (NOVO FLUXO)
4. Cancelar Apólice (Ainda usa a lógica antiga)
5. Registrar Sinistro (Ainda usa a lógica antiga)
6. Atualizar Status de Sinistro (Ainda usa a lógica antiga)
7. Relatórios
0. Sair
"""
            )
        else:
            # ... (menu usuário comum)
            pass

        op = input("Opção: ")
        try:
            if op == "0":
                print("Encerrando.")
                break
            # ... (Outras opções do menu)

            # 🛑 NOVO FLUXO HÍBRIDO
            elif op == "3" and tipo == "admin":
                emitir_apolice_novo_fluxo()  # Chama a nova função de emissão

            # ... (Restante das opções)

            elif op == "7" or (op == "1" and tipo == "comum"):
                # ... (Lógica de relatórios)
                pass

            else:
                print("Opção inválida ou permissão insuficiente.")
        except BusinessError as e:
            print(f"ERRO DE NEGÓCIO: {e}")
        except ValueError as e:
            print(f"ERRO DE VALOR: Entrada inválida. {e}")
        except Exception as e:
            print(f"ERRO INESPERADO: {e}")


def emitir_apolice_novo_fluxo():
    """
    Função que coleta os dados necessários e chama o serviço híbrido.
    Substitui a lógica de 'sis.emitir_apolice' do código antigo.
    """
    cpf = input("CPF do cliente (Apenas para referência): ")
    cliente_id = input("ID do Cliente (Real do MySQL): ")  # Requer o ID do MySQL

    print("Tipos: 1-Automóvel, 2-Residencial, 3-Vida")
    tipo_seguro_op = input("Escolha o tipo de seguro (1/2/3): ")

    # Mapeamento do tipo de seguro (necessário para a função insert_apolice)
    tipo_map = {"1": "AUTO", "2": "RESIDENCIAL", "3": "VIDA"}
    tipo = tipo_map.get(tipo_seguro_op, "PADRAO")

    # Simplicamos a coleta de dados, focando apenas no valor para a inserção no RDS
    valor = float(input("Valor total segurado (para o RDS): "))

    dados_apolice = {
        "cliente_id": cliente_id,
        "tipo": tipo,
        "valor": valor,
        "data_inicio": str(date.today()),
    }

    # 🛑 CHAMADA AO NOVO SERVIÇO HÍBRIDO 🛑
    resultado_servico = emitir_apolice_hibrida(dados_apolice, usuario_acao="ADMIN_CLI")

    print("\n--- Resultado da Emissão Híbrida ---")
    print(resultado_servico)


# Remova o bloco original 'elif op == "3" and tipo == "admin":' do main() e chame a nova função.
# O restante do seu código main() fica inalterado.

if __name__ == "__main__":
    main()
