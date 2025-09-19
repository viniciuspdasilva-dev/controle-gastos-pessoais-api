from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# importando os elementos definidos no modelo
from models.base import Base
from models.tables import Categoria, Gastos, Tags

db_path = "database/"

if not os.path.exists(db_path):
    os.makedirs(db_path)

db_url = 'sqlite:///%s/db.sqlite3' % db_path

engine = create_engine(db_url, echo=True)

# Instancia um criador de seção com o banco
Session = sessionmaker(bind=engine)

# cria o banco se ele não existir
if not database_exists(engine.url):
    create_database(engine.url)

# cria as tabelas do banco, caso não existam
Base.metadata.create_all(engine)