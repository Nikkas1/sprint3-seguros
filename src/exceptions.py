# src/exceptions.py


class BusinessError(Exception):
    """Classe base para erros de negócio. Mensagem amigável para o usuário."""

    pass


class CpfInvalido(BusinessError):
    # O CPF aqui pode ser o CPF em si, ou uma mensagem de "CPF já existe"
    def __init__(self, message="CPF inválido ou já está em uso."):
        super().__init__(message)


class ApoliceInexistente(BusinessError):
    def __init__(self, numero):
        super().__init__(f"Apólice número '{numero}' não encontrada.")


class OperacaoNaoPermitida(BusinessError):
    def __init__(self, message="Operação não permitida para este perfil de usuário."):
        super().__init__(message)


class LoginInvalido(BusinessError):
    def __init__(self):
        super().__init__("Usuário ou senha inválidos.")


class SinistroInvalido(BusinessError):
    def __init__(self, message="Sinistro inválido ou apólice sem sinistro ativo."):
        super().__init__(message)
