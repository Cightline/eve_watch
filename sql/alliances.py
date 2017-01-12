from sql import *

class Corporation(Base):
    __tablename__ = 'corporations'
    id           = Column(Integer,  primary_key=True)
    corp_id      = Column(Integer)
    alliance_id  = Column(Integer,  ForeignKey('alliances.id'))


class Alliance(Base):
    __tablename__ = 'alliances'
    id           = Column(Integer, primary_key=True)
    member_count = Column(Integer)
    ticker       = Column(String)
    name         = Column(String)
    executor_id  = Column(Integer)
    member_corps = relationship('Corporation', backref='alliance', lazy='dynamic')


    def __unicode__(self):
        return self.id


