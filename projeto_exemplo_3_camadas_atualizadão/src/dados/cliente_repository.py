from typing import Optional

import mysql.connector

from src.dominio.cliente import Clientes


class ClienteRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao
        self._criar_tabela()

    def _criar_tabela(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente   INT          NOT NULL AUTO_INCREMENT,
            nome         VARCHAR(100) NOT NULL,
            cpf          VARCHAR(14)  NOT NULL UNIQUE,
            telefone     VARCHAR(15),
            email        VARCHAR(100),
            data_cadastro DATE        NOT NULL DEFAULT (CURRENT_DATE),
            PRIMARY KEY (id_cliente)
        )
        """
        cursor = self.conexao.cursor()
        cursor.execute(sql)
        self.conexao.commit()
        cursor.close()

    def adicionar(self, cliente: Clientes) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, cpf, telefone, email, data_cadastro) VALUES (%s, %s, %s, %s, %s)",
            (cliente.nome, cliente.cpf, cliente.telefone, cliente.email, cliente.data_cadastro),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Clientes]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_cliente, nome, cpf, telefone, email, data_cadastro FROM clientes ORDER BY id_cliente"
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [
            Clientes(
                id=linha["id_cliente"],
                nome=linha["nome"],
                cpf=linha["cpf"],
                telefone=linha["telefone"],
                email=linha["email"],
                data_cadastro=str(linha["data_cadastro"]),
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_cliente: int) -> Optional[Clientes]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_cliente, nome, cpf, telefone, email, data_cadastro FROM clientes WHERE id_cliente = %s",
            (id_cliente,),
        )
        linha = cursor.fetchone()
        cursor.close()
        if linha is None:
            return None
        return Clientes(
            id=linha["id_cliente"],
            nome=linha["nome"],
            cpf=linha["cpf"],
            telefone=linha["telefone"],
            email=linha["email"],
            data_cadastro=str(linha["data_cadastro"]),
        )

    def atualizar(self, cliente: Clientes) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE clientes SET nome = %s, cpf = %s, telefone = %s, email = %s, data_cadastro = %s WHERE id_cliente = %s",
            (cliente.nome, cliente.cpf, cliente.telefone, cliente.email, cliente.data_cadastro, cliente.id),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_cliente: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM clientes WHERE id_cliente = %s",
            (id_cliente,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados