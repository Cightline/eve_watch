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
from libs.intel        import FleetComposition

from sql.db_connect    import Connect


def autolog(msg):
    func = inspect.currentframe().f_back.f_code
    logging.debug('%s: %s in %s:%i' % (msg, func.co_name, func.co_filename, func.co_firstlineno))



class Core():
    def __init__(self):
        self.load_config()


        # NOT SURE HOW TO HAVE JUST ONE LOGGER, SO I'M IMPORTING IT AGAIN AND SETTING IT UP.. AGAIN
        f_handler = logging.FileHandler(self.config['log_path'])
        f_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)%:%(name)s:%(message)s'))

        self.logger = colorlog.getLogger()
        self.logger.handlers = [f_handler]
        self.logger.setLevel(logging.DEBUG)


        # Check the database before initilizaing the rest of the libraries
        # losses_utils will try to connect to the library, causing it to create an empty file.
        self.db            = Connect(self.config['database']['data'])
        self.update_utils  = Update(self.config, self.logger, self.db)
        self.losses_utils  = LossesUtils(self.config)
        self.misc_utils    =  Utils(self.config)


