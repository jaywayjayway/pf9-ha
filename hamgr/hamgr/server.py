#!/usr/bin/env python

# Copyright (c) 2016 Platform9 Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from eventlet import wsgi
from hamgr import periodic_task
from paste.deploy import loadapp
import argparse
import ConfigParser
import eventlet
import logging
import logging.handlers

eventlet.monkey_patch()


def _get_arg_parser():
    parser = argparse.ArgumentParser(description="High Availability Manager for VirtualMachines")
    parser.add_argument('--config-file', dest='config_file', default='/etc/pf9/hamgr/hamgr.conf')
    parser.add_argument('--paste-ini', dest='paste_file')
    return parser.parse_args()


def _configure_logging(conf):
    log_filename = conf.get("log", "location")
    logging.basicConfig(filename=log_filename,
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=1024 * 1024 * 5, backupCount=5)
    logging.root.addHandler(handler)


def start_server(conf, paste_ini):
    _configure_logging(conf)
    if paste_ini:
        paste_file = paste_ini
    else:
        paste_file = conf.get("DEFAULT", "paste-ini")
    periodic_task.start()
    wsgi_app = loadapp('config:%s' % paste_file, 'main')
    wsgi.server(eventlet.listen(('', conf.getint("DEFAULT", "listen_port"))), wsgi_app)


if __name__ == '__main__':
    parser = _get_arg_parser()
    conf = ConfigParser.ConfigParser()
    with open(parser.config_file) as f:
        conf.readfp(f)
    start_server(conf, parser.paste_file)

