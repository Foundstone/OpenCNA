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
from utils import StringView


_FNAME_REGEX = r".*\d{14}-(.*?)-.*.log"


class SystemInfoParser(R7rParser):
    """Parse the output of system info command"""

    def __init__(self, input_fnames, output_fname):
        super(SystemInfoParser, self).__init__(input_fnames, output_fname)
        self.logger = logging.getLogger(__name__)

    def _is_a_line_separator(self, line):
        return line == '\r\n' or line == '\n'

    def normalize(self):
        self.logger.info(
            'system_info parser. Start processing: ' + str(self.input_fnames))
        match = re.match(_FNAME_REGEX, os.path.basename(self.input_fnames[0]))
        if not match:
            logging.error(('system_info parser. Failure: the input file '
                           'name ' + self.input_fnames[0] + ' does not match '
                           'the regex ' + _FNAME_REGEX))
            sys.exit(1)
        host_name = match.groups()[0]

        try:
            lines = []
            with open(self.input_fnames[0]) as infile:
                for systeminfoline in infile:
                    if systeminfoline.startswith(' '):
                        lines[len(lines) - 1] = lines[len(lines) - 1] + \
                            ' - ' + systeminfoline.strip().rstrip("\r\n")
                    else:
                        lines.append(systeminfoline.strip())

            result_dict = {}
            for _, iitt in enumerate(lines[1:]):
                pair_key_value = StringView(iitt).split_str(':', 1)
                label = pair_key_value[0].strip().title().replace(
                    ' ', '_').replace('(', '').replace(')', '').strip()
                result_dict[label] = pair_key_value[1].strip()

            result = [["host_name"] + result_dict.keys()]
            line = []
            for _, value in result_dict.iteritems():
                line.append(value)
            result.append([host_name] + line)

            self.logger.info(
                'system_info parser. Writing output: ' + str(self.output_fname))
            folder = os.path.dirname(self.output_fname)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(self.output_fname, "w") as handler:
                csv_writer = csv.writer(handler)
                csv_writer.writerows(result)

        except NameError as e:
            logging.exception(
                'system_info parser. Failure: ' + str(e.message))
            sys.exit(1)
        except Exception, e:
            logging.exception(
                'system_info parser. Failure: ' + str(e.message))
            sys.exit(1)
