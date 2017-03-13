import inspect
import logging
import os
import json

from flask import Flask
from flask_restful import Resource, Api, reqparse
import colorlog

from libs.losses_utils import LossesUtils
from libs.utils        import Utils
from libs.update       import Update
from libs.core         import Core

from sql.db_connect    import Connect



def autolog(msg):
    func = inspect.currentframe().f_back.f_code
    logging.debug('%s: %s in %s:%i' % (msg, func.co_name, func.co_filename, func.co_firstlineno))


def log_exception(sender, exception, **extra):
    logging.error('got exception during processing: %s' % (exception))



app  = Flask(__name__)
api  = Api(app)
core = Core()

f_handler = logging.FileHandler(core.get_config()['log_path'])
f_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)%:%(name)s:%(message)s'))

logger = colorlog.getLogger()
logger.handlers = [f_handler]
logger.setLevel(logging.DEBUG)


logger.info('test')

class FleetComposition(Resource):
    def get(self, start_time, end_time, alliance):

        #autolog(args)
    
        data = core.fleet_composition(start_time=start_time, end_time=end_time, alliance=[alliance])
         

        return data


api.add_resource(FleetComposition, '/api/fleet_composition/<string:start_time>/<string:end_time>/<int:alliance>')


if __name__ == '__main__':
    app.run(host=core.get_config()['host'], port=core.get_config()['port'], debug=core.get_config()['DEBUG'])
