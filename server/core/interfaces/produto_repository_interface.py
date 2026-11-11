from abc import ABC, abstractmethod
from typing import Optional

from core.entities.produto import Produto


class ProdutoRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        pass

    @abstractmethod
    def listar(self) -> list[Produto]:
        pass

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> Optional[Produto]:
        pass

    @abstractmethod
    def remover_por_nome(self, nome: str) -> bool:
        pass
