# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import sys
import os
import logging
import re
import csv

from r7r_parser import R7rParser


_FNAME_REGEX = r".*\d{14}-(.*?)-.*.log"


class NetstatParser(R7rParser):
    """A parser for the netstat log file"""

    def __init__(self, input_fnames, output_fname):
        super(NetstatParser, self).__init__(input_fnames, output_fname)
        self.logger = logging.getLogger(__name__)

    def normalize(self):
        self.logger.info(
            'netstat parser. Start processing: ' + str(self.input_fnames))
        match = re.match(_FNAME_REGEX, os.path.basename(self.input_fnames[0]))
        if not match:
            logging.error(('netstat parser. Failure: the input file '
                           'name ' + self.input_fnames[0] + ' does not match '
                           'the regex ' + _FNAME_REGEX))
            sys.exit(1)
        host_name = match.groups()[0]

        try:
            netstat_lines = [["host_name", "protocol", "local_address",
                              "local_address_port", "foreign_address",
                              "foreign_address_port", "state", "PID"]]
            with open(self.input_fnames[0], 'r') as handler:
                for line in handler:
                    match = re.match(r" *(\S+) +(\S+):(\S+) +(\S+):(\S+) +(\S*) *(\d+)",
                                     line)
                    if match:
                        data = [host_name] + list(match.groups())
                        netstat_lines.append(data)

            self.logger.info(
                'netstat parser. Writing output: ' + str(self.output_fname))
            folder = os.path.dirname(self.output_fname)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(self.output_fname, "w") as handler:
                csv_writer = csv.writer(handler)
                csv_writer.writerows(netstat_lines)

        except NameError as e:
            logging.exception('netstat parser. Failure: ' + str(e.message))
            sys.exit(1)
        except Exception, e:
            logging.exception('netstat parser. Failure: ' + str(e.message))
            sys.exit(1)
