from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Produto:
    nome: str
    quantidade: int
    valor: float
    id: Optional[int] = None
    data_insercao: Optional[datetime] = None
