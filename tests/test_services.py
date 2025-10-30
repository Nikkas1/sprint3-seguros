# tests/test_services.py

import unittest
from unittest.mock import patch, MagicMock
from datetime import date
import sys
import os

# Ajuste de Path para importar o 'services' da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import emitir_apolice_hibrida


class TestEmissaoHibrida(unittest.TestCase):

    # ----------------------------------------------------
    # Teste de Sucesso na Emissão (Caminho Feliz)
    # ----------------------------------------------------
    @patch("services.log_operacao")
    @patch("services.insert_apolice")
    def test_01_emissao_sucesso_deve_chamar_mysql_e_mongo(
        self, mock_insert_apolice, mock_log_operacao
    ):
        # 1. Configurar o Mock do MySQL para simular sucesso
        APOLICE_ID_TESTE = 99
        mock_insert_apolice.return_value = APOLICE_ID_TESTE

        # 2. Dados de Entrada
        dados_apolice = {
            "cliente_id": 10,
            "tipo": "VIDA",
            "valor": 50000.00,
            "data_inicio": str(date.today()),
        }
        usuario_acao = "TEST_USER_SUCESSO"

        # 3. Executar o Serviço
        resultado = emitir_apolice_hibrida(dados_apolice, usuario_acao)

        # 4. Asserções (Verificações)

        # A) Verifica se a inserção principal (MySQL) foi chamada
        mock_insert_apolice.assert_called_once()

        # B) Verifica o resultado retornado ao usuário
        self.assertIn(f"ID MySQL: {APOLICE_ID_TESTE}", resultado)

        # C) Verifica se o log no MongoDB foi chamado com o status de SUCESSO
        mock_log_operacao.assert_called_once()
        mock_log_operacao.assert_called_with(
            usuario=usuario_acao,
            acao="EMISSAO_APOLICE",
            status="SUCESSO",
            detalhes={
                "apolice_id_mysql": APOLICE_ID_TESTE,
                "dados_recebidos": dados_apolice,
            },
        )

    # ----------------------------------------------------
    # Teste de Falha na Emissão (MySQL Falha)
    # ----------------------------------------------------
    @patch("services.log_operacao")
    @patch("services.insert_apolice")
    def test_02_emissao_falha_mysql_deve_logar_falha_no_mongo(
        self, mock_insert_apolice, mock_log_operacao
    ):
        # 1. Configurar o Mock do MySQL para simular falha (retorna 0)
        mock_insert_apolice.return_value = 0

        # 2. Dados de Entrada
        dados_apolice = {
            "cliente_id": 999,
            "tipo": "AUTO",
            "valor": 10000.00,
            "data_inicio": str(date.today()),
        }
        usuario_acao = "TEST_USER_FALHA"

        # 3. Executar o Serviço
        resultado = emitir_apolice_hibrida(dados_apolice, usuario_acao)

        # 4. Asserções

        # A) Verifica se o resultado indica falha
        self.assertIn("Falha ao inserir a apólice no MySQL", resultado)

        # B) Verifica se o log no MongoDB foi chamado com o status de FALHA
        mock_log_operacao.assert_called_once()
        mock_log_operacao.assert_called_with(
            usuario=usuario_acao,
            acao="EMISSAO_APOLICE",
            status="FALHA_MYSQL",
            detalhes={"dados_recebidos": dados_apolice},
        )

    # ----------------------------------------------------
    # Teste de Exceção (Erro Crítico de Código ou Conexão)
    # ----------------------------------------------------
    @patch("services.log_operacao")
    @patch("services.insert_apolice")
    def test_03_emissao_excecao_deve_logar_erro_critico(
        self, mock_insert_apolice, mock_log_operacao
    ):
        # 1. Configurar o Mock para lançar uma exceção (simular erro de conexão/código)
        mock_insert_apolice.side_effect = Exception("Conexão MySQL interrompida")

        # 2. Dados de Entrada
        dados_apolice = {
            "cliente_id": 1,
            "tipo": "RESIDENCIAL",
            "valor": 500.00,
            "data_inicio": str(date.today()),
        }
        usuario_acao = "TEST_USER_EXCECAO"

        # 3. Executar o Serviço
        resultado = emitir_apolice_hibrida(dados_apolice, usuario_acao)

        # 4. Asserções

        # A) Verifica se o resultado indica o erro crítico
        self.assertIn(
            "Erro Crítico durante a emissão: Conexão MySQL interrompida", resultado
        )

        # B) Verifica se o log no MongoDB foi chamado com o status de ERRO_INESPERADO
        mock_log_operacao.assert_called_once()
        mock_log_operacao.assert_called_with(
            usuario=usuario_acao,
            acao="EMISSAO_APOLICE",
            status="ERRO_INESPERADO",
            detalhes={
                "erro": "Conexão MySQL interrompida",
                "dados_recebidos": dados_apolice,
            },
        )


if __name__ == "__main__":
    unittest.main()
