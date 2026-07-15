from typing import Optional

import mysql.connector

from src.dominio.itens_venda import Itens_venda


class ItensVendaRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao
        self._criar_tabela()

    def _criar_tabela(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS itens_venda (
            id_item      INT            NOT NULL AUTO_INCREMENT,
            id_venda     INT            NOT NULL,
            id_produto   INT            NOT NULL,
            quantidade   INT            NOT NULL,
            preco_unit   DECIMAL(10, 2) NOT NULL,
            PRIMARY KEY (id_item),
            FOREIGN KEY (id_venda)   REFERENCES vendas(id_venda),
            FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
        )
        """
        cursor = self.conexao.cursor()
        cursor.execute(sql)
        self.conexao.commit()
        cursor.close()

    def adicionar(self, item: Itens_venda) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unit) VALUES (%s, %s, %s, %s)",
            (item.id_venda, item.id_produto, item.quantidade, item.preco_unit),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Itens_venda]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_item, id_venda, id_produto, quantidade, preco_unit FROM itens_venda ORDER BY id_item"
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [
            Itens_venda(
                id_item=linha["id_item"],
                id_venda=linha["id_venda"],
                id_produto=linha["id_produto"],
                quantidade=linha["quantidade"],
                preco_unit=float(linha["preco_unit"]),
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_item: int) -> Optional[Itens_venda]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_item, id_venda, id_produto, quantidade, preco_unit FROM itens_venda WHERE id_item = %s",
            (id_item,),
        )
        linha = cursor.fetchone()
        cursor.close()
        if linha is None:
            return None
        return Itens_venda(
            id_item=linha["id_item"],
            id_venda=linha["id_venda"],
            id_produto=linha["id_produto"],
            quantidade=linha["quantidade"],
            preco_unit=float(linha["preco_unit"]),
        )

    def atualizar(self, item: Itens_venda) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE itens_venda SET id_venda = %s, id_produto = %s, quantidade = %s, preco_unit = %s WHERE id_item = %s",
            (item.id_venda, item.id_produto, item.quantidade, item.preco_unit, item.id_item),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_item: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM itens_venda WHERE id_item = %s",
            (id_item,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados