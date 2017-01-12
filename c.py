
import json
import datetime
import argparse

import collections

import pandas as pd


from libs.losses_utils import LossesUtils
from libs.utils        import Utils

from sql.db_connect    import Connect




class Command():
    def __init__(self):
        with open('config.json') as cfg:
            self.config = json.load(cfg)
            assert(self.config)
    
        self.of_path         = 'output.txt'
        self.of_file         = open('output.txt','w')
        self.lu              = LossesUtils(self.config)
        self.u               = Utils(self.config)
        self.now             = datetime.datetime.now()
        self.db              = Connect(self.config['database']['data'])
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--fleet-comp', help='fleet composition', action='store', type=int)

        self.args = parser.parse_args() 
        
        if self.args.fleet_comp:
    
            for a in self.config['alliances']:
                self.fleet_composition(a, self.args.fleet_comp)

    def fleet_composition(self, alliance, days_ago):
        kill_dict  = {}
        ship_dict  = {}

        start_date = self.now - datetime.timedelta(days=days_ago)

        print('\n\nSearch start date: %s' % (start_date))
        print('Alliance: %s (ID %s)\n' % (alliance, self.config['alliances'][alliance][0]))
       
        s = self.lu.query(self.config['alliances'][alliance], start_date=start_date)

        
        #kill_frame = pd.read_sql(s.statement, self.db.session.bind)

        #Index(['id', 'killID', 'weaponTypeID', 'allianceID', 'corporationName','shipTypeID', 'characterName', 'characterID', 'allianceName','killTime'],


        # AVERAGE SHIPS PER KILL
        #print('AVERAGE SHIPS PER KILL: %s\n' % (kill_frame.groupby('killID')['characterName'].nunique().mean()))

        # MAX SHIPS PER KILL
        #print('MAX SHIPS PER KILL: %s\n' % (kill_frame.groupby('killID')['characterName'].nunique().max()))
            
        # SHIP USAGE (SUCCESSFUL KILLS)
        #ship_counts = kill_frame['shipTypeID'].value_counts()

        #print('SHIP/SUCCESSFUL KILLS\n')
        #for value in ship_counts.index:
        #    print(self.u.lookup_typename(int(value)), ship_counts[value])


        #print(kill_frame.groupby('killID'))


        #kill_groups = kill_frame.groupby(['killID'])['shipTypeID']
    

      
        #print(kill_frame.to_dict())


        #print(kill_dict)
    
        # GO BY KILLID 

        # GET THE SHIPS

        # COMPARE TO THE REST OF THE KILLIDS

        for item in s:
            if item.killID not in kill_dict.keys():
                kill_dict[item.killID] = [self.u.lookup_typename(item.shipTypeID)]

            else:
                kill_dict[item.killID].append(self.u.lookup_typename(item.shipTypeID))


    
        matches = {}
        
        for value in kill_dict.values():

            for v in kill_dict.values():
                if len(value) <= 1:
                    continue

                if set(v) == set(value):
                    
                    h = '-'.join(sorted(value))
                    if h not in matches.keys():
                        matches[h] = 1

                    else:
                        matches[h] += 1



        for match in matches:
            print(' '.join(match.split('-')), matches[match])


if __name__ == '__main__':
    com = Command()
