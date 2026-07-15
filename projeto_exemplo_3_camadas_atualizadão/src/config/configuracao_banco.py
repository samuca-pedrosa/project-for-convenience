import os


def obter_configuracao_banco() -> dict:
    """
    Le a configuracao de conexao do banco a partir de variaveis de ambiente,
    com valores padrao iguais aos do docker-compose.yml do projeto.

    Variaveis aceitas:
    - DB_HOST
    - DB_PORT
    - DB_USER
    - DB_PASSWORD
    - DB_NAME
    """
    return {
        "tipo_banco": "mysql",
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "porta": int(os.environ.get("DB_PORT", "3306")),
        "usuario": os.environ.get("DB_USER", "root"),
        "senha": os.environ.get("DB_PASSWORD", "Hjklmno123"),
        "banco": os.environ.get("DB_NAME", "aplicacao"),
    }
