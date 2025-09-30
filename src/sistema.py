from . import dao
from .database import get_db
from .exceptions import BusinessError, LoginInvalido, OperacaoNaoPermitida, CpfInvalido, ApoliceInexistente
from .logger import get_logger
from .utils import gerar_numero_apolice
from .seguro import SeguroAutomovel, SeguroResidencial, SeguroVida
from .export import export_to_csv # <-- NOVO: Importa a função de exportação

class SistemaSeguros:
    def __init__(self):
        self.usuario_logado = None
        self.logger = get_logger("Sistema", "INIT")
        self.logger.info("Sistema inicializado, pronto para login.")

    def login(self):
        while True:
            username = input("Usuário: ")
            password = input("Senha: ")

            db_session_generator = get_db()
            db = next(db_session_generator)
            
            try:
                user = dao.authenticate_user(db, username, password) 
                
                self.usuario_logado = user
                self.logger = get_logger(user.username, "MENU") 
                self.logger.info("Login realizado com sucesso.")
                
                return True, user.role
            
            except LoginInvalido:
                print("Login Inválido!")
                return False, None
            
            except Exception as e:
                self.logger.error(f"Erro inesperado no login: {e}", exc_info=True)
                return False, None
            
            finally:
                db.close()

    def cadastrar_cliente(self):
        if not self.usuario_logado:
            raise OperacaoNaoPermitida("Usuário não logado.")
        if self.usuario_logado.role != "admin":
            raise OperacaoNaoPermitida("Apenas administradores podem cadastrar clientes.")

        nome = input("Nome do Cliente: ")
        cpf = input("CPF: ")
        data_nasc = input("Data de Nascimento (DD/MM/AAAA): ")
        
        
        telefone = input("Telefone: ")
        email = input("E-mail: ")
        endereco = input("Endereço: ")
        

        cliente_data = {
            "nome": nome,
            "cpf": cpf,
            "data_nasc": data_nasc,
        
            "telefone": telefone,
            "email": email,
            "endereco": endereco
            
        }
        
        db = next(get_db())

        try:
            novo_cliente = dao.create_cliente(db, cliente_data, self.usuario_logado)
            print(f"Cliente {novo_cliente.nome} cadastrado com sucesso (ID: {novo_cliente.id})!")
            self.logger.info(f"Cliente cadastrado: ID={novo_cliente.id}")
            return novo_cliente

        except BusinessError as e:
            print(f"Erro ao cadastrar cliente: {e}")
            # Não lançamos o erro aqui se a intenção é apenas mostrar o erro ao usuário
            # Se for para o main lidar com o erro, o 'raise' é necessário
            self.logger.warning(f"Falha ao cadastrar cliente: {e}")
        
        except Exception as e:
            self.logger.error(f"Erro ao cadastrar cliente: {e}", exc_info=True)
            print("Ocorreu um erro interno. Verifique os logs.")
            
        finally:
            db.close()

    def atualizar_cliente(self, cpf, telefone=None, email=None, endereco=None):
        if not self.usuario_logado:
            raise OperacaoNaoPermitida("Usuário não logado.")
        
        db = next(get_db())
        try:
            cliente_atualizado = dao.update_cliente(db, cpf, telefone, email, endereco, self.usuario_logado)
            print(f"Cliente {cliente_atualizado.nome} atualizado com sucesso!")
        
        except BusinessError as e:
            print(f"Erro ao atualizar cliente: {e}")
            self.logger.warning(f"Falha ao atualizar cliente {cpf}: {e}")
        
        except Exception as e:
            self.logger.error(f"Erro ao atualizar cliente: {e}", exc_info=True)
            print("Ocorreu um erro interno. Verifique os logs.")
            
        finally:
            db.close()

    def emitir_apolice(self, cpf, tipo_seguro, dados_seguro):
        if not self.usuario_logado:
            raise OperacaoNaoPermitida("Usuário não logado.")

        if tipo_seguro == "1":
            seguro_obj = SeguroAutomovel(dados_seguro['modelo'], dados_seguro['ano'], dados_seguro['placa'], dados_seguro['valor'])
        elif tipo_seguro == "2":
            seguro_obj = SeguroResidencial(dados_seguro['endereco'], dados_seguro['valor'])
        elif tipo_seguro == "3":
            seguro_obj = SeguroVida(dados_seguro['beneficiarios'], dados_seguro['valor'])
        else:
            raise ValueError("Tipo de seguro inválido.")

        db = next(get_db())
        try:
            apolice_data = {
                "cpf_cliente": cpf,
                "tipo_seguro": seguro_obj.__class__.__name__,
                "premio": seguro_obj.valor_premio(),
                "dados_seguro": dados_seguro 
            }
            
            nova_apolice = dao.create_apolice(db, apolice_data, self.usuario_logado)
            print(f"Apólice N° {nova_apolice.numero} emitida com sucesso!")
            return nova_apolice
            
        except BusinessError as e:
            print(f"Erro ao emitir apólice: {e}")
            self.logger.warning(f"Falha ao emitir apólice para {cpf}: {e}")
        
        except Exception as e:
            self.logger.error(f"Erro ao emitir apólice: {e}", exc_info=True)
            print("Ocorreu um erro interno. Verifique os logs.")
            
        finally:
            db.close()

    def cancelar_apolice(self, numero):
        if not self.usuario_logado:
            raise OperacaoNaoPermitida("Usuário não logado.")
        
        # --- NOVO: Confirmação de Ação Destrutiva ---
        confirmacao = input(f"Tem certeza que deseja CANCELAR a Apólice N° {numero}? (s/N): ").lower()
        if confirmacao != 's':
            print("Operação de cancelamento abortada.")
            self.logger.info(f"Cancelamento de apólice {numero} abortado pelo usuário.")
            return

        db = next(get_db())
        try:
            apolice = dao.cancel_apolice(db, numero, self.usuario_logado)
            print(f"Apólice N° {apolice.numero} cancelada com sucesso!")
            
        except BusinessError as e:
            print(f"Erro ao cancelar apólice: {e}")
            self.logger.warning(f"Falha ao cancelar apólice {numero}: {e}")
            
        except Exception as e:
            self.logger.error(f"Erro ao cancelar apólice: {e}", exc_info=True)
            print("Ocorreu um erro interno. Verifique os logs.")
            
        finally:
            db.close()

    def registrar_sinistro(self, numero_apolice, descricao, data):
        if not self.usuario_logado:
            raise OperacaoNaoPermitida("Usuário não logado.")
        
        db = next(get_db())
        try:
            sinistro_data = {
                "numero_apolice": numero_apolice,
                "descricao": descricao,
                "data": data
            }
            sinistro = dao.create_sinistro(db, sinistro_data, self.usuario_logado)
            print(f"Sinistro registrado na Apólice {numero_apolice} (ID: {sinistro.id})!")
            return sinistro
            
        except BusinessError as e:
            print(f"Erro ao registrar sinistro: {e}")
            self.logger.warning(f"Falha ao registrar sinistro na apólice {numero_apolice}: {e}")
        
        except Exception as e:
            self.logger.error(f"Erro ao registrar sinistro: {e}", exc_info=True)
            print("Ocorreu um erro interno. Verifique os logs.")
            
        finally:
            db.close()

    def atualizar_status_sinistro(self, numero_apolice, novo_status):
        if not self.usuario_logado:
            raise OperacaoNaoPermitida("Usuário não logado.")

        db = next(get_db())
        try:
            sinistro = dao.update_sinistro_status(db, numero_apolice, novo_status, self.usuario_logado)
            print(f"Status do Sinistro da Apólice {numero_apolice} atualizado para '{sinistro.status}'.")
        
        except BusinessError as e:
            print(f"Erro ao atualizar status: {e}")
            self.logger.warning(f"Falha ao atualizar status do sinistro {numero_apolice}: {e}")
        
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status do sinistro: {e}", exc_info=True)
            print("Ocorreu um erro interno. Verifique os logs.")
            
        finally:
            db.close()

    # --- FUNÇÃO UTILITÁRIA PARA EXIBIÇÃO E EXPORTAÇÃO DE RELATÓRIOS ---

    def _display_and_export_report(self, report_data: list | dict, title: str, filename_prefix: str):
        """Exibe o relatório no console e pergunta ao usuário se deseja exportar para CSV."""

        print("\n" + "="*80)
        print(f"*** RELATÓRIO: {title} ***")
        print("="*80)

        # 1. Exibir Relatório
        if isinstance(report_data, list):
            if not report_data:
                print("Nenhum dado encontrado.")
                return

            # Assume que é uma lista de dicionários
            if report_data:
                # Obtém o cabeçalho (keys do primeiro item)
                headers = list(report_data[0].keys())
                
                # Define a largura da coluna para formatação
                col_widths = {header: len(header) for header in headers}
                for row in report_data:
                    for header in headers:
                        # Adapta a largura para números formatados ou strings
                        display_value = str(row.get(header, ''))
                        if isinstance(row.get(header), (int, float)):
                            # Formata valores monetários para melhor exibição (exclusivo para 'valor_total_segurado')
                            if header.lower().find('valor') != -1 or header.lower().find('premio') != -1:
                                display_value = f"R$ {row.get(header, 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                                row[header] = row.get(header) # Mantém o original para CSV
                            else:
                                display_value = str(row.get(header))
                        
                        col_widths[header] = max(col_widths[header], len(display_value))

                # Imprime o cabeçalho
                header_line = " | ".join(f"{h.upper():<{col_widths[h]}}" for h in headers)
                print(header_line)
                print("-" * len(header_line))

                # Imprime os dados
                for row in report_data:
                    row_line = []
                    for h in headers:
                        value = row.get(h, '')
                        display_value = str(value)

                        # Re-aplica a formatação para exibição
                        if isinstance(value, (int, float)):
                            if h.lower().find('valor') != -1 or h.lower().find('premio') != -1:
                                display_value = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        
                        row_line.append(f"{display_value:<{col_widths[h]}}")
                    print(" | ".join(row_line))

        elif isinstance(report_data, dict):
            # Formato de dicionário (Ex: contagem por status/tipo)
            if not report_data:
                print("Nenhum dado encontrado.")
                return

            print(f"{'ITEM':<30} | {'CONTAGEM':<10}")
            print("-" * 41)
            # Converte para lista de dicionários para facilitar a exportação
            export_list = []
            for key, value in report_data.items():
                print(f"{key:<30} | {value:<10}")
                export_list.append({"item": key, "contagem": value})
            report_data = export_list # Usa essa lista para a exportação

        else:
            print("Formato de relatório inválido.")
            return

        print("="*80)

        # 2. Exportar para CSV
        confirmacao = input("Deseja exportar este relatório para CSV? (s/N): ").lower()
        if confirmacao == 's':
            if isinstance(report_data, list) and report_data:
                filepath = export_to_csv(report_data, filename_prefix, self.usuario_logado.username)
                if filepath:
                    print(f"\nSUCESSO: Relatório exportado para: {filepath}")
                else:
                    print("\nFALHA na exportação do relatório.")
            else:
                print("\nNão foi possível exportar: dados ausentes ou formato incorreto.")

    # --- RELATÓRIOS (Refatorados para usar o DAO) ---
    
    def relatorio_valor_segurado_por_cliente(self):
        db = next(get_db())
        try:
            # Chama a função implementada no dao.py
            dados = dao.relatorio_valor_segurado_por_cliente(db)
            self._display_and_export_report(
                dados, 
                "Valor Total Segurado por Cliente (Apólices Ativas)", 
                "valor_segurado_cliente"
            )
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de valor segurado: {e}", exc_info=True)
            print("Erro ao gerar relatório. Verifique os logs.")
        finally:
            db.close()

    def relatorio_apolices_por_tipo(self):
        db = next(get_db())
        try:
            # Chama a função implementada no dao.py
            dados = dao.relatorio_apolices_por_tipo(db)
            self._display_and_export_report(
                dados,
                "Quantidade de Apólices Ativas por Tipo de Seguro",
                "apolices_por_tipo"
            )
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de apólices por tipo: {e}", exc_info=True)
            print("Erro ao gerar relatório. Verifique os logs.")
        finally:
            db.close()

    def relatorio_sinistros_status(self):
        db = next(get_db())
        try:
            # Chama a função implementada no dao.py
            dados = dao.relatorio_sinistros_status(db)
            self._display_and_export_report(
                dados,
                "Status dos Sinistros (Contagem)",
                "sinistros_por_status"
            )
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de sinistros por status: {e}", exc_info=True)
            print("Erro ao gerar relatório. Verifique os logs.")
        finally:
            db.close()

    def relatorio_ranking_clientes(self):
        db = next(get_db())
        try:
            # Chama a função implementada no dao.py
            dados = dao.relatorio_ranking_clientes(db)
            self._display_and_export_report(
                dados,
                "Ranking de Clientes por Total de Apólices Ativas",
                "ranking_clientes_apolices"
            )
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de ranking de clientes: {e}", exc_info=True)
            print("Erro ao gerar relatório. Verifique os logs.")
        finally:
            db.close()
