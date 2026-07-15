from dataclasses import dataclass
from typing import Optional


@dataclass
class Clientes:
    id: Optional[int]
    nome: str
    cpf: str
    telefone: str
    email: str
    data_cadastro: str
    