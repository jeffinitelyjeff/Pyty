from datetime import datetime

import logging
from settings import *

logging.basicConfig(level=LOG_LEVEL, filename=LOG_DIR+LOGFILE)

class Logger:
    def __init__(self):
        self.in_debug_file = False

    def enter_debug_file(self):
        self.in_debug_file = True

    def exit_debug_file(self):
        self.in_debug_file = False

    def debug(self, s, cond=True):
        if self.in_debug_file and cond:
            logging.debug(s)

def announce_file(filename):
    logging.debug("\n\n---- RUNNING " + filename.upper() + " AT " +
                  str(datetime.now()) + " ----")
