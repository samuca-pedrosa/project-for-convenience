from datetime import datetime
from typing import Optional

from src.dados.itensvenda_repository import ItensVendaRepository
from src.dados.produto_repository import ProdutoRepository
from src.dados.vendas_repository import VendasRepository
from src.dominio.itens_venda import Itens_venda
from src.dominio.venda import Venda


class VendaService:
    """
    Camada de negócio: orquestra a criação de uma venda e seus itens.

    Regras aplicadas:
    - a venda precisa ter ao menos um item;
    - cada item precisa de um produto existente e quantidade positiva;
    - o estoque do produto e' verificado e baixado ao confirmar a venda;
    - o total da venda e' calculado a partir do preco atual dos produtos.
    """

    def __init__(
        self,
        repositorio_venda: VendasRepository,
        repositorio_item: ItensVendaRepository,
        repositorio_produto: ProdutoRepository,
    ) -> None:
        self.repositorio_venda = repositorio_venda
        self.repositorio_item = repositorio_item
        self.repositorio_produto = repositorio_produto

    def registrar_venda(
        self,
        itens: list[dict],
        id_cliente: Optional[int] = None,
        forma_pagamento: str = "Nao informado",
    ) -> Venda:
        if not itens:
            raise ValueError("A venda precisa ter ao menos um item.")

        if not forma_pagamento or not forma_pagamento.strip():
            raise ValueError("Informe a forma de pagamento da venda.")

        itens_validados = []
        total = 0.0

        for item in itens:
            id_produto = item.get("id_produto")
            quantidade = item.get("quantidade")

            if not id_produto:
                raise ValueError("Cada item precisa informar o id_produto.")
            if quantidade is None or quantidade <= 0:
                raise ValueError("A quantidade de cada item deve ser maior que zero.")

            produto = self.repositorio_produto.buscar_por_id(id_produto)
            if produto is None:
                raise ValueError(f"Produto com id {id_produto} nao foi encontrado.")
            if produto.estoque < quantidade:
                raise ValueError(
                    f"Estoque insuficiente para o produto '{produto.nome}'. "
                    f"Disponivel: {produto.estoque}, solicitado: {quantidade}."
                )

            subtotal = float(produto.preco) * int(quantidade)
            total += subtotal
            itens_validados.append((produto, quantidade))

        venda = Venda(
            id_venda=None,
            id_cliente=id_cliente,
            data_venda=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total=round(total, 2),
            forma_pagamento=forma_pagamento.strip(),
        )
        novo_id_venda = self.repositorio_venda.adicionar(venda)
        venda.id_venda = novo_id_venda

        for produto, quantidade in itens_validados:
            item_venda = Itens_venda(
                id_item=None,
                id_venda=novo_id_venda,
                id_produto=produto.id,
                quantidade=quantidade,
                preco_unit=float(produto.preco),
            )
            self.repositorio_item.adicionar(item_venda)

            produto.estoque -= quantidade
            self.repositorio_produto.atualizar(produto)

        return venda

    def listar_vendas(self) -> list[Venda]:
        return self.repositorio_venda.listar_todos()

    def buscar_venda_por_id(self, id_venda: int) -> Optional[Venda]:
        if id_venda <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio_venda.buscar_por_id(id_venda)

    def listar_itens_da_venda(self, id_venda: int) -> list[Itens_venda]:
        if id_venda <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        itens = self.repositorio_item.listar_todos()
        return [item for item in itens if item.id_venda == id_venda]

    def remover_venda(self, id_venda: int) -> bool:
        if id_venda <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio_venda.remover(id_venda)
