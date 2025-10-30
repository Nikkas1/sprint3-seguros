import pymysql
import json
import boto3
import csv
from io import StringIO
from pymysql.err import OperationalError

# --- CONFIGURAÇÕES DO BANCO RDS ---
# Credenciais baseadas no seu db_mysql.py e no enunciado da Lambda
ENDPOINT = "sprint4-seguros.cizdwekfp2hc.us-east-1.rds.amazonaws.com"
USERNAME = "lambda_user"  # ALTERADO: Usa o novo usuário configurado no RDS
PASSWORD = "adminadmin"  # Sua senha do RDS
DATABASE_NAME = "seguro_db"
DB_PORT = 3306

# Cliente S3 (Boto3) para interagir com o bucket
s3 = boto3.client("s3")


def lambda_handler(event, context):
    rows_inserted = 0

    # 1. Tenta extrair o nome do bucket e a chave do arquivo do evento S3
    try:
        # Pega o bucket e a chave (nome do arquivo) do evento que o S3 dispara
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
    except Exception as e:
        # Se não for um evento S3, retorna erro
        return {
            "statusCode": 400,
            "body": json.dumps(
                f"❌ Erro ao extrair info do S3. Não é um evento S3 válido: {str(e)}"
            ),
        }

    print(f"Iniciando processamento do arquivo: s3://{bucket_name}/{key}")

    try:
        # 2. Conexão ao Banco de Dados RDS (MySQL)
        conn = pymysql.connect(
            host=ENDPOINT,
            user=USERNAME,
            passwd=PASSWORD,
            db=DATABASE_NAME,
            port=DB_PORT,
            connect_timeout=10,
            # Mantido: Força o uso da autenticação nativa, ignorando a necessidade do 'cryptography'
            auth_plugin="mysql_native_password",
        )
        cur = conn.cursor()

        # 3. Baixar e ler o conteúdo do arquivo CSV do S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        file_content = response["Body"].read().decode("utf-8")

        # 4. Processar o CSV linha por linha
        csv_file = StringIO(file_content)
        reader = csv.reader(csv_file)
        next(reader)  # Pula o cabeçalho (nome,email)

        # Query de Inserção (Ajustada para a sua tabela 'clientes')
        insert_query = "INSERT INTO clientes (nome, email) VALUES (%s, %s)"

        for row in reader:
            # Assumindo que o CSV tem as colunas na ordem (nome, email)
            if len(row) >= 2:
                # Usa %s para prevenir SQL Injection
                cur.execute(insert_query, (row[0], row[1]))
                rows_inserted += 1

        # 5. Commit e fechamento da conexão
        conn.commit()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps(
                f"✅ SUCESSO! {rows_inserted} clientes importados do arquivo {key}."
            ),
        }

    except OperationalError as e:
        # Erro comum se as permissões de rede/VPC ou credenciais estiverem erradas
        print(f"Erro de Conexão/SQL no RDS: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                f"❌ Erro de Conexão: Verifique IAM, VPC/SG e Credenciais. Erro: {str(e)}"
            ),
        }
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"❌ Erro ao processar arquivo S3/CSV: {str(e)}"),
        }
