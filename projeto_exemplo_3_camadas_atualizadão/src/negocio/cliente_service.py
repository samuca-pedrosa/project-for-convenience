import re
from datetime import date
from typing import Optional

from src.dados.cliente_repository import ClienteRepository
from src.dominio.cliente import Clientes


class ClienteService:
    """Camada de negócio: aplica validações e regras simples para clientes."""

    def __init__(self, repositorio: ClienteRepository) -> None:
        self.repositorio = repositorio

    @staticmethod
    def _somente_digitos(valor: str) -> str:
        return re.sub(r"\D", "", valor or "")

    def cadastrar_cliente(
        self,
        nome: str,
        cpf: str,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Clientes:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do cliente nao pode ficar vazio.")

        cpf_limpo = self._somente_digitos(cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("O CPF deve conter 11 digitos.")

        cliente = Clientes(
            id=None,
            nome=nome_limpo,
            cpf=cpf_limpo,
            telefone=(telefone.strip() if telefone else None),
            email=(email.strip() if email else None),
            data_cadastro=str(date.today()),
        )
        novo_id = self.repositorio.adicionar(cliente)
        cliente.id = novo_id
        return cliente

    def listar_clientes(self) -> list[Clientes]:
        return self.repositorio.listar_todos()

    def buscar_cliente_por_id(self, id_cliente: int) -> Optional[Clientes]:
        if id_cliente <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio.buscar_por_id(id_cliente)

    def atualizar_cliente(
        self,
        id_cliente: int,
        nome: str,
        cpf: str,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        if id_cliente <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do cliente nao pode ficar vazio.")

        cpf_limpo = self._somente_digitos(cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("O CPF deve conter 11 digitos.")

        cliente_atual = self.repositorio.buscar_por_id(id_cliente)
        data_cadastro = cliente_atual.data_cadastro if cliente_atual else str(date.today())

        cliente = Clientes(
            id=id_cliente,
            nome=nome_limpo,
            cpf=cpf_limpo,
            telefone=(telefone.strip() if telefone else None),
            email=(email.strip() if email else None),
            data_cadastro=data_cadastro,
        )
        return self.repositorio.atualizar(cliente)

    def remover_cliente(self, id_cliente: int) -> bool:
        if id_cliente <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio.remover(id_cliente)
