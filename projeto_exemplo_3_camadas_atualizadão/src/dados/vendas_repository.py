from typing import Optional

import mysql.connector

from src.dominio.venda import Venda


class VendasRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao
        self._criar_tabela()
        self._garantir_coluna_forma_pagamento()

    def _criar_tabela(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS vendas (
            id_venda         INT            NOT NULL AUTO_INCREMENT,
            id_cliente       INT,
            data_venda       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
            total            DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            forma_pagamento  VARCHAR(30)    NOT NULL DEFAULT 'Nao informado',
            PRIMARY KEY (id_venda),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        )
        """
        cursor = self.conexao.cursor()
        cursor.execute(sql)
        self.conexao.commit()
        cursor.close()

    def _garantir_coluna_forma_pagamento(self) -> None:
        """Migracao leve: adiciona a coluna forma_pagamento em bancos criados
        antes dessa funcionalidade existir, sem exigir passo manual."""
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'vendas'
              AND column_name = 'forma_pagamento'
            """
        )
        (existe,) = cursor.fetchone()
        if not existe:
            cursor.execute(
                "ALTER TABLE vendas ADD COLUMN forma_pagamento VARCHAR(30) NOT NULL DEFAULT 'Nao informado'"
            )
            self.conexao.commit()
        cursor.close()

    def adicionar(self, venda: Venda) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO vendas (id_cliente, data_venda, total, forma_pagamento) VALUES (%s, %s, %s, %s)",
            (venda.id_cliente, venda.data_venda, venda.total, venda.forma_pagamento),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Venda]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_venda, id_cliente, data_venda, total, forma_pagamento FROM vendas ORDER BY id_venda"
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [
            Venda(
                id_venda=linha["id_venda"],
                id_cliente=linha["id_cliente"],
                data_venda=str(linha["data_venda"]),
                total=float(linha["total"]),
                forma_pagamento=linha["forma_pagamento"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_venda: int) -> Optional[Venda]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_venda, id_cliente, data_venda, total, forma_pagamento FROM vendas WHERE id_venda = %s",
            (id_venda,),
        )
        linha = cursor.fetchone()
        cursor.close()
        if linha is None:
            return None
        return Venda(
            id_venda=linha["id_venda"],
            id_cliente=linha["id_cliente"],
            data_venda=str(linha["data_venda"]),
            total=float(linha["total"]),
            forma_pagamento=linha["forma_pagamento"],
        )

    def atualizar(self, venda: Venda) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE vendas SET id_cliente = %s, data_venda = %s, total = %s, forma_pagamento = %s WHERE id_venda = %s",
            (venda.id_cliente, venda.data_venda, venda.total, venda.forma_pagamento, venda.id_venda),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_venda: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM vendas WHERE id_venda = %s",
            (id_venda,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados
