from utils import validar_data


class Sinistro:
    def __init__(self, numero_apolice, descricao, data, status="Aberto"):
        if not validar_data(data):
            raise ValueError("Data do sinistro inválida (use DD/MM/AAAA).")
        if not descricao.strip():
            raise ValueError("Descrição é obrigatória.")
        self.numero_apolice = numero_apolice
        self.descricao = descricao
        self.data = data
        self.status = status

    def atualizar_status(self, novo_status):
        if novo_status not in ["Aberto", "Fechado", "Em Análise"]:
            raise ValueError("Status inválido. Use: Aberto, Fechado, Em Análise.")
        self.status = novo_status

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Sinistro(d["numero_apolice"], d["descricao"], d["data"], d["status"])
