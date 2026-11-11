from typing import Optional

from core.entities.produto import Produto
from core.interfaces.produto_repository_interface import ProdutoRepositoryInterface
from infra.db.database import Session
from infra.db.models import ProdutoModel


def _para_entidade(model: ProdutoModel) -> Produto:
    return Produto(
        id=model.id,
        nome=model.nome,
        quantidade=model.quantidade,
        valor=model.valor,
        data_insercao=model.data_insercao,
    )


def _para_model(produto: Produto) -> ProdutoModel:
    return ProdutoModel(
        nome=produto.nome,
        quantidade=produto.quantidade,
        valor=produto.valor,
    )


class ProdutoRepositorySQLAlchemy(ProdutoRepositoryInterface):
    def salvar(self, produto: Produto) -> Produto:
        with Session() as session:
            model = _para_model(produto)
            session.add(model)
            session.commit()
            return _para_entidade(model)

    def listar(self) -> list[Produto]:
        with Session() as session:
            models = session.query(ProdutoModel).all()
            return [_para_entidade(model) for model in models]

    def buscar_por_nome(self, nome: str) -> Optional[Produto]:
        with Session() as session:
            model = (
                session.query(ProdutoModel)
                .filter_by(nome=nome)
                .first()
            )
            if model is None:
                return None
            return _para_entidade(model)

    def remover_por_nome(self, nome: str) -> bool:
        with Session() as session:
            quantidade_removida = (
                session.query(ProdutoModel)
                .filter_by(nome=nome)
                .delete()
            )
            session.commit()
            return quantidade_removida > 0
