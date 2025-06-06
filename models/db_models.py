# models.py
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)


