from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag

from api.controllers.produto_controller import registrar_rotas_produto
from core.usecases.adicionar_produto import AdicionarProduto
from core.usecases.buscar_produto import BuscarProduto
from core.usecases.listar_produtos import ListarProdutos
from core.usecases.remover_produto import RemoverProduto
from infra.db.database import criar_banco
from infra.gateways.produto_repository_sqlalchemy import ProdutoRepositorySQLAlchemy


app = OpenAPI(__name__, info=Info(title="Minha API", version="1.0.0"))
CORS(app)

criar_banco()

repositorio = ProdutoRepositorySQLAlchemy()
adicionar = AdicionarProduto(repositorio)
listar = ListarProdutos(repositorio)
buscar = BuscarProduto(repositorio)
remover = RemoverProduto(repositorio)

registrar_rotas_produto(app, adicionar, listar, buscar, remover)

tag_documentacao = Tag(name="Documentação")


@app.get("/", tags=[tag_documentacao])
def documentacao():
    return redirect("/openapi")


if __name__ == "__main__":
    app.run(debug=True)
