
import json
import datetime
import argparse
import copy

import collections


from libs.losses_utils import LossesUtils
from libs.utils        import Utils
from libs.update       import Update

from sql.db_connect    import Connect



class Command():
    def __init__(self):
        with open('config.json') as cfg:
            self.config = json.load(cfg)
            assert(self.config)
    
        self.lu              = LossesUtils(self.config)
        self.u               = Utils(self.config)
        self.now             = datetime.datetime.now()
        self.db              = Connect(self.config['database']['data'])
        self.update          = Update(self.config)
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--fleet-comp', help='fleet composition', action='store', type=int)
        parser.add_argument('--min-fleet-limit', help='the minimum fleet size to show', action='store', type=int, default=3)
        parser.add_argument('--top-fleet-limit', help='the minimum fleet size to show', action='store', type=int, default=10)
        parser.add_argument('--update', help='update the database by days', action='store', type=int, default=30)
        parser.add_argument('--alliance', help='the alliance to update or view', action='store', type=int)
        parser.add_argument('--kills', help='do you want to list kills or losses', action='store', type=bool, default=True)

        self.args = parser.parse_args() 


        if self.args.fleet_comp:
            self.fleet_composition(alliance=[self.args.alliance], 
                                   days_ago=self.args.fleet_comp, 
                                   min_fleet_limit=self.args.min_fleet_limit, 
                                   top_fleet_limit=self.args.top_fleet_limit,
                                   kills=self.args.kills)


    def update_database(self, days, alliance):
        self.update.update_losses(days_ago=days, alliance_ids=alliance)


    
    def fleet_composition(self, alliance, days_ago, min_fleet_limit, top_fleet_limit, kills=False):
        kill_dict  = {}
        fleet_dict = {}
        some_dict  = {}
        seen_kills = []
        filtered_dict = {}
        ordered_and_filtered_dict = {}

        self.update_database(days=days_ago, alliance=alliance)

        start_date = self.now - datetime.timedelta(days=days_ago)

        print('\n\nSearch start date: %s' % (start_date.strftime('%d %B %Y')))
        print('Alliance: %s (ID %s)\n' % ('FIX ME', alliance))
      


        # NOT REALLY IMPLEMENTED, FIX
        if kills:
            s = self.lu.query(alliance, start_date=start_date, type_='attacker')

        else:
            print('what')
            s = self.lu.query(alliance, start_date=start_date, type_='losses')
            
      
        # Attackers
        for kill in s:
            if kill.killID not in kill_dict:
                kill_dict[kill.killID] = [kill]

            else:
                kill_dict[kill.killID].append(kill)



        # Iterate through the dict
        for key, value in kill_dict.items():
            # We want more than 1 
            if len(value) >= min_fleet_limit:
                # Grab all the ships used and append them to a list
                # Fleets should have a unique killID, as they were all grouped by killID 
                fleet = []
                for attacker in value:
                    fleet.append(self.u.lookup_typename(attacker.shipTypeID))
    
                # Save the fleet to a dict
                fleet_dict[key] = fleet

        
        # Iterate the dict against itself to find matches
        for key, value in sorted(fleet_dict.items()):
            
            for k, v in sorted(fleet_dict.items()):
                if set(value) == set(v) and key not in seen_kills:

                    seen_kills.append(key)

                    d_key = str(sorted(value))

                    if d_key not in some_dict.keys():
                        some_dict[d_key] = [key, k]


                    else:
                        some_dict[d_key].extend([key, k])


        # Filter out duplicates
        for key, value in some_dict.items():

            if len(set(value)) == 1:
                some_dict[key] = None

            else:
                filtered_dict[key] = sorted(set(value))

        
        # So now we have a dictionary where the key is the fleet, and the values are the kills
        # We can run a len(value) to figure out how many kills they have used with the specific fleet.
        # and we can just eval (probably not the best idea) the key to find out what the ships actually are. 
        # http://stackoverflow.com/questions/16868457/python-sorting-dictionary-by-length-of-values
        for k in sorted(filtered_dict, key=lambda k: len(filtered_dict[k]), reverse=True):

            times_used = len(filtered_dict[k])

            if times_used >= min_fleet_limit:
                # FIX EVAL
                c = collections.Counter(eval(k)).most_common()
                
                # jesus fuck
                print('SUCCESSFULL USAGE: (%s)' % (times_used), 'SHIPS: %s' % (' '.join('%s %sx ' % t for t in c)))


                for item in filtered_dict[k]:
                    print('https://zkillboard.com/kill/%s' % (item))

                print('\n')

    

if __name__ == '__main__':
    com = Command()
