from typing import List, Optional

from pydantic import BaseModel


class RelatorioSchema(BaseModel):
    name: str

class RelatorioQuerySchema(BaseModel):
    initial_date: str
    final_date: str

class RelatorioTotalSchema(BaseModel):
    total: float

class GastosPerCategoriaSchema(RelatorioSchema):
    categoria_name: str = "Cartões"
    total: float = 256.0

class TotalizadorGastosPerCategoriaSchema(RelatorioSchema):
    relatorio: List[GastosPerCategoriaSchema] = []

class CategoriaTotal:
    categoria: str
    total: float
    def __init__(self, categoria: str, total: float):
        self.categoria = categoria
        self.total = total

def construir_relatorio_total_geral(total_gastos: float):
    return {
        "total": total_gastos,
    }

def construir_relatorio_gastos_per_categoria(relatorio: List[CategoriaTotal]):
    result = []
    for relatorio in relatorio:
        result.append({
            "categoria_name": relatorio.categoria,
            "total": relatorio.total
        })
    return result