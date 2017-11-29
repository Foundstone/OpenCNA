# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import os
import cPickle as pickle

from csv_processor import CsvProcessor


_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_MODEL_DIR = os.path.join("..", "models")
_MODEL_FNAME = os.path.join(_MODEL_DIR, "nsrl.pkl")

_WHITELIST = ["system idle process", "system"]


class ProcessNsrlChecker(CsvProcessor):
    """Check if a process is already in the NSRL"""

    def __init__(self):
        description = ("Check if an input string is in the training set. By "
                       "default, it checks the existance in the executable "
                       "items of the NSRL.")
        super(ProcessNsrlChecker, self).__init__(description)

    def process(self, csv_split_line):
        """Check if a process name is in the NSRL"""
        with open(_MODEL_FNAME) as handler:
            data = pickle.load(handler)
        data = [x.lower() for x in data]

        value = csv_split_line[0]
        if not value or value in _WHITELIST:
            res = False
        else:
            res = value.lower() in data
        return res


if __name__ == "__main__":
    ProcessNsrlChecker().run()
