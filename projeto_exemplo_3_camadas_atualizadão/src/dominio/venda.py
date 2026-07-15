from dataclasses import dataclass
from typing import Optional


@dataclass
class Venda:
    id_venda: Optional[int]
    id_cliente: Optional[int]
    data_venda: str
    total: float
    forma_pagamento: str