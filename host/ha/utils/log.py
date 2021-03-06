# Copyright 2016 Platform9 Systems Inc.
# All Rights Reserved

from os.path import dirname
from os.path import exists
from os import makedirs
from oslo_config import cfg

import logging
import logging.handlers
import logging.config

CONF = cfg.CONF

log_group = cfg.OptGroup('log', title='Group for all log options')
log_opts = [
    cfg.StrOpt('level', default='DEBUG', help='Log level'),
    cfg.StrOpt('file', default='/var/log/pf9/pf9-ha.log',
               help='log file location')
]

CONF.register_group(log_group)
CONF.register_opts(log_opts, log_group)


LOG_FILE = CONF.log.file

def setup_log_dir_and_file(filename, mode='a', encoding=None, owner=None):
    try:
        if not exists(dirname(filename)):
            makedirs(dirname(filename))
        if not exists(filename):
            open(filename, mode).close()
        return logging.handlers.RotatingFileHandler(filename, mode=mode,
                                                    maxBytes=10*1024*1024,
                                                    backupCount=10)
    except:
        return logging.NullHandler()

def setup_logger():
    log_config = {
        'version': 1.0,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                '()': setup_log_dir_and_file,
                'level': CONF.log.level,
                'formatter': 'default',
                'filename': LOG_FILE,
            },
        },
        'root': {
            'handlers': ['file'],
            'level': CONF.log.level,
        },
    }
    logging.config.dictConfig(log_config)


def getLogger(logger_name):
    return logging.getLogger(logger_name)

setup_logger()

