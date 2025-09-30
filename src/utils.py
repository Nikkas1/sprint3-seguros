import re
import hashlib
import os
import uuid
import random
import string
import datetime 
from .exceptions import CpfInvalido, BusinessError 

def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return salt.hex() + ":" + dk.hex()

def verify_password(stored_hash: str, provided_password: str) -> bool:
    try:
        salt_hex, dk_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        new_dk = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100_000)
        return new_dk.hex() == dk_hex
    except:
        return False

def validar_cpf(cpf: str) -> str:
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf_limpo) != 11 or cpf_limpo == cpf_limpo[0] * 11:
        raise CpfInvalido(f"CPF '{cpf}' deve ter 11 dígitos e não pode ser sequências repetidas.")
        
    for i in range(9, 11):
        soma = sum(int(cpf_limpo[num]) * ((i+1)-num) for num in range(0, i))
        digito = ((soma*10) % 11) % 10
        if digito != int(cpf_limpo[i]):
            raise CpfInvalido(f"Dígito verificador incorreto para o CPF '{cpf}'.")
            
    return cpf_limpo

def parse_date(data_str: str) -> datetime.date:
    if not data_str:
        return None
    try:
        return datetime.datetime.strptime(data_str, '%d/%m/%Y').date()
    except ValueError:
        raise BusinessError("Formato de data inválido. Use DD/MM/AAAA.") 

def gerar_numero_apolice() -> str:
    return str(uuid.uuid4())[:8].upper()

def calcular_premio_automovel(valor_veiculo: float, ano_veiculo: int) -> float:
    base_rate = 0.05
    current_year = datetime.date.today().year
    idade_veiculo = current_year - ano_veiculo
    
    fator_risco = 1.0
    if idade_veiculo > 5:
        fator_risco = 1.2
    elif idade_veiculo > 10:
        fator_risco = 1.5
        
    premio = valor_veiculo * base_rate * fator_risco
    
    return round(premio, 2)
