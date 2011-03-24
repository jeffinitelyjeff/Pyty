import math

import logging
from settings import *

logging.basicConfig(level=LOG_LEVEL, filename=LOG_DIR+LOGFILE,
                    format='%(asctime)s: %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

_MARGIN = len('%s, %s %s %s %s:%s:%s: ' %
              ('Thu', '24', 'Mar', '2011', '17', '09', '37'))

class Logger:
    nl = "\n" + (" " * _MARGIN)
    
    def __init__(self):
        self.in_debug_file = False

    def enter_debug_file(self):
        self.in_debug_file = True

    def exit_debug_file(self):
        self.in_debug_file = False

    def debug(self, s, cond=True):
        if FILE_DEBUG and self.in_debug_file and cond:
            logging.debug(s.replace('\n', Logger.nl))

def announce_file(filename):
    gen_width = 40 - len(filename)
    lwidth = int(math.ceil(gen_width / 2.0))
    rwidth = int(math.floor(gen_width / 2.0))
    logging.debug("="*lwidth + " RUNNING " + filename.upper() + " " + "="*rwidth)
