import toml
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import logging




class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

class Logger:
    class ColorFormatter(logging.Formatter):
        LEVEL_COLORS = {
            logging.DEBUG: LogColors.CYAN,
            logging.INFO: LogColors.GREEN,
            logging.WARNING: LogColors.YELLOW,
            logging.ERROR: LogColors.RED,
            logging.CRITICAL: LogColors.MAGENTA,
        }

        def format(self, record):
            log_color = self.LEVEL_COLORS.get(record.levelno, LogColors.WHITE)
            message = super().format(record)
            return f"{log_color}{message}{LogColors.RESET}"

    def __init__(self, name: str, level: int = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Check if the logger already has handlers to avoid adding multiple handlers
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setFormatter(self.ColorFormatter('%(asctime)s - %(levelname)s - %(message)s', 
                                                     datefmt='%Y-%m-%d %H:%M:%S'))
            self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger




def read_toml_conf_controlPC(file_path):
    data = {}
    with open(file_path, 'r') as config_file:
        config_file = toml.load(file_path)

    if 'name' in config_file['ControlPC']:
        data['name'] = config_file['ControlPC']['name']
    else:
        logger.warning("No name was given, default value for file name is: Test CLAM")
        data['name'] = "Test spectrum analyzer"

    data['date_time'] = f"{datetime.datetime.now()}"

    # Azimuth angle
    azimuth = {}
    if 'start' in config_file['ControlPC']['span']['azimuth']:
        azimuth['start'] = config_file['ControlPC']['span']['azimuth']['start']
    else:
         logger.critical("Didn't got azimuth start's angle, default value is 0")
         azimuth['start'] = 0
    
    if 'stop' in config_file['ControlPC']['span']['azimuth']:
        azimuth['stop'] = config_file['ControlPC']['span']['azimuth']['stop']
    else:
         logger.critical("Didn't got azimuth stop's angle, default value is 360")
         azimuth['stop'] = 360

    if 'step' in config_file['ControlPC']['span']['azimuth']:
        azimuth['step'] = config_file['ControlPC']['span']['azimuth']['step']
    else:
         logger.critical("Didn't got azimuth step's angle, default value is 1")
         azimuth['step'] = 1  
    data['azimuth'] = azimuth



    # Pitch angle
    pitch = {}
    if 'start' in config_file['ControlPC']['span']['pitch']:
        pitch['start'] = config_file['ControlPC']['span']['pitch']['start']
    else:
         logger.critical("Didn't got pitch start's angle, default value is 0")
         pitch['start'] = 0
    
    if 'stop' in config_file['ControlPC']['span']['pitch']:
        pitch['stop'] = config_file['ControlPC']['span']['pitch']['stop']
        
    else:
         logger.critical("Didn't got pitch stop's angle, default value is 90")
         pitch['stop'] = 90

    if 'step' in config_file['ControlPC']['span']['pitch']:
        pitch['step'] = config_file['ControlPC']['span']['pitch']['step']
    else:
         pitch['step'] = 1
         logger.critical("Didn't got pitch step angle, default value is 1")  
    data['pitch'] = pitch

    # Freq
    freq = {}
    if 'start' in config_file['ControlPC']['freq']:
        freq['start'] = config_file['ControlPC']['freq']['start']
    else:
         logger.error("No freq start was supplied, exit system")
         exit()
    
    if 'stop' in config_file['ControlPC']['freq']:
        freq['stop'] = config_file['ControlPC']['freq']['stop']
    else:
         logger.error("No freq stop was supplied, exit system")
         exit()

    if 'step' in config_file['ControlPC']['freq']:
        freq['step'] = config_file['ControlPC']['freq']['step']
    else:
         logger.error("No freq stop was supplied, exit system")
         exit()
    data['freq'] = freq


    if 'power' in config_file['ControlPC']:
        data['power'] = config_file['ControlPC']['power']
    else:
         logger.error("No power was supplied, exit system")
         exit()

    if 'wave_type' in config_file['ControlPC']:
        data['wave_type'] = config_file['ControlPC']['wave_type']
    else:
        data['wave_type'] = 'CW'
        logger.critical("Didn't got wave_type, default value is CW")


    if 'sleep' in config_file['ControlPC']:
        data['sleep'] = config_file['ControlPC']['sleep']
    else:
        logger.warning("No sleep time was given, default value is: 1.5")
        data['sleep'] = 1.5

    if 'results_file_name' in config_file['ControlPC']:
        data['results_file_name'] = config_file['ControlPC']['results_file_name']
    else:
        data['results_file_name'] = "Results of CLAM"
        logger.warning("No name for results file was given, default value is: Results of CLAM")
    
    return data
    



def print_dict(data:dict):
    for key, val in data.items():
        print(f"{key}  --->  {val}")


