Estrutura que vamos utilizar baseado em ARQUITETURA.md:

1. core/entities
2. core/interfaces
3. core/usecases
4. infra/db
5. infra/gateways
6. api/presenters
7. api/controllers
8. app.py
9. client/scripts.js

Mas antes disso, criaremos a estrutura do diretório. Para evitar trabalho mecanico vamos pedir para o assistente criar a estrutura de diretórios utilizando o seguinte prompt:

```
Dentro da pasta server, crie apenas a estrutura de diretórios, sem escrever código:

- core/ com os subdiretórios entities/, interfaces/ e usecases/
- infra/ com os subdiretórios db/ e gateways/
- api/ com os subdiretórios controllers/ e presenters/

Coloque um arquivo __init__.py vazio em cada uma dessas pastas e subpastas
(não na própria server/).

Na raiz de server/, crie:
- app.py vazio
- requirements.txt com: flask, flask-openapi3[swagger], flask-cors,
  sqlalchemy, sqlalchemy-utils
```

## 1. core/entities

```
Em server/core/entities/, crie produto.py com a entidade Produto como uma
dataclass Python pura, sem importar Flask, SQLAlchemy ou Pydantic.

Campos:
- nome: str
- quantidade: int
- valor: float
- id: Optional[int] = None
- data_insercao: Optional[datetime] = None

Use o __init__ gerado pela dataclass; não escreva um manualmente.
Não crie nenhum outro arquivo.
```

## 2. core/interfaces

```
Em server/core/interfaces/, crie produto_repository_interface.py com a classe abstrata
ProdutoRepositoryInterface(ABC). Ela só pode importar a entidade de
core/entities/produto.py.

Métodos abstratos:
- salvar(produto: Produto) -> Produto      # devolve o produto com id
- listar() -> list[Produto]
- buscar_por_nome(nome: str) -> Optional[Produto]
- remover_por_nome(nome: str) -> bool      # True se removeu

Não implemente os métodos e não crie nenhum outro arquivo.
```

Um **repository** (repositório) é um objeto que guarda e recupera entidades **como se fosse uma coleção em memória**, escondendo de onde os dados realmente vêm. É um padrão de projeto descrito por Martin Fowler e popularizado pelo DDD (*Domain-Driven Design*).

Quem usa o repositório só vê operações como "salve este produto", "me dê todos" e "encontre pelo nome". Não vê SQL, sessão, commit, tabela ou arquivo.

### No projeto

O repositório tem duas partes, e cada uma fica numa camada:

| Parte | Onde | Papel |
|---|---|---|
| `ProdutoRepositoryInterface` | `core/interfaces` | **O contrato:** quais operações existem (`salvar`, `listar`, `buscar_por_nome`, `remover_por_nome`) |
| `ProdutoRepositorySQLAlchemy` | `infra/gateways` | **A implementação:** como essas operações são feitas usando o SQLAlchemy e o SQLite |

O caso de uso conhece só conhecerá o contrato:

```python
class AdicionarProduto:
    def __init__(self, repositorio: ProdutoRepositoryInterface):
        self.repositorio = repositorio

    def executar(self, nome, quantidade, valor):
        if self.repositorio.buscar_por_nome(nome):   # "procure na coleção"
            raise ProdutoJaExiste(nome)
        return self.repositorio.salvar(Produto(nome, quantidade, valor))
```

Esse código não sabe se os produtos estão num SQLite, num PostgreSQL, numa API externa ou numa lista Python.


## 3. core/usecases

```
Em server/core/usecases/, crie os casos de uso. Eles só podem importar de
core/ (entities e interfaces), nunca de infra/ ou api/.

- erros.py: duas exceções que herdam de Exception. Cada uma recebe o nome
  do produto no __init__ e repassa uma mensagem pronta para
  super().__init__():
  - ProdutoJaExiste(nome): "Produto '<nome>' já existe na base"
  - ProdutoNaoEncontrado(nome): "Produto '<nome>' não encontrado na base"
  As exceções não conhecem HTTP; quem decide o status code é o controller.
  
- adicionar_produto.py, listar_produtos.py, buscar_produto.py,
  remover_produto.py: uma classe por arquivo (AdicionarProduto,
  ListarProdutos, BuscarProduto, RemoverProduto). Cada classe recebe um
  ProdutoRepositoryInterface no __init__ e tem um único método executar().

Implemente cada executar() seguindo exatamente estes passos:

AdicionarProduto.executar(nome, quantidade, valor) -> Produto
  1. Busque um produto com esse nome no repositório (buscar_por_nome).
  2. Se encontrar, lance ProdutoJaExiste(nome).
  3. Crie a entidade Produto com nome, quantidade e valor.
  4. Salve no repositório (salvar) e retorne o produto devolvido por ele.

ListarProdutos.executar() -> list[Produto]
  1. Retorne a lista do repositório (listar). Se não houver produtos,
     retorne a lista vazia, sem lançar erro.

BuscarProduto.executar(nome) -> Produto
  1. Busque o produto no repositório (buscar_por_nome).
  2. Se não encontrar, lance ProdutoNaoEncontrado(nome).
  3. Retorne o produto encontrado.

RemoverProduto.executar(nome) -> None
  1. Peça ao repositório para remover pelo nome (remover_por_nome).
  2. Se ele retornar False, lance ProdutoNaoEncontrado(nome).

Não crie nenhum outro arquivo.
```

`Exception` é nativa do Python e faz parte dos **built-ins**, os nomes que ficam disponíveis em qualquer arquivo sem precisar de `import`. É o mesmo caso de `print`, `len`, `str`, `list`, `ValueError` e `KeyError`.

Por baixo, esses nomes moram no módulo `builtins`, que o Python carrega sozinho. Por isso as duas formas abaixo funcionam, mas a segunda nunca é necessária:

```python
class ProdutoJaExiste(Exception): ...

import builtins
class ProdutoJaExiste(builtins.Exception): ...
```

O `super().__init__(f"Produto '{nome}' já existe na base")` chama o construtor da `Exception`, que guarda a mensagem. 

## 4. infra/db

```
Em server/infra/db/, crie:

- models.py: Base (declarative_base) e ProdutoModel, tabela "produto", com as
  colunas id ("pk_produto", chave primária), nome (String(140), único),
  quantidade (Integer), valor (Float) e data_insercao (DateTime, com
  default=datetime.now, sem parênteses).

- database.py: importe Base de models.py e crie:
  - a engine do SQLite em database/db.sqlite3;
  - Session (sessionmaker ligado à engine);
  - uma função criar_banco() que cria a pasta database/ se não existir,
    cria o banco se não existir (database_exists / create_database do
    sqlalchemy_utils) e cria as tabelas (Base.metadata.create_all).

Não importe nada de core/ ou api/ e não crie nenhum outro arquivo.
```

Os dois arquivos cuidam do banco, mas respondem perguntas diferentes: o `models.py` diz **como os dados ficam guardados**, e o `database.py` diz **onde fica o banco e como conversar com ele**.

### `models.py`

Ele contém o **mapeamento objeto-relacional (ORM)**, ou seja, as classes Python que o SQLAlchemy traduz em tabelas:

- **`Base`** é a classe-mãe de todos os models. É ela que registra as tabelas para o SQLAlchemy saber quais criar.
- **`ProdutoModel`** é a tabela `produto`: nome das colunas, tipos, chave primária, `unique` e valor padrão.

Você mexe nesse arquivo quando **a estrutura dos dados muda**, por exemplo para criar uma coluna nova ou uma tabela nova.

### `database.py`

Ele configura o acesso ao banco:

- **`engine`** é a conexão com o banco de verdade e diz que banco é esse (`sqlite:///database/db.sqlite3`).
- **`Session`** é a fábrica de sessões. Cada `Session()` abre uma "conversa" com o banco, em que você faz `add`, consultas e `commit`.
- **`criar_banco()`** deixa tudo pronto na primeira execução: cria a pasta, o arquivo do banco e as tabelas descritas no `models.py`.

Você mexe nesse arquivo quando **o banco muda**, por exemplo ao trocar o SQLite por PostgreSQL. Só a URL da engine muda, e os models continuam iguais.

### Por que estão em `infra` e não em `core`

Os dois dependem do SQLAlchemy, e o SQLAlchemy é um **detalhe técnico fornecido por um framework externo**: ele fica no círculo azul, *Frameworks & Drivers*. Por isso o produto passa a existir duas vezes:

- **`Produto`**, em `core/entities`, é o que o produto **é** para o negócio: uma dataclass pura.
- **`ProdutoModel`**, em `infra/db`, é **como** o produto fica guardado no SQLite.

Quem converte de um para o outro é o gateway, no passo 5. Assim o `core` nunca precisa saber que existe banco.

## 5. infra/gateways

```
Em server/infra/gateways/, crie o arquivo produto_repository_sqlalchemy.py.

Nele, crie a classe ProdutoRepositorySQLAlchemy, que implementa
core/interfaces/produto_repository_interface.py usando Session e ProdutoModel de infra/db/. Os métodos sempre recebem e devolvem a entidade Produto, nunca o
ProdutoModel.

Funções privadas de conversão (fora da classe):
- _para_entidade(model) -> Produto: copia id, nome, quantidade, valor e
  data_insercao do model para a entidade.
- _para_model(produto) -> ProdutoModel: copia nome, quantidade e valor
  (sem id, que é gerado pelo banco).

Cada método abre a sessão com "with Session() as session:" e segue estes passos:

salvar(produto) -> Produto
  1. Converta a entidade em ProdutoModel (_para_model).
  2. Adicione o model na sessão e faça commit.
  3. Ainda dentro do with, converta o model de volta (_para_entidade) e
     retorne. Assim a entidade volta com o id gerado.

listar() -> list[Produto]
  1. Busque todos os ProdutoModel.
  2. Retorne a lista convertida com _para_entidade.

buscar_por_nome(nome) -> Optional[Produto]
  1. Busque o primeiro ProdutoModel com esse nome.
  2. Se não encontrar, retorne None.
  3. Se encontrar, retorne convertido com _para_entidade.

remover_por_nome(nome) -> bool
  1. Remova os ProdutoModel com esse nome (query + delete) e guarde a
     quantidade removida.
  2. Faça commit.
  3. Retorne True se removeu algum, False caso contrário.

Não crie nenhum outro arquivo.
```

### Repository e Gateway

No diagrama da Clean Architecture, o círculo verde se chama **Gateways**: tudo o que faz a ponte entre os casos de uso e algo externo. O repository é **um tipo de gateway**, especializado em persistir entidades. Por isso o arquivo fica em `infra/gateways/`, mas a classe se chama `...Repository...`.

### Para que serve, na prática

**1. Trocar o banco sem mexer nas regras.** Para usar PostgreSQL, basta outra implementação da interface. Os casos de uso não mudam.

**2. Testar sem banco.** Dá para criar um repositório falso em memória:

```python
class ProdutoRepositoryEmMemoria(ProdutoRepositoryInterface):
    def __init__(self):
        self.produtos = {}

    def salvar(self, produto):
        produto.id = len(self.produtos) + 1
        self.produtos[produto.nome] = produto
        return produto

    def listar(self):
        return list(self.produtos.values())

    def buscar_por_nome(self, nome):
        return self.produtos.get(nome)

    def remover_por_nome(self, nome):
        return self.produtos.pop(nome, None) is not None
```

Com ele, o `AdicionarProduto` pode ser testado em milissegundos, sem criar banco nem tabelas.

## 6. api/presenters

```
Em server/api/presenters/, crie os presenters. Eles podem importar pydantic e
core/entities, nunca infra/.

error_presenter.py
- ErrorSchema (BaseModel): message: str
- apresenta_erro(mensagem: str) -> ErrorSchema
  Retorna ErrorSchema com message=mensagem.

produto_presenter.py
- Schemas de saída (BaseModel):
  - ProdutoViewSchema: id: int, nome: str, quantidade: int, valor: float
  - ListagemProdutosSchema: produtos: List[ProdutoViewSchema]
  - ProdutoDelSchema: message: str, nome: str
- apresenta_produto(produto: Produto) -> ProdutoViewSchema
  Copia id, nome, quantidade e valor da entidade para o schema.
  (data_insercao não é exposta na resposta.)
- apresenta_produtos(produtos: list[Produto]) -> ListagemProdutosSchema
  Aplica apresenta_produto em cada produto e coloca o resultado em
  produtos. Lista vazia gera {"produtos": []}.
- apresenta_remocao(nome: str) -> ProdutoDelSchema
  Retorna message="Produto removido" e o nome recebido.

Não crie nenhum outro arquivo.
```

## 7. api/controllers

```
Em server/api/controllers/, crie:

- produto_schemas.py: schemas Pydantic de entrada
  - ProdutoSchema: nome: str = "Banana Prata", quantidade: int = 12,
    valor: float = 12.50
  - ProdutoBuscaSchema: nome: str = "Banana Prata"

- produto_controller.py: uma função registrar_rotas_produto(app, adicionar, listar, buscar, remover) que recebe o app e os quatro casos de uso, cria a Tag "Produto" e define as rotas abaixo diretamente no app recebido (@app.post, @app.get, @app.delete), dentro da própria função. A função não retorna nada. Não use Blueprint nem APIBlueprint.

Todas as respostas são o schema devolvido pelo presenter com .model_dump().
Os erros são capturados com try/except e respondidos com
apresenta_erro(str(e)).model_dump(). Documente no parâmetro responses os
schemas de saída de cada status.

POST /produto (body: ProdutoSchema)
  responses: 200 ProdutoViewSchema, 409 ErrorSchema
  1. Chame adicionar.executar com nome, quantidade e valor do body.
  2. Se lançar ProdutoJaExiste, retorne o erro com 409.
  3. Retorne apresenta_produto(produto) com 200.

GET /produtos
  responses: 200 ListagemProdutosSchema
  1. Chame listar.executar().
  2. Retorne apresenta_produtos(produtos) com 200.

GET /produto (query: ProdutoBuscaSchema)
  responses: 200 ProdutoViewSchema, 404 ErrorSchema
  1. Chame buscar.executar com o nome da query.
  2. Se lançar ProdutoNaoEncontrado, retorne o erro com 404.
  3. Retorne apresenta_produto(produto) com 200.

DELETE /produto (query: ProdutoBuscaSchema)
  responses: 200 ProdutoDelSchema, 404 ErrorSchema
  1. Chame remover.executar com o nome da query.
  2. Se lançar ProdutoNaoEncontrado, retorne o erro com 404.
  3. Retorne apresenta_remocao(nome) com 200.

O controller não importa nada de infra/, não instancia repositórios nem
casos de uso e não cria o app.

Siga exatamente o que está descrito acima, sem acrescentar rotas, classes,
padrões ou bibliotecas não pedidos. Não crie nenhum outro arquivo.
```

## 8. app.py

```
Em server/app.py, monte a aplicação nesta ordem:

1. Crie o app OpenAPI (flask-openapi3) com
   Info(title="Minha API", version="1.0.0") e habilite CORS(app).
2. Chame criar_banco().
3. Crie um único ProdutoRepositorySQLAlchemy.
4. Crie os quatro casos de uso, passando esse mesmo repositório para cada um.
5. Chame registrar_rotas_produto(app, adicionar, listar, buscar, remover).
6. Crie a rota GET / (tag "Documentação") que redireciona para /openapi.
7. No final: if __name__ == "__main__": app.run(debug=True).

O app.py é o único arquivo que importa de core/, infra/ e api/ ao mesmo tempo.

Não crie nenhum outro arquivo ou mexa em outro já existente.
```

Depois, rode a API e teste nesta sequência:
1. POST /produto {"nome": "Banana", "quantidade": 2, "valor": 3.5} -> 200
2. O mesmo POST de novo -> 409
3. GET /produtos -> 200, lista com Banana
4. GET /produto?nome=Banana -> 200
5. DELETE /produto?nome=Banana -> 200
6. O mesmo DELETE de novo -> 404


## 9. client/scripts.js

```
Em client/, crie scripts.js, que faz a comunicação do front com a API.
Não altere index.html nem styles.css.

O index.html já usa:
- inputs com ids newInput (nome), newQuantity (quantidade) e newPrice (valor);
- o botão Adicionar com onclick="newItem()";
- a tabela com id myTable (colunas Nome, Quantidade, Valor e o botão de remover).

Contrato da API:
- GET    /produtos           -> 200 {"produtos": [{id, nome, quantidade, valor}]}
- POST   /produto (JSON)     -> 200 {id, nome, quantidade, valor} ou 409 {"message"}
- DELETE /produto?nome=...   -> 200 {"message", "nome"} ou 404 {"message"}

Use fetch com async/await. Crie no topo uma constante
API_URL = "http://127.0.0.1:5000" e monte todas as URLs a partir dela.

Funções:

getList()
  1. Faça GET em /produtos.
  2. Para cada produto da resposta, chame insertList(nome, quantidade, valor).
  3. Chame getList() uma vez ao carregar o arquivo.

postItem(nome, quantidade, valor) -> objeto da resposta
  1. Faça POST em /produto com header Content-Type: application/json e
     body JSON.stringify({ nome, quantidade: Number(quantidade),
     valor: Number(valor) }).
  2. Se a resposta não for ok (response.ok), lance um Error com o
     message do JSON.
  3. Retorne o JSON da resposta.

deleteItem(nome)
  1. Faça DELETE em /produto?nome=<nome>, usando encodeURIComponent(nome).
  2. Se a resposta não for ok, lance um Error com o message do JSON.

newItem()
  1. Leia os três inputs.
  2. Se o nome estiver vazio, alert("Escreva o nome de um item!") e pare.
  3. Se quantidade ou valor estiverem vazios ou não forem números,
     alert("Quantidade e valor precisam ser números!") e pare.
  4. Chame postItem. Só depois que a API responder com sucesso, chame
     insertList com os dados devolvidos pela API, limpe os inputs e
     alert("Item adicionado!").
  5. Se der erro, alert com a mensagem do erro (ex.: produto já existe).

insertList(nome, quantidade, valor)
  1. Insira uma linha em myTable com nome, quantidade e valor
     (use textContent, nunca innerHTML).
  2. Na última célula, crie um span com classe "close" e texto "×".
  3. No clique desse span: confirm("Você tem certeza?"); se confirmado,
     chame deleteItem(nome). Só depois do sucesso, remova a linha e
     alert("Removido!"). Se der erro, alert com a mensagem do erro.

Comentários de uma linha no formato "// Função para ..." acima de cada
função. Siga exatamente o que está descrito acima, sem bibliotecas nem
funções extras. Não crie nenhum outro arquivo.
```

Depois, com a API rodando, abra client/index.html no navegador e teste:
1. Adicionar "Banana" -> aparece na tabela.
2. Adicionar "Banana" de novo -> alerta de produto já existente, a tabela não muda.
3. Recarregar a página -> Banana continua na tabela (veio do banco).
4. Remover Banana -> some da tabela; recarregando, continua sem ela.
