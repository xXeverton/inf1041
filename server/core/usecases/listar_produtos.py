from core.entities.produto import Produto
from core.interfaces.produto_repository_interface import ProdutoRepositoryInterface


class ListarProdutos:
    def __init__(self, repositorio: ProdutoRepositoryInterface) -> None:
        self.repositorio = repositorio

    def executar(self) -> list[Produto]:
        return self.repositorio.listar()
