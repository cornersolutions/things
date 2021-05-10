from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, create_engine
import re
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

######################################################################################
# The top half of this file contains helper functions for interacting with our database
######################################################################################

# TODO: We need to find a better way to store the database string
db_string = f'postgresql+psycopg2://pi:raspberry@192.168.2.201:5432/thingsdb'


def get_engine():
    return create_engine(db_string)


Session = sessionmaker()
def setup_session():
    engine = create_engine(db_string)
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


Base = declarative_base(cls=Base)


class User(Base):
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    

class Photo(Base):
    photo_id = Column(Integer, primary_key=True)
    photo = Column(LargeBinary)


class Description(Base):
    description_id = Column(Integer, primary_key=True)
    description = Column(String)


class Thing(Base):
    thing_id = Column(Integer, primary_key=True)
    thing_description_id = Column(Integer, ForeignKey(Description.description_id))
    thing_photo_id = Column(Integer, ForeignKey(Photo.photo_id))
    
    
class Inventory(Base):
    inventory_id = Column(Integer, primary_key=True)
    inventory_thing_id = Column(Integer, ForeignKey(Thing.thing_id))
    inventory_user_id = Column(Integer, ForeignKey(User.user_id))


if __name__ == '__main__':
    Base.metadata.create_all(get_engine())