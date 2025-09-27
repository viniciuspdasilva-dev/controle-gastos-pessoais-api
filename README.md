# 📊 Controle de Gastos Pessoais - API

API RESTful construída em **Flask + SQLAlchemy + Pydantic** para gerenciar despesas pessoais, com suporte a categorias,
relatórios e integração com frontend.

---

## 🚀 Funcionalidades

- Cadastro e listagem de **gastos pessoais**
- Criação e consulta de **categorias**
- Relatórios de gastos por categoria ou total geral em intervalos de tempo
- Validações e documentação automática com **OpenAPI (Swagger/Redoc/RapiDoc)**

---

## 📂 Estrutura de Arquivos

```
├── app.py                # Arquivo principal com definição das rotas
├── database/
│   └── db.sqlite3         # Banco de dados SQLite, usado como exemplo
├── models/
│   └── tables.py         # Modelos do banco de dados (SQLAlchemy)
│   └── base.py           # Arquivo base para modelos (SQLAlchemy)
├── schemas/
│   ├── categoria.py      # Schemas Pydantic para Categoria
│   ├── gastos.py         # Schemas Pydantic para Gastos
│   ├── relatorios.py     # Schemas para relatórios
│   └── error.py          # Schema de erro padrão
├── requirements.txt      # Modulos do python necessarios para execução do projeto
```

---

## ⚙️ Como rodar o projeto

1. Clone o repositório:

```bash
  git clone https://github.com/viniciuspdasilva-dev/controle-gastos-pessoais-api.git
  cd controle-gastos-api
```

2. Crie e ative um ambiente virtual:

```bash
  python -m venv venv
  source venv/bin/activate   # Linux/Mac
  venv\Scripts\activate      # Windows
```

3. Instale as dependências:

```bash
  pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
  flask run
```

5. Acesse a documentação interativa:

- Swagger: [http://localhost:5000/openapi/swagger](http://localhost:5000/openapi/swagger)
- Redoc: [http://localhost:5000/openapi/redoc](http://localhost:5000/openapi/redoc)

---

## 🗄️ Modelos de Dados

### 📌 Categoria (`Categoria`)

Definida em `tables.py`

| Campo  | Tipo       | Obrigatório | Descrição           |
|--------|------------|-------------|---------------------|
| `id`   | Integer    | Sim         | Identificador único |
| `name` | String(50) | Sim, único  | Nome da categoria   |

---

### 📌 Gastos (`Gastos`)

Definida em `tables.py`

| Campo          | Tipo                    | Obrigatório | Descrição            |
|----------------|-------------------------|-------------|----------------------|
| `id`           | Integer                 | Sim         | Identificador único  |
| `descricao`    | String(120)             | Sim         | Descrição do gasto   |
| `valor`        | Float                   | Sim         | Valor do gasto       |
| `data`         | DateTime                | Sim         | Data do gasto        |
| `categoria_id` | Integer (FK)            | Sim         | Categoria vinculada  |
| `tag`          | Many-to-Many com `Tags` | Não         | Etiquetas adicionais |

---

### 📌 Tags (`Tags`)

Definida em `tables.py`

| Campo   | Tipo       | Obrigatório | Descrição     |
|---------|------------|-------------|---------------|
| `id`    | Integer    | Sim         | Identificador |
| `name`  | String(50) | Sim         | Nome da tag   |
| `color` | String(10) | Sim         | Cor associada |

---

## 📑 Schemas (Validação e Respostas)

- **`CategoriaSchema`**: Define o corpo para criação de categoria (`name: str`)
- **`ListaCategoriaSchema`**: Retorna lista de categorias
- **`GastosPessoaisSchema`**: Define criação de gasto (`descricao`, `valor`, `data`, `categoria_id`)
- **`GastosBuscaSchema`**: Busca gasto por `id`
- **`RelatorioQuerySchema`**: Recebe `initial_date` e `final_date` para relatórios
- **`RelatorioTotalSchema`**: Retorna somatório dos gastos no período
- **`TotalizadorGastosPerCategoriaSchema`**: Retorna gastos agrupados por categoria
- **`ErrorSchema`**: Padrão para erros (`message: str`)

---

## 🔗 Rotas da API

### 🏠 Home

- `GET /` → Redireciona para documentação Swagger.

---

### 📌 Gastos

- `POST /gastos` → Cadastra novo gasto.
    - Body: `GastosPessoaisSchema`
- `GET /gastos` → Lista todos os gastos.
- `GET /gasto/buscar/{id}` → Busca gasto pelo `id`.

---

### 📂 Categorias

- `GET /categorias` → Lista todas as categorias.
- `GET /categoria?name=...` → Busca categoria pelo nome.
- `POST /categorias` → Cria uma nova categoria.

---

### 📊 Relatórios

- `GET /relatorios/gastos_per_categoria?initial_date=dd/mm/yyyy&final_date=dd/mm/yyyy`  
  → Total por categoria no intervalo informado.
- `GET /relatorios/total_geral?initial_date=dd/mm/yyyy&final_date=dd/mm/yyyy`  
  → Somatório de todos os gastos no período.

---

## 📌 Tecnologias Utilizadas

- **Flask** (com `flask-openapi3` para documentação)
- **SQLAlchemy** (ORM para modelos e tabelas)
- **Pydantic** (validação de entrada e saída)
- **Flask-CORS** (para integração com frontend)