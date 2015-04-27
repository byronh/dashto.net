import datetime
from cryptacular.bcrypt import BCRYPTPasswordManager
from sqlalchemy import Column, DateTime, Integer, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    _password = Column('password', Unicode(255), nullable=False)
    joined = Column(DateTime, default=datetime.datetime.utcnow)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        manager = BCRYPTPasswordManager()
        self._password = manager.encode(value)

    def validate_password(self, value):
        manager = BCRYPTPasswordManager()
        return manager.check(self._password, value)
