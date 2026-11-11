# Clean Architecture na API de Produtos

## Estrutura de pastas

```text
server/
├── app.py                          # ponto de entrada: cria o Flask, CORS e conecta as camadas
├── requirements.txt
│
├── core/                           # regras de negócio, sem Flask nem SQLAlchemy
│   ├── entities/
│   │   └── produto.py              # Produto como classe Python pura (dataclass)
│   ├── interfaces/
│   │   └── produto_repository_interface.py   # contrato (ABC) que o banco precisa cumprir
│   └── usecases/
│       ├── erros.py                # ProdutoJaExiste, ProdutoNaoEncontrado
│       ├── adicionar_produto.py
│       ├── listar_produtos.py
│       ├── buscar_produto.py
│       └── remover_produto.py
│
├── infra/                          # detalhes técnicos de persistência
│   ├── db/
│   │   ├── database.py             # engine, Session, criação do banco (antigo model/__init__.py)
│   │   └── models.py               # ProdutoModel do SQLAlchemy (antigo model/produto.py + base.py)
│   └── gateways/
│       └── produto_repository_sqlalchemy.py   # implementa a interface usando o SQLAlchemy
│
└── api/                            # entrada e saída HTTP
    ├── controllers/                # caminho de IDA: requisição → use case
    │   ├── produto_controller.py   # rotas: validam a entrada, chamam o use case, chamam o presenter
    │   └── produto_schemas.py      # schemas de entrada: ProdutoSchema, ProdutoBuscaSchema
    └── presenters/                 # caminho de VOLTA: entidade → resposta
        ├── produto_presenter.py    # apresenta_produto(s) + ProdutoViewSchema, ListagemProdutosSchema, ProdutoDelSchema
        └── error_presenter.py      # ErrorSchema
```

### Correspondência com o diagrama

| Camada do diagrama | Cor | Diretório |
|---|---|---|
| Entities | amarelo | `core/entities` |
| Use Cases | vermelho | `core/usecases` + `core/interfaces` |
| Controllers, Presenters | verde | `api/controllers`, `api/presenters` |
| Gateways | verde | `infra/gateways` |
| DB | azul | `infra/db` (SQLAlchemy + SQLite) |
| Web | azul | Flask / flask-openapi3, configurado no `app.py` |
| UI | azul | o projeto `front/` (fora da API) |
| Devices, External Interfaces | azul | não se aplicam neste projeto |

## Diagrama de dependências

As setas indicam **quem importa quem**. Todas apontam para dentro, em direção ao `core`, e o `core` não importa nada de `api` nem de `infra`.

```mermaid
flowchart TB
    UI["front/ (UI)<br/>index.html + scripts.js"]

    subgraph API["api/"]
        CTRL["controllers<br/>rotas + schemas de entrada"]
        PRES["presenters<br/>apresenta_produto(s) + schemas de saída"]
    end

    subgraph CORE["core/"]
        UC["usecases<br/>adicionar / listar / buscar / remover"]
        IF["interfaces<br/>ProdutoRepositoryInterface (ABC)"]
        ENT["entities<br/>Produto"]
    end

    subgraph INFRA["infra/"]
        GW["gateways<br/>ProdutoRepositorySQLAlchemy"]
        DB["db<br/>database.py / models.py"]
    end

    APP["app.py<br/>(Flask + CORS + montagem)"]
    SQLITE[("SQLite<br/>database/db.sqlite3")]

    UI -- "HTTP / JSON" --> CTRL
    CTRL --> UC
    CTRL --> PRES
    PRES --> ENT
    UC --> IF
    UC --> ENT
    IF --> ENT
    GW -. "implementa" .-> IF
    GW --> ENT
    GW --> DB
    DB --> SQLITE
    APP --> CTRL
    APP --> GW

    classDef entities fill:#fbf6b6,stroke:#333,color:#000
    classDef usecases fill:#f6a5a5,stroke:#333,color:#000
    classDef adapters fill:#a7f3b5,stroke:#333,color:#000
    classDef frameworks fill:#a6d8f7,stroke:#333,color:#000

    class ENT entities
    class UC,IF usecases
    class CTRL,PRES,GW adapters
    class DB,SQLITE,UI,APP frameworks
```

O `app.py` é o único arquivo que conhece todas as camadas. Ele cria o repositório concreto (`infra`) e o entrega aos casos de uso (`core`) usados pelos controllers (`api`). Isso é a **injeção de dependência**: o caso de uso recebe "algo que cumpre a interface `ProdutoRepositoryInterface`", sem saber que por trás existe SQLAlchemy.

## Fluxo de uma requisição: `POST /produto`

```mermaid
sequenceDiagram
    participant F as front (UI)
    participant C as Controller<br/>api/controllers
    participant U as AdicionarProduto<br/>core/usecases
    participant R as ProdutoRepositorySQLAlchemy<br/>infra/gateways
    participant P as Presenter<br/>api/presenters

    F->>C: POST /produto {nome, quantidade, valor}
    C->>U: executar(nome, quantidade, valor)
    U->>R: buscar_por_nome(nome)
    R-->>U: None
    U->>R: salvar(Produto)
    R-->>U: Produto (com id)
    U-->>C: Produto
    C->>P: apresenta_produto(produto)
    P-->>C: ProdutoViewSchema
    C-->>F: 200 + JSON
```

Se o nome já existir, o caso de uso lança `ProdutoJaExiste` e o controller converte esse erro em `409`. Assim, o `core` não conhece códigos HTTP.

## Schemas: entrada com o controller, saída com o presenter

Os schemas Pydantic só descrevem a **forma** dos dados. Por isso não ganham uma pasta própria; cada um fica com quem o usa:

- **Schemas de entrada** (`ProdutoSchema`, `ProdutoBuscaSchema`) validam o que chega na requisição. Fazem parte do caminho de ida e ficam em `controllers/`.
- **Schemas de saída** (`ProdutoViewSchema`, `ListagemProdutosSchema`, `ProdutoDelSchema`, `ErrorSchema`) são o *View Model* da Clean Architecture: o formato que o presenter produz. Ficam em `presenters/`.

### Onde Schemas e Presenters aparecem

```text
requisição ──► ProdutoSchema ──► use case ──► Produto (entidade) ──► presenter ──► ProdutoViewSchema ──► resposta
               (controller)                   (core)                              (presenter)
```

- **`ProdutoSchema`** é o que **chega** na requisição. Quem recebe é a rota, que tira os dados dele e entrega ao use case.
- **`Produto`** é o que o use case **devolve**. Esse `Produto` é a entidade do `core`, não o modelo do SQLAlchemy.
- **`ProdutoViewSchema`** é o que **sai** na resposta. Quem monta é o presenter, a partir da entidade.

O presenter monta e devolve o próprio schema de saída, em vez de um `dict` solto, e o formato da resposta fica garantido:

```python
def apresenta_produto(produto: Produto) -> ProdutoViewSchema:
    return ProdutoViewSchema(id=produto.id, nome=produto.nome,
                             quantidade=produto.quantidade, valor=produto.valor)
```
