from typing import Optional

from src.dados.produto_repository import ProdutoRepository
from src.dominio.produtos import Produtos


class ProdutoService:
    """Camada de negócio: aplica validações e regras simples."""

    def __init__(self, repositorio: ProdutoRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_produto(
        self, nome: str, categoria: str, preco: float, estoque: int
    ) -> Produtos:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do produto nao pode ficar vazio.")

        categoria_limpa = categoria.strip()
        if not categoria_limpa:
            raise ValueError("A categoria do produto nao pode ficar vazia.")

        if preco < 0:
            raise ValueError("O preco do produto nao pode ser negativo.")

        if estoque < 0:
            raise ValueError("O estoque do produto nao pode ser negativo.")

        produto = Produtos(
            id=None,
            nome=nome_limpo,
            categoria=categoria_limpa,
            preco=preco,
            estoque=estoque,
        )
        novo_id = self.repositorio.adicionar(produto)
        produto.id = novo_id
        return produto

    def listar_produtos(self) -> list[Produtos]:
        return self.repositorio.listar_todos()

    def buscar_produto_por_id(self, id_produto: int) -> Optional[Produtos]:
        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio.buscar_por_id(id_produto)

    def atualizar_produto(
        self, id_produto: int, nome: str, categoria: str, preco: float, estoque: int
    ) -> bool:
        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do produto nao pode ficar vazio.")

        categoria_limpa = categoria.strip()
        if not categoria_limpa:
            raise ValueError("A categoria do produto nao pode ficar vazia.")

        if preco < 0:
            raise ValueError("O preco do produto nao pode ser negativo.")

        if estoque < 0:
            raise ValueError("O estoque do produto nao pode ser negativo.")

        produto = Produtos(
            id=id_produto,
            nome=nome_limpo,
            categoria=categoria_limpa,
            preco=preco,
            estoque=estoque,
        )
        return self.repositorio.atualizar(produto)

    def remover_produto(self, id_produto: int) -> bool:
        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio.remover(id_produto)
