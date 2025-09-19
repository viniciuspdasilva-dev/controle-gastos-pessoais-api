from typing import List, Optional
from pydantic import BaseModel

from models import Categoria


class CategoriaSchema(BaseModel):
    name: str = "Cartões"


class ListaCategoriaSchema(BaseModel):
    categorias: List[CategoriaSchema]


class CategoriaViewSchema(CategoriaSchema):
    id: int = 0


class SearchCategoriaSchema(BaseModel):
    name: Optional[str] = "Cartões"


class CategoriaFormSchema(CategoriaSchema):
    pass


def definir_categoria(categoria: Categoria):
    return {
        "id": categoria.id,
        "name": categoria.name
    }


def definir_categorias(categorias: List[Categoria]):
    results = []
    for categoria in categorias:
        results.append(definir_categoria(categoria))
    return {"categorias": results}
