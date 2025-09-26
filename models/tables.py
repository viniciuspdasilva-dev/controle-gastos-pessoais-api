from datetime import datetime
from typing import List

from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped

from models import Base


association_table = Table(
    "association_table",
    Base.metadata,
    Column('gastos_id', ForeignKey("gastos.id")),
    Column('tags_id', ForeignKey("tags.id")),
)

class Tags(Base):
    __tablename__ = 'tags'
    id: Mapped[Integer] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[String] = Column(String(50), nullable=False)
    color: Mapped[String] = Column(String(10), nullable=False)

class Categoria(Base):
    __tablename__ = 'categoria'
    id: Mapped[Integer] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[String] = Column(String(50), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

class Gastos(Base):
    __tablename__ = 'gastos'
    id: Mapped[Integer] = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    descricao: Mapped[String] = Column(String(120), nullable=False)
    valor: Mapped[Float] = Column(Float, nullable=False, default=0.0)
    data: Mapped[DateTime]  = Column(DateTime, nullable=False, default=datetime.now)
    categoria_id: Mapped[Integer] = Column(Integer, ForeignKey('categoria.id'), nullable=False)


    categoria = relationship('Categoria', backref='gastos', lazy=True)
    tag: Mapped[List[Tags]] = relationship('Tags', secondary=association_table)

    def __init__(self, descricao, valor, data, categoria_id, tags=None):
        if tags is None:
            tags = []
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.categoria_id = categoria_id
        self.tag = tags







