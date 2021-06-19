from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, create_engine, UniqueConstraint, Boolean
import re
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy

from src.app_init import app

######################################################################################
# The top half of this file contains helper functions for interacting with our database
######################################################################################

# TODO: We need to find a better way to store the database string
pg_string = f'postgresql+psycopg2://pi:raspberry@192.168.2.201:5432/thingsdb'
app.config['SQLALCHEMY_DATABASE_URI'] = pg_string

db = SQLAlchemy(app)


def get_engine(engine_string):
    if engine_string is None:
        engine_string = pg_string
    return create_engine(pg_string)


Session = sessionmaker()
def setup_session(engine_string=None):
    if engine_string is None:
        engine_string = pg_string
    engine = create_engine(engine_string)
    Session.configure(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


######################################################################################
# The second half of this file contains our database ORM.
######################################################################################


def get_table_name(class_string):
    res_list = []
    res_list = re.findall('[A-Z][^A-Z]*', class_string)
    return '_'.join(res_list).lower()


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return get_table_name(cls.__name__)

    @classmethod
    def get_unique(cls, session, **kwargs):
        cls_q = session.query(cls)
        for key, value in kwargs.items():
            col = getattr(cls, key)
            cls_q = cls_q.filter(col == value)
        first = cls_q.first()
        if first:
            return first
        else:
            obj = cls(**kwargs)
            session.add(obj)
            return obj

    def get_class_table_vals(self):
        """
        Only want to jsonify the table columns
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base = declarative_base(cls=Base)


class User(db.Model, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(70), unique = True)
    public_id = Column(String(50), unique=True)
    

class Photo(Base):
    photo_id = Column(Integer, primary_key=True)
    photo = Column(LargeBinary)


class Description(Base):
    description_id = Column(Integer, primary_key=True)
    description = Column(String)


class Thing(Base):
    thing_id = Column(Integer, primary_key=True)
    thing_name = Column(String)
    thing_description_id = Column(Integer, ForeignKey(Description.description_id))
    thing_photo_id = Column(Integer, ForeignKey(Photo.photo_id))

    description = relationship(Description)
    photo = relationship(Photo)
    
    
class Inventory(Base):
    inventory_id = Column(Integer, primary_key=True)
    inventory_thing_id = Column(Integer, ForeignKey(Thing.thing_id), unique=True)
    inventory_user_id = Column(Integer, ForeignKey(User.id))


class Group(Base):
    group_id = Column(Integer, primary_key=True)
    group_name = Column(String)
    user_owned_group = Column(Boolean)


class GroupThing(Base):
    __table_args__ = (UniqueConstraint('group_id', 'thing_id'), )

    group_thing_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey(Group.group_id))
    thing_id = Column(Integer, ForeignKey(Thing.thing_id))

    group = relationship(Group)
    thing = relationship(Thing)


class GroupUser(Base):
    __table_args__ = (UniqueConstraint('group_id', 'user_id'), )

    group_user_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey(Group.group_id))
    user_id = Column(Integer, ForeignKey(User.id))
    user_owner = Column(Boolean)

    group = relationship(Group)
    user = relationship(User)


def init_db(engine_string=None):
    Base.metadata.create_all(get_engine(engine_string))


if __name__ == '__main__':
    init_db()