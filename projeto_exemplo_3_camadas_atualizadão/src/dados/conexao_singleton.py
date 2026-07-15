from typing import Optional

import mysql.connector

from src.dados.conexao_factory import ConexaoFactory


class ConexaoSingleton:
    """
    Singleton responsavel por manter uma unica conexao ativa.

    A primeira chamada cria a conexao usando a Factory.
    As proximas chamadas reaproveitam a mesma conexao.
    """

    _conexao: Optional[mysql.connector.MySQLConnection] = None

    @classmethod
    def obter_conexao(cls, tipo_banco: str = "mysql", **configuracao) -> mysql.connector.MySQLConnection:
        if cls._conexao is None:
            cls._conexao = ConexaoFactory.criar_conexao(
                tipo_banco=tipo_banco,
                **configuracao,
            )
        return cls._conexao

    @classmethod
    def fechar_conexao(cls) -> None:
        if cls._conexao is not None:
            cls._conexao.close()
            cls._conexao = None
