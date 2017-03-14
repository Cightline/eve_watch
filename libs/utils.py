import xml.etree.cElementTree as ET
import datetime
import hashlib
import os
import json
import logging


import colorlog

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


from sql.db_connect import Connect

from libs.losses_utils import LossesUtils
from libs.update       import Update



class Utils():
    def __init__(self):
        self.load_config()


        f_handler = logging.FileHandler(self.config['log_path'])
        f_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)%:%(name)s:%(message)s'))

        self.logger = colorlog.getLogger()
        self.logger.handlers = [f_handler]
        self.logger.setLevel(logging.DEBUG)

        # Load up a bunch of shit
        self.db           = Connect(self.config['database']['data'])
        self.update_utils = Update(self.config, self.logger, self.db)
        self.losses_utils = LossesUtils(self.config)


        self.base = automap_base()
        engine  = create_engine(self.config['database']['ccp_dump'], convert_unicode=True)
        self.base.prepare(engine, reflect=True)
        self.session = Session(engine)


    def load_config(self):
        config_paths = ['/etc/eve_watch/config.json', '%s/config.json' % (os.getcwd())]

        for path in config_paths:
            if os.path.exists(path):
                with open(path) as cfg:
                    config = json.load(cfg)
                    break

        if not config:
            print('unable to load config')
            exit(1)

        self.config = config

   
    def autolog(msg):
        func = inspect.currentframe().f_back.f_code
        self.logger.debug('%s: %s in %s:%i' % (msg, func.co_name, func.co_filename, func.co_firstlineno))


    def format_currency(amount):
        return '{:,.2f}'.format(amount)


    def format_time(timestamp):
        if timestamp:
            return datetime.datetime.utcfromtimestamp(timestamp).isoformat()
        else:
            return 'N/A'


    def alliance_id_from_corp_id(self, id):
        q = self.session.query(self.base.classes.corporations.alliance_id).filter_by(id=id)

        print(dir(q))

        return q.first() 


    def lookup_typename(self, id):
        #Base.classes.invTypes is the table, typeName is the column
        q = self.session.query(self.base.classes.invTypes.typeName).filter_by(typeID=id)

        result = q.first()

        if result:
            return result[0]
    
        return None
    
    def lookup_typeid(self, name):
        q = self.session.query(self.base.classes.invTypes.typeID).filter_by(typeName=name)

        result = q.first()

        if result:
            return result[0]

        return None

    def lookup_system(self, name):
        query = self.session.query(self.base.classes.mapSolarSystems).filter(
            self.base.classes.mapSolarSystems.solarSystemName.like(name))
       
        return query.first() or None


    def lookup_planets(self, solarSystemID):
        #sqlite> select * from mapDenormalize where itemID = 40000002;
        #itemID      typeID      groupID     solarSystemID  constellationID  regionID    orbitID     x               y              z               radius      itemName    security    celestialIndex  orbitIndex
        #----------  ----------  ----------  -------------  ---------------  ----------  ----------  --------------  -------------  --------------  ----------  ----------  ----------  --------------  ----------
        #40000002    11          7           30000001       20000001         10000001    40000001    161891117336.0  21288951986.0  -73529712226.0  5060000.0   Tanoo I     0.858324    1                         
        #sqlite> 
        
        data = self.session.query(self.base.classes.mapDenormalize).filter_by(groupID=7, solarSystemID=solarSystemID)

        return data
