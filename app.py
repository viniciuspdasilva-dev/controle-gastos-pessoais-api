from getopt import error

from flask_openapi3 import OpenAPI, Info, Tag, Contact
from flask import redirect
from sqlalchemy import func, desc, cast, DateTime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.coercions import expect

from models import Session
from models.tables import Categoria, Gastos, Tags

from flask_cors import CORS

from schemas.Relatorios import construir_relatorio_gastos_per_categoria, CategoriaTotal, \
    TotalizadorGastosPerCategoriaSchema, RelatorioTotalSchema, construir_relatorio_total_geral, RelatorioQuerySchema
from schemas.categoria import CategoriaSchema, definir_categorias, ListaCategoriaSchema, definir_categoria, \
    SearchCategoriaSchema, CategoriaViewSchema
from schemas.error import ErrorSchema
from schemas.gastos import GastosViewSchema, GastosPessoaisSchema, apresenta_gasto, GastosBuscaSchema, apresenta_gastos

contact = Contact(
    name="Vinicius Pereira da Silva",
    email="viniciuspdasilva.dev@gmail.com",
    url="https://github.com/viniciuspdasilva-dev/controle-gastos-pessoais-api"
)
info = Info(
    title="Gastos Pessoais API",
    version="1.0.0",
    contact=contact,
    description="API simples, construida em FlaskAPI, python3"
)
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
gastos_tag = Tag(name="Gastos Pessoais", description="Adição, visualização e remoção de gastos pessoais à base")
categoria_tag = Tag(name="Categorias", description="Adição de categorias de um gasto cadastrado na base")
relatorios_tag = Tag(name="Relatorios Gerais", description="Categoria relacionada a relatorios gerais")


@app.get("/", tags=[home_tag], description="Pagina inicial do OpenAPI")
def home():
    return redirect("/openapi/swagger")


# Rotas - Gastos
@app.post("/gasto/cadastrar",
          tags=[gastos_tag],
          description="Rota principal para inserir um novo gasto pessoal",
          responses={"200": GastosViewSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
          )
def gasto_cadastrar(form: GastosPessoaisSchema):
    gasto = Gastos(
        descricao=form.descricao,
        data=form.data,
        valor=form.valor,
        categoria_id=form.categoria_id
    )
    try:
        session = Session()
        session.add(gasto)
        session.commit()
        return apresenta_gasto(gasto), 200
    except IntegrityError as e:
        error_msg = "Gasto já cadastrado no sistema" + str(e)
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/" + str(e)
        return {"message": error_msg}, 400


@app.get("/gastos",
         tags=[gastos_tag],
         description="Rota que lista todos os gastos cadastrados",
         responses={"200": GastosViewSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
         )
def buscar_gastos():
    session = Session()
    try:
        gastos = session.query(Gastos).all()
        return apresenta_gastos(gastos), 200
    except Exception as e:
        return {"message": f"Ocorreu um erro durante a consulta: {e}"}


@app.get("/gasto/buscar/{id}",
         tags=[gastos_tag],
         description="Rota que lista um gasto especifico por id informado",
         responses={"200": GastosViewSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
         )
def buscar_gasto(query: GastosBuscaSchema):
    id_gasto = query.id
    if id_gasto is None or id_gasto == 0:
        return {"message": "Não foi possivel realizar a consulta, pois o id não foi enviado corretamente"}, 400
    session = Session()
    gasto = session.query(Gastos).filter(Gastos.id == id_gasto).first()
    if gasto is None:
        return {"message": f"Nenhum gasto encontrado com o id: {id_gasto}"}, 404
    else:
        return apresenta_gasto(gasto), 200


# Rotas - Consultas gerais

@app.get("/relatorios/gastos_per_categoria",
         tags=[relatorios_tag],
         description="Totalizador de gastos per categoria, dentro de um intervalo de datas",
         responses={"200": TotalizadorGastosPerCategoriaSchema, "409": ErrorSchema, "400": ErrorSchema,
                    "500": ErrorSchema}
         )
def totalizar_gastos_categorias(query: RelatorioQuerySchema):
    initial_date = query.initial_date
    final_date = query.final_date
    session = Session()
    try:
        result = (
            session.query(Categoria.name.label("Categoria"), func.coalesce(func.sum(Gastos.valor), 0).label("total"))
            .join(Gastos, Categoria.id == Gastos.categoria_id)
            .where(cast(Gastos.data, DateTime) >= initial_date)
            .where(cast(Gastos.data, DateTime) <= final_date)
            .group_by(Categoria.name)
            .order_by(desc(func.sum(Gastos.valor)))
            .all()
        )
        return construir_relatorio_gastos_per_categoria(
            [CategoriaTotal(categoria=r[0], total=r[1]) for r in result]
        ), 200
    except Exception as e:
        error_msg = "Ocorreu um erro ao realizar a consulta: " + str(e)
        return {"message": error_msg}, 400


@app.get("/relatorios/total_geral",
         tags=[relatorios_tag],
         description="Retorna o somatorio de todos os gastos dentro de um intervalo de tempo",
         responses={"200": RelatorioTotalSchema, "409": ErrorSchema, "400": ErrorSchema,
                    "500": ErrorSchema}
         )
def consultar_valor_total(query: RelatorioQuerySchema):
    initial_date = query.initial_date
    final_date = query.final_date
    try:
        session = Session()
        total = (
            session.query(func.coalesce(func.sum(Gastos.valor), 0).label("total"))
            .where(cast(Gastos.data, DateTime) >= initial_date)
            .where(cast(Gastos.data, DateTime) <= final_date)
            .scalar()
        )
        return construir_relatorio_total_geral(total), 200
    except Exception as e:
        error_msg = "Ocorreu um erro ao realizar a consulta: " + str(e)
        return {"message": error_msg}, 400


# Rotas - Categorias
@app.get("/categorias",
         tags=[categoria_tag],
         description="Rota que lista as categorias de gastos salvas",
         responses={"200": ListaCategoriaSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
         )
def consultar_categorias_salvas():
    try:
        session = Session()
        categorias = session.query(Categoria).all()
        return definir_categorias(categorias)
    except Exception as e:
        msg_erro = "Ocorreu um erro: " + str(e)
        return {"message": msg_erro}, 400


@app.get("/categoria",
         tags=[categoria_tag],
         description="Rota que returna uma categoria pelo nome salvo",
         responses={"200": CategoriaViewSchema, "409": ErrorSchema, "400": ErrorSchema, "404": ErrorSchema,
                    "500": ErrorSchema}
         )
def consultar_categoria(params: SearchCategoriaSchema):
    categoria_name = params.name
    if not categoria_name:
        return {"message": "Nenhum criterio de pesquisa foi mandado"}, 400
    session = Session()
    categoria = session.query(Categoria).filter_by(name=categoria_name).first()

    if not categoria:
        return {"message": "Nenhum categoria foi mandado"}, 404
    else:
        return definir_categoria(categoria)


@app.post("/categorias",
          tags=[categoria_tag],
          description="Rota que cria uma nova categoria de gasto",
          responses={"200": CategoriaSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema})
def cadastrar_categoria(form: CategoriaSchema):
    categoria = Categoria(
        name=form.name
    )
    try:
        session = Session()
        session.add(categoria)
        session.commit()
        return definir_categoria(categoria), 200

    except IntegrityError as e:
        error_msg = "Gasto já cadastrado no sistema" + str(e)
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/ - " + str(e)
        return {"message": error_msg}, 400
