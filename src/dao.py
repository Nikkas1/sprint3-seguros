import re
from sqlalchemy.orm import Session
from sqlalchemy import select, exc, func, case, desc
import datetime
import json

from .database import SessionLocal 
from .models import User, Cliente, Apolice, Sinistro, Audit 
from .exceptions import BusinessError, CpfInvalido, ApoliceInexistente, LoginInvalido
from .utils import validar_cpf, hash_password, verify_password, parse_date, gerar_numero_apolice
from .logger import get_logger 

def _log_audit(db: Session, user: User, operation: str, entity: str, entity_id: str, payload: dict = None):
    if payload is None:
        payload = {}
        
    audit = Audit(
        user_id=user.id if user else None,
        operation=operation,
        entity=entity,
        entity_id=str(entity_id),
        payload=json.dumps(payload) 
    )
    db.add(audit)

def get_db():
    return SessionLocal()

def init_admin(db: Session, username: str = "admin", password: str = "Sompo123", role: str = "admin"):
    logger = get_logger(operation="SETUP")
    
    if db.scalar(select(User).where(User.username == username)):
        return db.scalar(select(User).where(User.username == username))
    
    hashed_pwd = hash_password(password) 
    
    user = User(username=username, password_hash=hashed_pwd, role=role)
    db.add(user)
    db.commit()
    logger.info(f"Usuário '{username}' criado com sucesso.")
    return user

def authenticate_user(db: Session, username: str, password: str):
    logger = get_logger(username, "LOGIN")
    
    user = db.scalar(select(User).where(User.username == username))
    
    if user and verify_password(user.password_hash, password):
        logger.info("Login bem-sucedido.")
        return user
    else:
        logger.warning(f"Tentativa de login inválida para o usuário: {username}.")
        raise LoginInvalido()

def create_cliente(db: Session, data: dict, user: User):
    logger = get_logger(user.username, "CREATE_CLIENTE")
    
    try:
        cpf_limpo = validar_cpf(data.get("cpf"))
        
        if db.scalar(select(Cliente).where(Cliente.cpf == cpf_limpo)):
            raise CpfInvalido(f"CPF {cpf_limpo} já está cadastrado.")

        cliente = Cliente(
            nome=data["nome"], 
            cpf=cpf_limpo, 
            data_nascimento=parse_date(data.get("data_nasc")),
            telefone=data.get("telefone"), 
            email=data.get("email"), 
            endereco=data.get("endereco")
        )
        db.add(cliente)
        db.flush()
        
        _log_audit(db, user, "CREATE_CLIENTE", "Cliente", cliente.id, data)
        db.commit()
        logger.info(f"Cliente criado ID={cliente.id}, CPF={cliente.cpf}")
        
        return cliente
        
    except BusinessError:
        db.rollback() 
        raise 
        
    except exc.IntegrityError as e:
        db.rollback()
        logger.error(f"Erro de integridade ao criar cliente: {e}", exc_info=True)
        raise BusinessError("Erro: CPF já cadastrado.")
        
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao criar cliente", exc_info=True)
        raise BusinessError("Erro interno ao salvar o cliente. Consulte logs.")

def get_cliente_by_cpf(db: Session, cpf: str):
    cpf_limpo = validar_cpf(cpf)
    return db.scalar(select(Cliente).where(Cliente.cpf == cpf_limpo))

def update_cliente(db: Session, cpf: str, telefone: str = None, email: str = None, endereco: str = None, user: User = None):
    logger = get_logger(user.username, "UPDATE_CLIENTE")
    
    try:
        cpf_limpo = validar_cpf(cpf)
        cliente = db.scalar(select(Cliente).where(Cliente.cpf == cpf_limpo))
        
        if not cliente:
            raise CpfInvalido("Cliente não encontrado com o CPF fornecido.")
        
        updates = {}
        
        if telefone is not None and telefone != cliente.telefone:
            updates['telefone'] = {'antigo': cliente.telefone, 'novo': telefone}
            cliente.telefone = telefone

        if email is not None and email != cliente.email:
            updates['email'] = {'antigo': cliente.email, 'novo': email}
            cliente.email = email

        if endereco is not None and endereco != cliente.endereco:
            updates['endereco'] = {'antigo': cliente.endereco, 'novo': endereco}
            cliente.endereco = endereco

        if not updates:
            logger.info(f"Cliente CPF={cpf_limpo} encontrado, mas nenhum dado foi alterado.")
            return cliente

        _log_audit(db, user, "UPDATE_CLIENTE", "Cliente", cliente.id, updates)
        
        db.commit()
        logger.info(f"Cliente CPF={cpf_limpo} atualizado. Campos alterados: {list(updates.keys())}") 
        
        return cliente
        
    except BusinessError:
        db.rollback() 
        raise 
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar cliente CPF={cpf}", exc_info=True)
        raise BusinessError("Erro interno ao atualizar o cliente. Consulte logs.")

def create_apolice(db: Session, data: dict, user: User):
    logger = get_logger(user.username, "CREATE_APOLICE")

    try:
        cpf_limpo = validar_cpf(data.get("cpf_cliente"))
        cliente = db.scalar(select(Cliente).where(Cliente.cpf == cpf_limpo))
        
        if not cliente:
            raise CpfInvalido("Cliente não encontrado.")

        num_apolice = gerar_numero_apolice()
        
        data_inicio_hoje = datetime.date.today()
        data_fim_proximo_ano = data_inicio_hoje.replace(year=data_inicio_hoje.year + 1)
        
        dados_seguro_json = json.dumps(data.get("dados_seguro")) 
        
        apolice = Apolice(
            numero=num_apolice,
            cliente_id=cliente.id,
            premio=data["premio"],
            data_inicio=data_inicio_hoje,
            data_fim=data_fim_proximo_ano,
            tipo=data.get("tipo_seguro"), 
            dados_seguro=dados_seguro_json, 
            status="Ativa"
        )
        db.add(apolice)
        db.flush() 

        _log_audit(db, user, "CREATE_APOLICE", "Apolice", apolice.id, data)
        db.commit() 
        logger.info(f"Apólice N°{apolice.numero} criada para o Cliente ID={cliente.id}.")
        
        return apolice

    except BusinessError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao criar apólice", exc_info=True)
        raise BusinessError("Erro interno ao emitir a apólice. Consulte logs.")
        
def get_apolice_by_numero(db: Session, numero: str):
    apolice = db.scalar(select(Apolice).where(Apolice.numero == numero))
    
    if not apolice:
        raise ApoliceInexistente(f"Apólice N°{numero} não encontrada.")
    
    try:
        if apolice.dados_seguro:
            apolice.dados_seguro = json.loads(apolice.dados_seguro)
        else:
            apolice.dados_seguro = {}
    except json.JSONDecodeError:
        get_logger("system", "ERROR").error(f"Erro ao desserializar dados_seguro da Apólice N°{numero}. Conteúdo: {apolice.dados_seguro}")
        apolice.dados_seguro = {} 

    return apolice

def cancel_apolice(db: Session, numero: str, user: User):
    logger = get_logger(user.username, "CANCEL_APOLICE")
    
    try:
        apolice = get_apolice_by_numero(db, numero) 
        
        if apolice.status != "Ativa":
            raise BusinessError(f"Apólice N°{numero} já está '{apolice.status}'.")

        apolice.status = "Cancelada"
        updates = {"status": {"antigo": "Ativa", "novo": "Cancelada"}}

        _log_audit(db, user, "CANCEL_APOLICE", "Apolice", apolice.id, updates)
        
        db.commit()
        logger.info(f"Apólice N°{numero} cancelada.")
        
        return apolice

    except BusinessError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao cancelar apólice N°{numero}", exc_info=True)
        raise BusinessError("Erro interno ao cancelar a apólice. Consulte logs.")

def create_sinistro(db: Session, data: dict, user: User):
    logger = get_logger(user.username, "CREATE_SINISTRO")

    try:
        numero_apolice = data.get("numero_apolice")
        
        apolice = get_apolice_by_numero(db, numero_apolice)
        
        if apolice.status != "Ativa":
            raise BusinessError(f"Apólice N°{numero_apolice} não está ativa (Status: {apolice.status}).")

        sinistro = Sinistro(
            apolice_id=apolice.id,
            data=parse_date(data.get("data")),
            descricao=data["descricao"],
            status="Aberto"
        )
        db.add(sinistro)
        db.flush() 

        _log_audit(db, user, "CREATE_SINISTRO", "Sinistro", sinistro.id, data)
        db.commit() 
        logger.info(f"Sinistro ID={sinistro.id} registrado na Apólice ID={apolice.id}.")
        
        return sinistro

    except BusinessError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao registrar sinistro", exc_info=True)
        raise BusinessError("Erro interno ao registrar o sinistro. Consulte logs.")

def update_sinistro_status(db: Session, numero_apolice: str, novo_status: str, user: User):
    logger = get_logger(user.username, "UPDATE_SINISTRO")
    
    STATUS_PERMITIDOS = ["Aberto", "Em Análise", "Fechado", "Recusado"] 
    
    if novo_status not in STATUS_PERMITIDOS:
        raise BusinessError(f"Status inválido: {novo_status}. Use: {', '.join(STATUS_PERMITIDOS)}.")
        
    try:
        sinistro = db.scalar(
            select(Sinistro)
            .join(Apolice)
            .where(Apolice.numero == numero_apolice)
            .order_by(Sinistro.id.desc())
        )
        
        if not sinistro:
            raise BusinessError(f"Sinistro não encontrado para a Apólice N°{numero_apolice}.")
            
        updates = {"status": {"antigo": sinistro.status, "novo": novo_status}}
        sinistro.status = novo_status

        _log_audit(db, user, "UPDATE_SINISTRO", "Sinistro", sinistro.id, updates)
        
        db.commit()
        logger.info(f"Status do Sinistro ID={sinistro.id} atualizado para '{novo_status}'.")
        
        return sinistro

    except BusinessError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar Sinistro da Apólice N°{numero_apolice}", exc_info=True)
        raise BusinessError("Erro interno ao atualizar o status do sinistro. Consulte logs.")

def relatorio_valor_segurado_por_cliente(db: Session):
    query = select(
        Cliente.nome,
        Cliente.cpf,
        func.sum(Apolice.premio).label('valor_total_segurado')
    ).join(Apolice, Cliente.id == Apolice.cliente_id).where(Apolice.status == 'Ativa').group_by(Cliente.id, Cliente.nome, Cliente.cpf)
    
    resultados = db.execute(query).all()
    
    relatorio = [
        {"nome": r.nome, "cpf": r.cpf, "valor_total_segurado": float(r.valor_total_segurado or 0)} 
        for r in resultados
    ]
    return relatorio

def relatorio_apolices_por_tipo(db: Session):
    query = select(
        Apolice.tipo, 
        func.count(Apolice.id).label('quantidade')
    ).where(Apolice.status == 'Ativa').group_by(Apolice.tipo)
    
    resultados = db.execute(query).all()
    
    relatorio = {r.tipo: r.quantidade for r in resultados}
    return relatorio

def relatorio_sinistros_status(db: Session):
    query = select(
        Sinistro.status,
        func.count(Sinistro.id).label('quantidade')
    ).group_by(Sinistro.status)
    
    resultados = db.execute(query).all()
    
    relatorio = {r.status: r.quantidade for r in resultados}
    return relatorio

def relatorio_ranking_clientes(db: Session):
    query = select(
        Cliente.nome,
        Cliente.cpf,
        func.count(Apolice.id).label('total_apolices_ativas')
    ).join(Apolice, Cliente.id == Apolice.cliente_id).where(Apolice.status == 'Ativa').group_by(Cliente.id, Cliente.nome, Cliente.cpf).order_by(desc('total_apolices_ativas'))
    
    resultados = db.execute(query).all()
    
    relatorio = [
        {"nome": r.nome, "cpf": r.cpf, "apolices": r.total_apolices_ativas} 
        for r in resultados
    ]
    return relatorio
