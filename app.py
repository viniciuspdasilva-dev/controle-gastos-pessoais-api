from getopt import error

from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect

from sqlalchemy.exc import IntegrityError
from models import Session
from models.tables import Categoria, Gastos, Tags

from flask_cors import CORS

from schemas.categoria import CategoriaSchema, definir_categorias, ListaCategoriaSchema, definir_categoria, \
    SearchCategoriaSchema, CategoriaViewSchema
from schemas.error import ErrorSchema
from schemas.gastos import GastosViewSchema, GastosPessoaisSchema, apresenta_gasto, GastosBuscaSchema, apresenta_gastos

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
gastos_tag = Tag(name="Gastos Pessoais", description="Adição, visualização e remoção de gastos pessoais à base")
categoria_tag = Tag(name="Categorias", description="Adição de categorias de um gasto cadastrado na base")


@app.get("/", tags=[home_tag])
def home():
    return redirect("/openapi")


# Rotas - Gastos

@app.post("/gasto/cadastrar",
          tags=[gastos_tag],
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
         responses={"200": GastosViewSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
         )
def buscar_gasto(query: GastosBuscaSchema):
    id_gasto = query.id
    if id_gasto is None or id_gasto == 0:
        return {"message": "Não foi possivel realizar a consulta, pois o id não foi enviado corretamente"}, 400
    session = Session()
    gasto  = session.query(Gastos).filter(Gastos.id == id_gasto).first()
    if gasto is None:
        return {"message": f"Nenhum gasto encontrado com o id: {id_gasto}"}, 404
    else:
        return apresenta_gasto(gasto), 200


# Rotas - Categorias
@app.get("/categorias",
         tags=[categoria_tag],
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
         responses={"200": CategoriaViewSchema, "409": ErrorSchema, "400": ErrorSchema, "404": ErrorSchema, "500": ErrorSchema}
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
