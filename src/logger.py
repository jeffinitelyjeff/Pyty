from datetime import datetime

import logging
from settings import *

logging.basicConfig(level=LOG_LEVEL, filename=LOG_DIR+LOGFILE)

class Logger:
    nl = "\n" + (" " * 12)
    
    def __init__(self):
        self.in_debug_file = False

    def enter_debug_file(self):
        self.in_debug_file = True

    def exit_debug_file(self):
        self.in_debug_file = False

    def debug(self, s, cond=True):
        if FILE_DEBUG and self.in_debug_file and cond:
            logging.debug(" " + s.replace('\n', Logger.nl))

def announce_file(filename):
    logging.debug(" ---- RUNNING " + filename.upper() + " AT " +
                  str(datetime.now()) + " ----" + Logger.nl*2)
