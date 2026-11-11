from pydantic import BaseModel


class ProdutoSchema(BaseModel):
    nome: str = "Banana Prata"
    quantidade: int = 12
    valor: float = 12.50


class ProdutoBuscaSchema(BaseModel):
    nome: str = "Banana Prata"
