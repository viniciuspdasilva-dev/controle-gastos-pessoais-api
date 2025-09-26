from datetime import datetime

from flask import redirect
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info, Tag, Contact
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError

from models import Session
from models.tables import Categoria, Gastos
from schemas.categoria import CategoriaSchema, definir_categorias, ListaCategoriaSchema, definir_categoria, \
    SearchCategoriaSchema, CategoriaViewSchema
from schemas.error import ErrorSchema
from schemas.gastos import GastosViewSchema, GastosPessoaisSchema, apresenta_gasto, GastosBuscaSchema, apresenta_gastos
from schemas.relatorios import construir_relatorio_gastos_per_categoria, CategoriaTotal, \
    TotalizadorGastosPerCategoriaSchema, RelatorioTotalSchema, construir_relatorio_total_geral, RelatorioQuerySchema

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
@app.post("/gastos",
          tags=[gastos_tag],
          description="Rota principal para inserir um novo gasto pessoal",
          responses={"200": GastosViewSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
          )
def gasto_cadastrar(form: GastosPessoaisSchema):
    # data_obj = datetime.strptime(form.data, "%d/%m/%Y")
    print(form)
    gasto = Gastos(
        descricao=form.descricao,
        data= form.data,
        valor=form.valor,
        categoria_id=form.categoria_id
    )
    session = Session()
    try:
        session.add(gasto)
        session.commit()
        return apresenta_gasto(gasto), 200
    except IntegrityError as e:
        error_msg = "Gasto já cadastrado no sistema" + str(e)
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/" + str(e)
        return {"message": error_msg}, 400
    finally:
        session.close()


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
        return {"message": f"Ocorreu um erro durante a consulta: {e}"}, 400
    finally:
        session.close()


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
    try:
        gasto = session.query(Gastos).filter(Gastos.id == id_gasto).first()
        session.commit()
        session.close()
        if gasto is None:
            return {"message": f"Nenhum gasto encontrado com o id: {id_gasto}"}, 404
        else:
            return apresenta_gasto(gasto), 200
    except Exception as e:
        error_msg = "Ocorreu um erro ao realizar a consulta: " + str(e)
        return {"message": error_msg}, 400
    finally:
        session.close()

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
        initial_date = datetime.strptime(initial_date, "%d/%m/%Y")
        final_date = datetime.strptime(final_date, "%d/%m/%Y")
        result = (
            session.query(Categoria.name.label("Categoria"), func.coalesce(func.sum(Gastos.valor), 0).label("total"))
            .join(Gastos, Categoria.id == Gastos.categoria_id)
            .filter(Gastos.data >= initial_date, Gastos.data <= final_date)
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
    finally:
        session.close()


@app.get("/relatorios/total_geral",
         tags=[relatorios_tag],
         description="Retorna o somatorio de todos os gastos dentro de um intervalo de tempo",
         responses={"200": RelatorioTotalSchema, "409": ErrorSchema, "400": ErrorSchema,
                    "500": ErrorSchema}
         )
def consultar_valor_total(query: RelatorioQuerySchema):
    initial_date = query.initial_date
    final_date = query.final_date
    session = Session()
    try:
        initial_date = datetime.strptime(initial_date, "%d/%m/%Y")
        final_date = datetime.strptime(final_date, "%d/%m/%Y")
        total = (
            session.query(func.coalesce(func.sum(Gastos.valor), 0).label("total"))
            .where(Gastos.data >= initial_date)
            .where(Gastos.data <= final_date)
            .scalar()
        )
        return construir_relatorio_total_geral(total), 200
    except Exception as e:
        error_msg = "Ocorreu um erro ao realizar a consulta: " + str(e)
        return {"message": error_msg}, 400
    finally:
        session.close()

# Rotas - Categorias
@app.get("/categorias",
         tags=[categoria_tag],
         description="Rota que lista as categorias de gastos salvas",
         responses={"200": ListaCategoriaSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema}
         )
def consultar_categorias_salvas():
    session = Session()
    try:
        categorias = session.query(Categoria).all()
        session.commit()
        return definir_categorias(categorias)
    except Exception as e:
        msg_erro = "Ocorreu um erro: " + str(e)
        return {"message": msg_erro}, 400
    finally:
        session.close()


@app.get("/categoria",
         tags=[categoria_tag],
         description="Rota que returna uma categoria pelo nome salvo",
         responses={"200": CategoriaViewSchema, "409": ErrorSchema, "400": ErrorSchema, "404": ErrorSchema,
                    "500": ErrorSchema}
         )
def consultar_categoria(query: SearchCategoriaSchema):
    categoria_name = query.name
    if not categoria_name:
        return {"message": "Nenhum criterio de pesquisa foi mandado"}, 400
    session = Session()
    try:
        categoria = session.query(Categoria).filter_by(name=categoria_name).first()
        session.commit()
        session.close()
        if not categoria:
            return {"message": f"Nenhum categoria encontrada com o criterio informado: {categoria_name} :/"}, 404
        else:
            return definir_categoria(categoria)
    except Exception as e:
        msg_erro = "Ocorreu um erro: " + str(e)
        return {"message": msg_erro}, 400
    finally:
        session.close()


@app.post("/categorias",
          tags=[categoria_tag],
          description="Rota que cria uma nova categoria de gasto",
          responses={"200": CategoriaSchema, "409": ErrorSchema, "400": ErrorSchema, "500": ErrorSchema})
def cadastrar_categoria(form: CategoriaSchema):
    categoria = Categoria(
        name=form.name
    )
    session = Session()
    try:
        session.add(categoria)
        session.commit()
        return definir_categoria(categoria), 200
    except IntegrityError as e:
        error_msg = "Gasto já cadastrado no sistema" + str(e)
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/ - " + str(e)
        return {"message": error_msg}, 400
    finally:
        session.close()
