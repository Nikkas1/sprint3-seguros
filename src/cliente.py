import re
from datetime import datetime
from utils import validar_cpf, validar_data

class Cliente:
    def __init__(self, nome, cpf, data_nasc, endereco, telefone, email):
        if not nome.strip():
            raise ValueError("Nome é obrigatório.")
        if not validar_cpf(cpf):
            raise ValueError("CPF inválido.")
        if not validar_data(data_nasc):
            raise ValueError("Data de nascimento inválida (use DD/MM/AAAA).")
        if not email or "@" not in email:
            raise ValueError("E-mail inválido.")
        
        self.nome = nome
        self.cpf = cpf
        self.data_nasc = data_nasc
        self.endereco = endereco
        self.telefone = telefone
        self.email = email

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Cliente(
            d['nome'], d['cpf'], d['data_nasc'],
            d['endereco'], d['telefone'], d['email']
        )

    def atualizar_dados(self, telefone=None, email=None, endereco=None):
        if telefone:
            self.telefone = telefone
        if email:
            if "@" not in email:
                raise ValueError("E-mail inválido.")
            self.email = email
        if endereco:
            self.endereco = endereco