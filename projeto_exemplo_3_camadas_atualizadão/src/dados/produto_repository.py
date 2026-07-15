from typing import Optional

import mysql.connector

from src.dominio.produtos import Produtos


class ProdutoRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao
        self._criar_tabela()

    def _criar_tabela(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto   INT            NOT NULL AUTO_INCREMENT,
            nome         VARCHAR(100)   NOT NULL,
            categoria    VARCHAR(50)    NOT NULL,
            preco        DECIMAL(10, 2) NOT NULL,
            estoque      INT            NOT NULL DEFAULT 0,
            PRIMARY KEY (id_produto)
        )
        """
        cursor = self.conexao.cursor()
        cursor.execute(sql)
        self.conexao.commit()
        cursor.close()

    def adicionar(self, produto: Produtos) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, categoria, preco, estoque) VALUES (%s, %s, %s, %s)",
            (produto.nome, produto.categoria, produto.preco, produto.estoque),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Produtos]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_produto, nome, categoria, preco, estoque FROM produtos ORDER BY id_produto"
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [
            Produtos(
                id=linha["id_produto"],
                nome=linha["nome"],
                categoria=linha["categoria"],
                preco=float(linha["preco"]),
                estoque=linha["estoque"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_produto: int) -> Optional[Produtos]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_produto, nome, categoria, preco, estoque FROM produtos WHERE id_produto = %s",
            (id_produto,),
        )
        linha = cursor.fetchone()
        cursor.close()
        if linha is None:
            return None
        return Produtos(
            id=linha["id_produto"],
            nome=linha["nome"],
            categoria=linha["categoria"],
            preco=float(linha["preco"]),
            estoque=linha["estoque"],
        )

    def atualizar(self, produto: Produtos) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = %s, categoria = %s, preco = %s, estoque = %s WHERE id_produto = %s",
            (produto.nome, produto.categoria, produto.preco, produto.estoque, produto.id),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_produto: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM produtos WHERE id_produto = %s",
            (id_produto,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados