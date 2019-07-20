from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

engine = create_engine('mysql+pymysql://root@localhost:3306/evotingparthenope', convert_unicode = True, echo = False, pool_size=100, max_overflow=0)
Base = declarative_base()
Base.metadata.reflect(engine)

from sqlalchemy.orm import relationships, backref


class Users(Base, UserMixin):
    __table__ = Table('utente', Base.metadata, autoload = True, autoload_with = engine)

    def get_user_by_id(id):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(Users).get(id)


class Candidato(Base):
    __table__ = Table('candidato', Base.metadata, autoload=True, autoload_with=engine)

    def get_candidato_by_id(id):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(Candidato).get(id)

class Elezioni(Base):
    __table__ = Table('elezioni', Base.metadata, autoload=True, autoload_with=engine)

    def get_elezione_by_id(id):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(Elezioni).get(id)


    def get_elezione_by_desc(descElezione):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(Elezioni).filter_by(DESCRIZIONE_ELEZIONE=descElezione).first()


class Lista(Base):
    __table__ = Table('lista', Base.metadata, autoload=True, autoload_with=engine)

    def get_lista_by_name(nomeLista):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(Lista).filter_by(NOME_LISTA = nomeLista).first()


class Voto(Base):
    __table__ = Table('voto', Base.metadata, autoload=True, autoload_with=engine)


class conteggio_voti_c(Base):
    __table__ = Table('conteggio_voti_candidato', Base.metadata, autoload=True, autoload_with=engine)

    def get_candidato_by_id(id, id_elezione):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(conteggio_voti_c).filter_by(FK_ID_CANDIDATO = id).filter_by(FK_ID_ELEZIONE = id_elezione).first()


class conteggio_voti_l(Base):
    __table__ = Table('conteggio_voti_lista', Base.metadata, autoload=True, autoload_with=engine)

    def get_lista_by_id(id, id_elezione):
        Session = sessionmaker(bind=engine)
        q = Session()
        return q.query(conteggio_voti_l).filter_by(FK_ID_LISTA = id).filter_by(FK_ID_ELEZIONE = id_elezione).first()



