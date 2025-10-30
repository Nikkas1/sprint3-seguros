import mysql.connector
from mysql.connector import Error as MySQLError

# --- CONFIGURAÇÕES DO RDS (CORRIGIDAS) ---
ENDPOINT = "sprint4-seguros.cizdwekfp2hc.us-east-1.rds.amazonaws.com"
# CREDENCIAIS CORRETAS PARA O TESTE:
USERNAME = "lambda_user_legacy"
PASSWORD = "NovaSenhaLambda2025!"
DATABASE_NAME = "seguro_db"
DB_PORT = 3306


def get_mysql_connection():
    """Tenta estabelecer e retornar uma nova conexão MySQL usando mysql.connector."""
    try:
        conn = mysql.connector.connect(
            host=ENDPOINT,
            user=USERNAME,
            password=PASSWORD,
            database=DATABASE_NAME,
            port=DB_PORT,
            connection_timeout=10,
        )
        return conn
    except MySQLError as e:
        # Se a conexão falhar agora, verifique o Security Group ou se a tabela existe.
        print(f"❌ Erro de Conexão MySQL: {e}")
        return None


def insert_cliente(nome: str, email: str) -> int | None:
    """Insere um novo cliente e retorna seu ID."""
    conn = get_mysql_connection()
    if conn is None:
        return None

    insert_query = "INSERT INTO clientes (nome, email) VALUES (%s, %s)"
    cur = conn.cursor()

    try:
        cur.execute(insert_query, (nome, email))
        conn.commit()
        cliente_id = cur.lastrowid
        return cliente_id
    except MySQLError as e:
        print(f"❌ Erro SQL ao inserir cliente: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def delete_cliente(cliente_id: int) -> bool:
    """Remove um cliente pelo ID. Crucial para limpeza de testes."""
    conn = get_mysql_connection()
    if conn is None:
        return False

    delete_query = "DELETE FROM clientes WHERE id = %s"
    cur = conn.cursor()

    try:
        cur.execute(delete_query, (cliente_id,))
        conn.commit()
        return cur.rowcount > 0
    except MySQLError as e:
        print(f"❌ Erro SQL ao deletar cliente: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def insert_apolice(
    cliente_id: int, tipo: str, valor: float, data_inicio: str
) -> int | None:
    """Insere uma nova apólice na tabela 'apolices' e retorna seu ID (nova função necessária)."""
    conn = get_mysql_connection()
    if conn is None:
        return None

    insert_query = """
    INSERT INTO apolices (cliente_id, tipo, valor, data_inicio) 
    VALUES (%s, %s, %s, %s)
    """
    cur = conn.cursor()

    try:
        cur.execute(insert_query, (cliente_id, tipo, valor, data_inicio))
        conn.commit()
        # lastrowid é o ID da última inserção
        apolice_id = cur.lastrowid
        return apolice_id
    except MySQLError as e:
        print(f"❌ Erro SQL ao inserir apólice: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()
