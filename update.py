import argparse
import json
import datetime
import requests

from dateutil.relativedelta import relativedelta

from sqlalchemy import *
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from libs.utils     import Utils
from sql.db_connect import Connect

import evelink



class Command():
    def __init__(self):
        self.config   = self.read_config()
        self.utils    = Utils(self.config)
        self.eve      = evelink.eve.EVE() 
        self.db       = Connect(self.config['database']['data']) 
        self.classes  = self.db.base.classes


        parser = argparse.ArgumentParser()
        parser.add_argument('--create-db', help='create the databases', action='store_true')
        parser.add_argument('--pi',        help='update the Planetary Interaction cache', action='store_true')
        parser.add_argument('--losses',    help='update the items and ships that have been destroyed', action='store', type=int)
        parser.add_argument('--alliances', help='update the alliances', action='store_true')


        
        self.args = parser.parse_args()
       


        if self.args.create_db:
            self.create_databases()

        if self.args.pi:
            self.update_pi()

        if self.args.losses:
            self.update_losses(self.args.losses)

        if self.args.alliances:
            self.update_alliances()


    def read_config(self, path='config.json'):
        with open(path) as cfg:
            config = json.load(cfg)
            assert(config)


        return config


    def create_databases(self):
        from sql        import initialize_sql
        from sql.pi     import Pi
        from sql.losses import ItemsLost, Kills
        from sql.alliances import Corporation, Alliance

        initialize_sql(self.db.engine)





    def update_losses(self, days_ago):
        '''Pull the kills from zKillboard and store them in the database'''
        print('updating losses...')

        losses              = self.db
        items_lost          = {}
        alliance_ids        = []
        alliances_requested = []
        time_format = '%Y-%m-%d %H:%M:%S'
        start_time  = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%Y%m%d00')

        print('Start date: %s' % (start_time))

        # add alliance ids from coalitions to alliance_ids
        for alliance in self.config['alliances']:
            alliance_ids.extend(self.config['alliances'][alliance])


        for alliance_id in alliance_ids:

            # what?
            if alliance_id in alliances_requested:
                continue 

            alliances_requested.append(alliance_id)
            kb_url = 'https://zkillboard.com/api/kills/allianceID/%s/startTime/%s' % (alliance_id, start_time)

            # USE REQUESTS JSON
            page = requests.get(kb_url)
            print(kb_url)
            data = json.loads(page.text)

            print('Working on: %s' % (alliance_id))

            # Example
            #{"characterID":926924867,"characterName":"clavo oxidado",
            #"corporationID":98390683,"corporationName":"Hogyoku","allianceID":1354830081,
            #"allianceName":"Goonswarm Federation","factionID":0,"factionName":"","securityStatus":-0.9,"damageDone":0,"finalBlow":0,"weaponTypeID":5439,"shipTypeID":0}
            # https://zkillboard.com/kill/54204593/


            for row in data:
                
                if type(data) == dict and 'error' in data.keys():
                    exit(data)

                kill_time   = datetime.datetime.strptime(row['killTime'], time_format)
                kill_id     = row['killID']

                # See if the killID already exists in the database
                query = losses.session.query(losses.base.classes.kills).filter_by(killID=kill_id).first()

                if query:
                    print('killID already exists, skipping...')
                    continue

                # The kill itself
                kill = losses.base.classes.kills(killID=kill_id,
                                             shipTypeID=row['victim']['shipTypeID'],
                                             killTime=kill_time,
                                             characterID=row['victim']['characterID'],
                                             corporationID=row['victim']['corporationID'],
                                             corporationName=row['victim']['corporationName'],
                                             allianceID=row['victim']['allianceID'])


                # Attach the items lost to the kill 
                for line in row['items']:
                    item = losses.base.classes.items_lost(typeID=line['typeID'])
                    kill.items_lost_collection.append(item)

        
                for line in row['attackers']:
                    attacker = losses.base.classes.attacker(weaponTypeID=line['weaponTypeID'],
                                                        allianceID=line['allianceID'],
                                                        corporationName=line['corporationName'],
                                                        shipTypeID=line['shipTypeID'],
                                                        characterName=line['characterName'],
                                                        characterID=line['characterID'],
                                                        allianceName=line['allianceName'])
                                                        

                    kill.attacker_collection.append(attacker)



                losses.session.add(kill)
                losses.session.commit()


    def update_alliances(self):
        #{'id': 99000304, 'member_count': 8, 'ticker': 'PIGS', 'name': 'THE SPACE P0LICE', 'executor_id': 98038175, 'member_corps': {699225816: {'id': 699225816, 'timestamp': 1423864860}, 875152542

        print('Deleting alliances and corporations...')
        self.db.session.query(self.db.base.classes.alliances).delete()
        self.db.session.query(self.db.base.classes.corporations).delete()
        self.db.session.commit()
       
        print('Adding current alliances...')
        alliances = self.eve.alliances().result

        for id_ in alliances.keys():

            member_count = alliances[id_]['member_count']
            ticker       = alliances[id_]['ticker']
            name         = alliances[id_]['name']
            executor_id  = alliances[id_]['executor_id']
            member_corps = alliances[id_]['member_corps']
    
            



            alliance = self.db.base.classes.alliances(id=id_,
                                                      member_count=member_count, 
                                                      ticker=ticker,
                                                      name=name,
                                                      executor_id=executor_id)

            
            for c in member_corps.keys():
                print(member_corps[c])
                corp = self.db.base.classes.corporations(alliance_id=member_corps[c]['id'])
                alliance.corporations_collection.append(corp)



            self.db.session.add(alliance)
            self.db.session.commit()



if __name__ == '__main__':
    cli = Command()
