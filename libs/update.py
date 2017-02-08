import argparse
import json
import datetime
import requests
import os

from dateutil.relativedelta import relativedelta

from sqlalchemy import *
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from libs.utils     import Utils
from sql.db_connect import Connect

import evelink



class Update():
    def __init__(self, config):
        self.config   = config
        self.utils    = Utils(self.config)
        self.eve      = evelink.eve.EVE() 
        self.db       = Connect(self.config['database']['data']) 
        self.classes  = self.db.base.classes
        self.headers  = {'user-agent': 'kill-frame/0.0.1 maintainer: Sightline email: sightline.networks@gmail.com', 'Accept-Encoding': 'gzip'}



    def create_databases(self):
        from sql        import initialize_sql
        from sql.pi     import Pi
        from sql.losses import ItemsLost, Kills
        from sql.alliances import Corporation, Alliance

        initialize_sql(self.db.engine)

    def check_database(self, create=False):
        if not os.path.exists(self.config['database']['data'].split(':')[-1]):
            self.create_database()



    def update_losses(self, start_time, end_time, alliance_ids):
        '''Pull the kills from zKillboard and store them in the database'''
        print('updating losses...')

        losses              = self.db
        items_lost          = {}
        alliances_requested = []
        time_format = '%Y-%m-%d %H:%M:%S'
        #start_time  = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%Y%m%d0000')

        # Gotta adjust this so it works with zkillboard
        # 2017021900
        # Convert it to datetime and back to make sure its legit, this also changes the minutes to 00  (ie 1900 rather than 1901)
        start_time = datetime.datetime.strptime(start_time, '%Y%m%d%H%M').strftime('%Y%m%d%H00')
        end_time   = datetime.datetime.strptime(end_time,   '%Y%m%d%H%M').strftime('%Y%m%d%H00')
        data = None
        
        self.check_database(create=True)

        print('Start date: %s' % (start_time))

        
        for alliance_id in alliance_ids:

            page = 0
            
            
            print('Working on: %s' % (alliance_id))
            
            while True:
                
                data = requests.get('https://zkillboard.com/api/kills/allianceID/%s/startTime/%s/endTime/%s/page/%s/' % (alliance_id, 
                                                                                                                         start_time, 
                                                                                                                         end_time, 
                                                                                                                         page), 
                                                                                                                         headers=self.headers)
           
                print(data.url)
                j_data = json.loads(data.text)

                print(len(j_data))
            

                for row in j_data:
                    
                    if type(j_data) == dict and 'error' in j_data.keys():
                        exit(j_data)

                    kill_time   = datetime.datetime.strptime(row['killTime'], time_format)
                    kill_id     = row['killID']

                    # See if the killID already exists in the database
                    query = losses.session.query(losses.base.classes.kills).filter_by(killID=kill_id).first()

                    if query:
                        #print('killID already exists, skipping...')
                        continue

                    
                    # The kill itself
                    kill = losses.base.classes.kills(killID=kill_id,
                                                 shipTypeID=row['victim']['shipTypeID'],
                                                 killTime=kill_time,
                                                 characterID=row['victim']['characterID'],
                                                 corporationID=row['victim']['corporationID'],
                                                 corporationName=row['victim']['corporationName'],
                                                 allianceID=row['victim']['allianceID'])


                    #res = self.es.index(index='eve', op_type='create', doc_type='items', body={'killID':kill_id, 
                    #                                                         'timestamp':kill_time, 
                    #                                                         'characterID':row['victim']['characterID'],
                    #                                                         'shipTypeID':self.utils.lookup_typename(row['victim']['shipTypeID']),
                    #                                                         'coprorationID':row['victim']['corporationID'],
                    #                                                         'corporationName':row['victim']['corporationName'],
                    #                                                         'allianceID':row['victim']['allianceID']})


                    # Attach the items lost to the kill 
                    for line in row['items']:
                        item = losses.base.classes.items_lost(typeID=line['typeID'])
                        kill.items_lost_collection.append(item)

                    #    res = self.es.index(index='eve', op_type='create', doc_type='items', body={'killID':kill_id, 
                    #                                                             'timestamp':kill_time, 
                    #                                                             'item':self.utils.lookup_typename(line['typeID'])})



            
                    for line in row['attackers']:
                        print(line)
                        attacker = losses.base.classes.attacker(weaponTypeID=line['weaponTypeID'],
                                                            allianceID=line['allianceID'],
                                                            corporationName=line['corporationName'],
                                                            shipTypeID=line['shipTypeID'],
                                                            characterName=line['characterName'],
                                                            characterID=line['characterID'],
                                                            allianceName=line['allianceName'])
                                                            

                        kill.attacker_collection.append(attacker)

                    #    res = self.es.index(index='eve', op_type='create', doc_type='attacker', body={'killID':kill_id,
                    #                                                                'shipTypeID':self.utils.lookup_typename(line['shipTypeID']),
                    #                                                                'allianceID':line['allianceID'],
                    #                                                                'weaponTypeID':self.utils.lookup_typename(line['weaponTypeID']),
                    #                                                                'characterName':line['characterName'],
                    #                                                                'allianceName':line['allianceName'],
                    #                                                                'coprorationName':line['corporationName'],
                    #                                                                'characterID':line['characterID'],
                    #                                                                'timestamp':kill_time})

                        #print(res)

                    

                    losses.session.add(kill)
                    losses.session.commit()

                if len(j_data) < 200:
                        break

                page += 1


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
