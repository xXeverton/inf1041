from typing import List

from pydantic import BaseModel

from core.entities.produto import Produto


class ProdutoViewSchema(BaseModel):
    id: int
    nome: str
    quantidade: int
    valor: float


class ListagemProdutosSchema(BaseModel):
    produtos: List[ProdutoViewSchema]


class ProdutoDelSchema(BaseModel):
    message: str
    nome: str


def apresenta_produto(produto: Produto) -> ProdutoViewSchema:
    return ProdutoViewSchema(
        id=produto.id,
        nome=produto.nome,
        quantidade=produto.quantidade,
        valor=produto.valor,
    )


def apresenta_produtos(produtos: list[Produto]) -> ListagemProdutosSchema:
    return ListagemProdutosSchema(
        produtos=[apresenta_produto(produto) for produto in produtos]
    )


def apresenta_remocao(nome: str) -> ProdutoDelSchema:
    return ProdutoDelSchema(message="Produto removido", nome=nome)
