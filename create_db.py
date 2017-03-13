
from sqlalchemy.ext.automap     import automap_base
from sqlalchemy                 import create_engine
from sqlalchemy_utils.functions import database_exists, drop_database
from sql import initialize_sql

from libs.core  import Core
from sql.losses import ItemsLost, Attacker, Kills


class CreateDB():
    def __init__(self):
        self.c       = Core()
        self.config  = self.c.load_config()
        self.db_path = self.c.config['database']['data']
        self.base    = automap_base()
       
    def create(self, confirm=False):

        if confirm:
            if database_exists(self.db_path):
                i = input('this will recreate the database, continue? [y/n]: ').lower().strip() 

                if i != 'y' and i != 'yes':
                    exit()
            
                drop_database(self.db_path)

        
        initialize_sql(create_engine(self.db_path, echo=False))



if __name__ == '__main__':

    cdb = CreateDB()
    r   = cdb.create(True)

    if r == None:
        print('databse created')
        
    else:
        print('unable to create the database')
        exit()
