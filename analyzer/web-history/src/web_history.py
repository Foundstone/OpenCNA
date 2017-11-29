# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import os
import re

from IPy import IP

from csv_processor import CsvProcessor


_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class WebHistoryProcessor(CsvProcessor):
    """Check if a URL in the web history is a naked IP"""

    def __init__(self):
        description = ("So far, check if a URL in web-history has a naked IP")
        # super(CsvProcessor, self).__init__(description)
        super(WebHistoryProcessor, self).__init__(description)

    def process(self, csv_split_line):
        value = [csv_split_line[i] for i in self.columns_indices][0]
        # good candidate to be an IP:
        ip_regex = r".....?://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:?[:/].*)?"
        match = re.match(ip_regex, value)
        is_naked_public = False
        if match:
            ip_candidate = match.groups()[0]
            try:
                is_naked_public = IP(ip_candidate).iptype() == 'PUBLIC'
            except ValueError:
                pass
        return is_naked_public


if __name__ == "__main__":
    WebHistoryProcessor().run()
