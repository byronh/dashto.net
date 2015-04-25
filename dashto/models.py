import datetime
from dashto import db
from sqlalchemy import Column, DateTime, Integer, Unicode


class User(db.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    email = Column(Unicode(255), unique=True, nullable=False)
    password = Column(Unicode(255), nullable=False)
    joined = Column(DateTime, default=datetime.datetime.utcnow)