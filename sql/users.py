from spearmint_libs.sql import *

class Character(Base):
    __tablename__ = 'characters'
    id           = Column(Integer, primary_key=True)
    character_id = Column(Integer)
    user_id      = Column(Integer, ForeignKey('users.id'))


class Users(Base):
    __tablename__ = 'users'
    id         = Column(Integer, primary_key=True)
    email      = Column(String(120), unique=True)
    password   = Column(String(255))
    api_code   = Column(String(255))
    api_key_id = Column(String(255))

    characters = relationship('Character', backref='user', lazy='dynamic')

    #def get_id(self):
    #    return self.email

    #def __unicode__(self):
    #    return self.email


