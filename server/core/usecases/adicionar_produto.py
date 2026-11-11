from core.entities.produto import Produto
from core.interfaces.produto_repository_interface import ProdutoRepositoryInterface
from core.usecases.erros import ProdutoJaExiste


class AdicionarProduto:
    def __init__(self, repositorio: ProdutoRepositoryInterface) -> None:
        self.repositorio = repositorio

    def executar(self, nome: str, quantidade: int, valor: float) -> Produto:
        if self.repositorio.buscar_por_nome(nome) is not None:
            raise ProdutoJaExiste(nome)

        produto = Produto(nome=nome, quantidade=quantidade, valor=valor)
        return self.repositorio.salvar(produto)
