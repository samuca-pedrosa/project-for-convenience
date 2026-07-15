from __future__ import annotations

import mysql.connector


class ConexaoFactory:
    """
    Factory responsavel por criar conexoes.

    Neste exemplo, deixamos a criacao concentrada em um unico lugar.
    Se no futuro a aplicacao trocar de MySQL para outro banco,
    a mudanca comeca por aqui.
    """

    @staticmethod
    def criar_conexao(tipo_banco: str = "mysql", **configuracao) -> mysql.connector.MySQLConnection:
        if tipo_banco != "mysql":
            raise ValueError(f"Tipo de banco nao suportado: {tipo_banco}")

        conexao = mysql.connector.connect(
            host=configuracao.get("host", "127.0.0.1"),
            port=int(configuracao.get("porta", 3306)),
            user=configuracao.get("usuario", "root"),
            password=configuracao.get("senha", ""),
            database=configuracao.get("banco", "aplicacao"),
        )
        return conexao
