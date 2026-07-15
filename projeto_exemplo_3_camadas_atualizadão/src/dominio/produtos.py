from dataclasses import dataclass
from typing import Optional


@dataclass
class Produtos:
    """Representa a entidade de dominio Produto."""

    id: Optional[int]
    nome: str
    preco: float
    estoque: int
    categoria: str
    
