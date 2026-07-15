from dataclasses import dataclass
from typing import Optional


@dataclass
class Itens_venda:
    id_item: Optional[int]
    id_venda: int
    id_produto: int
    quantidade: int
    preco_unit: float