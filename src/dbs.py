from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BLOB, ForeignKey
import re


Base = declarative_base()
db_engine = ''


def get_table_name(class_def):
    res_list = []
    res_list = re.findall('[A-Z][^A-Z]*', class_def.__class__.__name__)
    return '_'.join(res_list)


class User(Base):
    __tablename__ = get_table_name(class_name=User)
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    

class Photo(Base):
    __tablename__ = get_table_name(class_name=Photo)
    photo_id = Column(Integer, primary_key=True)
    photo = Column(BLOB)


class Description(Base):
    __tablename__ = get_table_name(class_name=Description)
    description_id = Column(Integer, primary_key=True)
    description = Column(String)


class Thing(Base):
    __tablename__ = get_table_name(class_name=Thing)
    thing_id = Column(Integer, primary_key=True)
    thing_description_id = Column(Integer, ForeignKey(Description.description_id))
    thing_photo_id = Column(Integer, ForeignKey(Photo.photo_id))
    
    
class Inventory(Base):
    __tablename__ = get_table_name(class_name=Inventory)
    inventory_id = Column(Integer, primary_key=True)
    inventory_thing_id = Column(Integer, ForeignKey(Things.thing_id))
    inventory_user_id = Column(Integer, ForeignKey(Users.user_id))


if __name__ == '__main__':
    Base.metadata.create_all(db_engine)