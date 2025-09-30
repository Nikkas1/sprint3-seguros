from sqlalchemy import Column, Integer, String, Date, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime as dt_class 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="comum") 

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    data_nascimento = Column(Date) 
    
    telefone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    
    apolices = relationship("Apolice", back_populates="cliente") 

class Apolice(Base):
    __tablename__ = "apolices"
    id = Column(Integer, primary_key=True)
    numero = Column(String, unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    premio = Column(Float, nullable=False)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    status = Column(String, default="Ativa") 
    
    
    tipo = Column(String, nullable=False)
    
    cliente = relationship("Cliente", back_populates="apolices") 
    
    dados_seguro = Column(JSON) 

    sinistros = relationship("Sinistro", back_populates="apolice") 

class Sinistro(Base):
    __tablename__ = "sinistros"
    id = Column(Integer, primary_key=True)
    apolice_id = Column(Integer, ForeignKey("apolices.id"))
    data = Column(Date)
    status = Column(String, default="Aberto") 
    descricao = Column(String)
    
    apolice = relationship("Apolice", back_populates="sinistros")

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=dt_class.utcnow) 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operation = Column(String)
    entity = Column(String)
    entity_id = Column(String)
    payload = Column(JSON)
    user = relationship("User")
