import inspect
import logging
import os
import json
import datetime
import collections
import ast

from flask import Flask
from flask_restful import Resource, Api, reqparse
import colorlog

from libs.losses_utils import LossesUtils
from libs.utils        import Utils
from libs.update       import Update

from sql.db_connect    import Connect


def autolog(msg):
    func = inspect.currentframe().f_back.f_code
    logging.debug('%s: %s in %s:%i' % (msg, func.co_name, func.co_filename, func.co_firstlineno))



class Core():
    def __init__(self):
        self.load_config()


        # NOT SURE HOW TO HAVE JUST ONE LOGGER, SO I'M IMPORTING IT AGAIN AND SETTING IT UP.. AGAIN
        f_handler = logging.FileHandler(self.get_config()['log_path'])
        f_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)%:%(name)s:%(message)s'))

        self.logger = colorlog.getLogger()
        self.logger.handlers = [f_handler]
        self.logger.setLevel(logging.DEBUG)


        # Check the database before initilizaing the rest of the libraries
        # losses_utils will try to connect to the library, causing it to create an empty file.
        self.db            = Connect(self.config['database']['data'])
        self.update        = Update(self.config, self.logger, self.db)
        self.lu            = LossesUtils(self.config)
        self.u             = Utils(self.config)


    def load_config(self):
        config_paths = ['/etc/eve_watch/config.json', '%s/config.json' % (os.getcwd())]
 
 
        for path in config_paths:
            if os.path.exists(path):
                with open(path) as cfg:
                    config = json.load(cfg)
                    break


        if not config:
            print('Unable to load config')
            exit(1)

        self.config = config

        

    def get_config(self):
        return self.config


    def update_database(self, start_time, end_time, alliance):
        self.logger.info('updating database')
        self.update.update_losses(start_time, end_time, alliance)

    
    
    
    def fleet_composition(self, alliance, start_time, end_time, min_fleet_limit=1):
        kill_dict   = {}
        fleet_dict  = {}
        some_dict   = {}
        seen_kills  = []
        filtered_dict = {}
        ordered_and_filtered_dict = {}
        return_data = []


        s_start_time = datetime.datetime.strptime(start_time, '%Y%m%d%H%M').strftime('%Y%m%d%H00')
        s_end_time   = datetime.datetime.strptime(end_time,   '%Y%m%d%H%M').strftime('%Y%m%d%H00')

        # Make the datetime.datetime for losses_utils.py 
        d_start_time = datetime.datetime.strptime(s_start_time, '%Y%m%d%H%M')
        d_end_time   = datetime.datetime.strptime(s_end_time,   '%Y%m%d%H%M')

        
        
        self.update_database(s_start_time, s_end_time, alliance)

        s = self.lu.query(alliance, start_time=d_start_time, end_time=d_end_time, type_='attacker')

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


            kb_links = []
            times_used = len(filtered_dict[k])

            if times_used >= min_fleet_limit:
                # FIX EVAL

                #['Ashimmu', 'Ashimmu', 'Devoter', 'Ishtar', 'Legion', 'Prophecy', 'Prophecy', 'Sacrilege', 'Stratios', 'Stratios']
                 
                c = collections.Counter(ast.literal_eval(k)).most_common()

                # jesus fuck
                #print('SUCCESSFULL USAGE: (%s)' % (times_used), 'SHIPS: %s' % (' '.join('%s %sx ' % t for t in c)))

              

                return_data.append({'%s' % (times_used):c,'kb_links':filtered_dict[k]})


        return return_data
        

