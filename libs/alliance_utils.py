
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


class AllianceUtils():
    def __init__(self, config):
        self.base = automap_base()
        engine    = create_engine(config['database']['data'], convert_unicode=True)
        self.base.prepare(engine, reflect=True)
        self.session = Session(engine)


    def alliance_id_from_corp_id(self, id):
        q = self.session.query(self.base.classes.corporations).filter_by(id=id).first()

        print('ALLIANCE_ID: %s' % (q.alliance_id))

        return q.alliance_id or None

    def alliance_name_from_id(self, id):
        q = self.session.query(self.base.classes.alliances).filter_by(id=id).first()

        if q:
            return q.name

        return False
