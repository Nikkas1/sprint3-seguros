import json
import os
import sys
from sqlalchemy import select
from sqlalchemy.orm import Session 


# Usando importações RELATIVAS para módulos dentro do pacote 'src'
from .database import create_schema, SessionLocal
from .dao import (
	init_admin, # CORRIGIDO: Era 'create_initial_admin', alterado para 'init_admin'
	create_cliente,
	create_apolice, 
	create_sinistro, 
	get_apolice_by_numero 
)
from .models import User, Cliente, Apolice 
from .logger import get_logger
from .exceptions import BusinessError
from .utils import parse_date, validar_cpf

# Adiciona o diretório raiz do projeto ao path para que as importações relativas funcionem ao executar como módulo
# Isso garante que mesmo que o script seja executado de outras formas, ele encontre os pacotes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

MIGRATION_USER = "migration_v2" 

def run_migration():
	logger = get_logger(MIGRATION_USER, "MIGRATION")
	print("\n--- Iniciando Migração de JSON para SQLite ---")
	
	# 1. Cria a estrutura do banco (schema)
	create_schema()
	db: Session = SessionLocal()

	try:
		# 2. Cria os Usuários Iniciais
		admin_user = init_admin(db, "admin", "admin123", "admin") # CORRIGIDO: Usando 'init_admin'
		migration_user = init_admin(db, MIGRATION_USER, "nao_usar", "admin") # CORRIGIDO: Usando 'init_admin'

		# Dicionário para mapear CPF antigo para o novo ID no DB
		cpf_to_id = {} 
		# Lista para guardar números das apólices migrados e seus IDs
		apolice_num_to_id = {}

		# 3. Processar JSONs da Sprint 2
		DATA_PATH = os.path.join("data", "sprint2")
		
		# A. Migração de Clientes
		clientes_path = os.path.join(DATA_PATH, "clientes.json")
		if os.path.exists(clientes_path):
			with open(clientes_path, encoding="utf-8") as f:
				clientes_json = json.load(f)
			
			print(f"Migrando {len(clientes_json)} clientes...")
			
			for cliente_data in clientes_json:
				try:
					data = {
						"nome": cliente_data.get("nome"),
						"cpf": cliente_data.get("cpf"),
						"data_nasc": cliente_data.get("data_nascimento"),
						"telefone": cliente_data.get("telefone"),
						"email": cliente_data.get("email"),
						"endereco": cliente_data.get("endereco")
					}
					
					cliente = create_cliente(db, data, user=migration_user)
					cpf_to_id[validar_cpf(cliente_data.get("cpf"))] = cliente.id
					logger.info(f"Cliente {cliente.cpf} migrado (ID={cliente.id}).")
				
				except BusinessError as e:
					logger.warning(f"Falha ao migrar cliente {cliente_data.get('cpf')}: {e}")
				except Exception as e:
					logger.error(f"Erro FATAL ao migrar cliente {cliente_data.get('cpf')}: {e}", exc_info=True)
		else:
			logger.error(f"Arquivo de clientes não encontrado em: {clientes_path}")


		# B. Migração de Apólices 
		apolices_path = os.path.join(DATA_PATH, "apolices.json")
		if os.path.exists(apolices_path):
			with open(apolices_path, encoding="utf-8") as f:
				apolices_json = json.load(f)

			print(f"Migrando {len(apolices_json)} apólices...")

			for apolice_data in apolices_json:
				cpf_cliente = validar_cpf(apolice_data.get("cpf_cliente"))

				if cpf_cliente not in cpf_to_id:
					logger.warning(f"Apólice N°{apolice_data.get('numero')} ignorada: Cliente {cpf_cliente} não migrado.")
					continue
				
				# Adaptação para o formato esperado por create_apolice
				try:
					apolice_payload = {
						"cpf_cliente": cpf_cliente,
						"premio": apolice_data.get("seguro", {}).get("premio_liquido"), 
						"tipo_seguro": apolice_data.get("seguro", {}).get("tipo"), 
						"dados_seguro": apolice_data.get("seguro") 
					}
					
					# Validação adicional
					if not apolice_payload.get("premio") or not apolice_payload.get("tipo_seguro"):
						apolice_payload["premio"] = apolice_data.get("valor_premio")
						apolice_payload["tipo_seguro"] = apolice_data.get("seguro", {}).get("tipo")

					
					apolice = create_apolice(db, apolice_payload, user=migration_user)
					
					# Mapeia o número da nova apólice gerada para uso na migração de sinistros
					apolice_num_to_id[apolice.numero] = apolice.id
					logger.info(f"Apólice N°{apolice.numero} migrada (ID={apolice.id}).")

				except BusinessError as e:
					logger.warning(f"Falha ao migrar apólice {apolice_data.get('numero')}: {e}")
				except Exception as e:
					logger.error(f"Erro FATAL ao migrar apólice {apolice_data.get('numero')}: {e}", exc_info=True)
		else:
			logger.error(f"Arquivo de apólices não encontrado em: {apolices_path}")


		# C. Migração de Sinistros 
		sinistros_path = os.path.join(DATA_PATH, "sinistros.json")
		if os.path.exists(sinistros_path):
			with open(sinistros_path, encoding="utf-8") as f:
				sinistros_json = json.load(f)
			
			print(f"Migrando {len(sinistros_json)} sinistros...")

			for sinistro_data in sinistros_json:
				numero_apolice = sinistro_data.get("numero_apolice")

				# Se a apólice não foi migrada, o sinistro é ignorado
				if numero_apolice not in apolice_num_to_id:
					logger.warning(f"Sinistro ID={sinistro_data.get('id')} ignorado: Apólice {numero_apolice} não foi migrada ou não existe.")
					continue
				
				try:
					# Adaptação para o formato esperado por create_sinistro
					sinistro_payload = {
						"numero_apolice": numero_apolice,
						"data": sinistro_data.get("data_ocorrencia"), 
						"descricao": sinistro_data.get("descricao"),
					}
					
					# Cria o sinistro. Aqui usamos a Apólice que *foi* gerada no DB.
					sinistro = create_sinistro(db, sinistro_payload, user=migration_user)
					logger.info(f"Sinistro migrado (ID={sinistro.id}) para Apólice N°{numero_apolice}.")

				except BusinessError as e:
					logger.warning(f"Falha ao migrar sinistro da apólice {numero_apolice}: {e}")
				except Exception as e:
					logger.error(f"Erro FATAL ao migrar sinistro da apólice {numero_apolice}: {e}", exc_info=True)
		else:
			logger.warning(f"Arquivo de sinistros não encontrado em: {sinistros_path}. Nenhuma migração de sinistros executada.")

		print("--- Migração Concluída ---")
		logger.info("Migração de dados finalizada.")

	finally:
		db.close()


if __name__ == "__main__":
	
	if not os.path.exists(os.path.join("data", "sprint2")):
		
		os.makedirs(os.path.join("data", "sprint2"))
		print("ERRO: A pasta 'data/sprint2/' não foi encontrada. Ela foi criada.")
		print("POR FAVOR, coloque seus arquivos 'clientes.json', 'apolices.json' e 'sinistros.json' da Sprint 2 nesta pasta.")
	else:
		run_migration()
