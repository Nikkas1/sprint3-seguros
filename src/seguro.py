from datetime import datetime

class Seguro:
    def __init__(self, valor):
        if valor <= 0:
            raise ValueError("Valor do seguro deve ser positivo.")
        self.valor = valor

    def calcular_premio(self):
        raise NotImplementedError("Subclasses devem implementar 'calcular_premio'")

    def valor_premio(self): 
        return self.valor * 0.02

    def to_dict(self):
        return {'tipo': self.__class__.__name__, 'valor': self.valor}

class SeguroAutomovel(Seguro):
    def __init__(self, modelo, ano, placa, valor):
        super().__init__(valor)
        if not modelo.strip():
            raise ValueError("Modelo é obrigatório.")
            
        if not (isinstance(ano, int) and 1900 <= ano <= datetime.now().year):
            raise ValueError("Ano inválido.")
            
        if not placa.strip():
            raise ValueError("Placa é obrigatória.")
            
        self.modelo = modelo
        self.ano = ano
        self.placa = placa

    def valor_premio(self): 
        return self.valor * 0.05 

    def to_dict(self):
        d = super().to_dict()
        d.update({'modelo': self.modelo, 'ano': self.ano, 'placa': self.placa})
        return d

    @staticmethod
    def from_dict(d):
        return SeguroAutomovel(d['modelo'], d['ano'], d['placa'], d['valor'])

class SeguroResidencial(Seguro):
    def __init__(self, endereco, valor):
        super().__init>(valor)
        if not endereco.strip():
            raise ValueError("Endereço é obrigatório.")
        self.endereco = endereco

    def valor_premio(self):
        return self.valor * 0.03

    def to_dict(self):
        d = super().to_dict()
        d.update({'endereco': self.endereco})
        return d

    @staticmethod
    def from_dict(d):
        return SeguroResidencial(d['endereco'], d['valor'])

class SeguroVida(Seguro):
    def __init__(self, beneficiarios, valor):
        super().__init__(valor)
        if not beneficiarios:
            raise ValueError("Pelo menos um beneficiário é obrigatório.")
        self.beneficiarios = beneficiarios

    def valor_premio(self):
        return self.valor * 0.01

    def to_dict(self):
        d = super().to_dict()
        d.update({'beneficiarios': self.beneficiarios})
        return d

    @staticmethod
    def from_dict(d):
        return SeguroVida(d['beneficiarios'], d['valor'])
