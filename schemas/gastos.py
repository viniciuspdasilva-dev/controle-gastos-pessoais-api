from datetime import datetime
from typing import List

from pydantic import BaseModel

from models import Gastos


class GastosPessoaisSchema(BaseModel):
    name: str = "Lançamento de cartão"
    descricao: str = "Lançamento de cartão do mês 12/29"
    valor: float = 0.0
    data: datetime = "16/12/2029"
    categoria_id: int = 1

class GastosBuscaSchema(BaseModel):
    id: int = 1

class ListaGastosSchema(BaseModel):
    gastos: List[GastosPessoaisSchema] = []

class EditarGastoSchema(GastosPessoaisSchema):
    id: int = 1

class GastosViewSchema(GastosPessoaisSchema):
    pass

class GastoDelSchema(BaseModel):
    message: str
    nome: str

def apresenta_gastos(gastos: List[Gastos]):
    result = []
    for gasto in gastos:
        result.append({
            "id": gasto.id,
            "descricao": gasto.descricao,
            "valor": gasto.valor,
            "data": gasto.data.strftime("%d/%m/%Y"),
            "categoria_name": gasto.categoria.name
        })
    return {"gastos": result}

def apresenta_gasto(gasto: Gastos):
    return {
        "id": gasto.id,
        "descricao": gasto.descricao,
        "valor": gasto.valor,
        "data": gasto.data,
        "categoria_name": gasto.categoria.name
    }