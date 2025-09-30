from src.sistema import SistemaSeguros
from src.database import create_schema, get_db 
from src.dao import init_admin 
from src.exceptions import BusinessError 

def main():
    create_schema() 
    db = next(get_db())
    try:
        init_admin(db)
    finally:
        db.close()
    
    sis = SistemaSeguros()
    print("=== Sistema de Seguros Sompo ===")
    
    ok, tipo = sis.login()
    
    if not ok:
        print("Login inválido!")
        return

    while True:
        if tipo == "admin":
            print("""
--- MENU ADMIN ---
1. Cadastrar Cliente
2. Atualizar Cliente
3. Emitir Apólice
4. Cancelar Apólice
5. Registrar Sinistro
6. Atualizar Status de Sinistro
7. Relatórios
0. Sair
""")
        else:
            print("""
--- MENU USUÁRIO ---
1. Relatórios
0. Sair
""")
        
        op = input("Opção: ")
        try:
            if op == "0":
                print("Encerrando.")
                break
            elif op == "1" and tipo == "admin":
                sis.cadastrar_cliente() 
                print("Cliente cadastrado com sucesso.")
            elif op == "2" and tipo == "admin":
                cpf = input("CPF do cliente: ")
                telefone = input("Novo telefone (deixe em branco para não alterar): ") or None
                email = input("Novo e-mail (deixe em branco para não alterar): ") or None
                endereco = input("Novo endereço (deixe em branco para não alterar): ") or None
                sis.atualizar_cliente(cpf, telefone, email, endereco)
                print("Cliente atualizado com sucesso.")
            elif op == "3" and tipo == "admin":
                cpf = input("CPF do cliente: ")
                print("Tipos: 1-Automóvel, 2-Residencial, 3-Vida")
                tipo_seguro = input("Escolha o tipo de seguro: ")
                dados_seguro = {}
                if tipo_seguro == "1":
                    dados_seguro['modelo'] = input("Modelo do carro: ")
                    dados_seguro['ano'] = int(input("Ano: "))
                    dados_seguro['placa'] = input("Placa: ")
                    dados_seguro['valor'] = float(input("Valor do carro: "))
                elif tipo_seguro == "2":
                    dados_seguro['endereco'] = input("Endereço do imóvel: ")
                    dados_seguro['valor'] = float(input("Valor do imóvel: "))
                elif tipo_seguro == "3":
                    beneficiarios_str = input("Beneficiários (separados por vírgula): ")
                    dados_seguro['beneficiarios'] = [b.strip() for b in beneficiarios_str.split(",") if b.strip()]
                    dados_seguro['valor'] = float(input("Valor segurado: "))
                apolice = sis.emitir_apolice(cpf, tipo_seguro, dados_seguro)
                print(f"Apólice {apolice.numero} emitida. Valor mensal: R$ {apolice.premio:.2f}")
            elif op == "4" and tipo == "admin":
                numero = input("Número da apólice: ")
                confirm = input("Confirma o cancelamento? (s/n): ")
                if confirm.lower() == 's':
                    sis.cancelar_apolice(numero)
                    print("Apólice cancelada.")
            elif op == "5" and tipo == "admin":
                numero_apolice = input("Número da apólice: ")
                descricao = input("Descrição do ocorrido: ")
                data = input("Data do sinistro (DD/MM/AAAA): ")
                sis.registrar_sinistro(numero_apolice, descricao, data)
                print("Sinistro registrado.")
            elif op == "6" and tipo == "admin":
                numero_apolice = input("Número da apólice do sinistro: ")
                novo_status = input("Novo status (Aberto/Fechado/Em Análise): ")
                sis.atualizar_status_sinistro(numero_apolice, novo_status)
                print("Status do sinistro atualizado.")
            elif op == "7" or (op == "1" and tipo == "comum"):
                print("""
1. Valor total segurado por cliente
2. Apólices por tipo de seguro
3. Quantidade de sinistros por status
4. Ranking de clientes com mais apólices
""")
                sub = input("Escolha: ")
                if sub == "1":
                    relatorio = sis.relatorio_valor_segurado_por_cliente()
                    for r in relatorio:
                        print(f"CPF: {r['cpf']}, Nome: {r['nome']}, Total Segurado: R$ {r['valor_total_segurado']:.2f}")
                elif sub == "2":
                    relatorio = sis.relatorio_apolices_por_tipo()
                    for tipo_s, quantidade in relatorio.items():
                        print(f"{tipo_s}: {quantidade} apólice(s)")
                elif sub == "3":
                    relatorio = sis.relatorio_sinistros_status()
                    for status, quantidade in relatorio.items():
                        print(f"{status}: {quantidade} sinistro(s)")
                elif sub == "4":
                    relatorio = sis.relatorio_ranking_clientes()
                    for r in relatorio:
                        print(f"CPF: {r['cpf']}, Nome: {r['nome']}, Apólices: {r['apolices']}")
                else:
                    print("Opção inválida.")
            else:
                print("Opção inválida ou permissão insuficiente.")
        except BusinessError as e:
            print(f"ERRO DE NEGÓCIO: {e}")
        except ValueError as e:
            print(f"ERRO DE VALOR: Entrada inválida. {e}")
        except Exception as e:
            print(f"ERRO INESPERADO: {e}")


if __name__ == "__main__":
    main()
