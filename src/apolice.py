from datetime import datetime
from utils import validar_data
from seguro import SeguroAutomovel, SeguroResidencial, SeguroVida

class Apolice:
    def __init__(self, numero, cpf_cliente, seguro, data_emissao, status='Ativa'):
        if not validar_data(data_emissao):
            raise ValueError("Data de emissão inválida (use DD/MM/AAAA).")
        self.numero = numero
        self.cpf_cliente = cpf_cliente
        self.seguro = seguro
        self.data_emissao = data_emissao
        self.status = status

    def valor_premio(self):
        return self.seguro.calcular_premio()

    def cancelar(self):
        if self.status != 'Ativa':
            raise ValueError("Apólice já está cancelada ou inativa.")
        self.status = 'Cancelada'

    def to_dict(self):
        return {
            'numero': self.numero,
            'cpf_cliente': self.cpf_cliente,
            'seguro': self.seguro.to_dict(),
            'data_emissao': self.data_emissao,
            'status': self.status
        }

    @staticmethod
    def from_dict(d):
        tipo = d['seguro']['tipo']
        if tipo == 'SeguroAutomovel':
            seguro = SeguroAutomovel.from_dict(d['seguro'])
        elif tipo == 'SeguroResidencial':
            seguro = SeguroResidencial.from_dict(d['seguro'])
        elif tipo == 'SeguroVida':
            seguro = SeguroVida.from_dict(d['seguro'])
        else:
            raise ValueError(f"Tipo de seguro desconhecido: {tipo}")
        return Apolice(d['numero'], d['cpf_cliente'], seguro, d['data_emissao'], d['status'])