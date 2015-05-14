import datetime
from cryptacular.bcrypt import BCRYPTPasswordManager
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UnicodeText
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, deferred, relationship, scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, unique=True, nullable=False)
    _password = deferred(Column('password', UnicodeText, nullable=False))
    joined = deferred(Column(DateTime, default=datetime.datetime.utcnow))

    campaigns = association_proxy('user_campaigns', 'campaign', creator=lambda c: Membership(campaign=c))
    characters = association_proxy('user_characters', 'character')

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


class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)

    users = association_proxy('campaign_users', 'user', creator=lambda u: Membership(user=u))


class Membership(Base):
    __tablename__ = 'memberships'

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    campaign_id = Column(Integer, ForeignKey(Campaign.id), primary_key=True)
    is_gm = Column(Boolean, nullable=False, default=False)

    user = relationship(User, backref=backref('user_campaigns', cascade='all, delete-orphan'))
    campaign = relationship(Campaign, backref=backref('campaign_users', cascade='all, delete-orphan'))

    def __init__(self, user=None, campaign=None, is_gm=False):
        self.user = user
        self.campaign = campaign
        self.is_gm = is_gm


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    name = Column(UnicodeText, nullable=False)
    full_name = Column(UnicodeText)
    portrait = Column(UnicodeText)
    biography = deferred(Column(UnicodeText))

    user = relationship(User, backref=backref('user_characters'))
