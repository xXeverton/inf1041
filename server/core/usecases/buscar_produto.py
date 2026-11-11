from core.entities.produto import Produto
from core.interfaces.produto_repository_interface import ProdutoRepositoryInterface
from core.usecases.erros import ProdutoNaoEncontrado


class BuscarProduto:
    def __init__(self, repositorio: ProdutoRepositoryInterface) -> None:
        self.repositorio = repositorio

    def executar(self, nome: str) -> Produto:
        produto = self.repositorio.buscar_por_nome(nome)
        if produto is None:
            raise ProdutoNaoEncontrado(nome)
        return produto
