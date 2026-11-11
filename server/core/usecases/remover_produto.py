from core.interfaces.produto_repository_interface import ProdutoRepositoryInterface
from core.usecases.erros import ProdutoNaoEncontrado


class RemoverProduto:
    def __init__(self, repositorio: ProdutoRepositoryInterface) -> None:
        self.repositorio = repositorio

    def executar(self, nome: str) -> None:
        if not self.repositorio.remover_por_nome(nome):
            raise ProdutoNaoEncontrado(nome)
