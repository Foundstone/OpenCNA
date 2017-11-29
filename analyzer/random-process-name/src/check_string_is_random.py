# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import os
from csv_processor import CsvProcessor
import fr_model as fmdl


_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

_WHITELIST = ["system idle process"]


class RandomStringChecker(CsvProcessor):
    """Check if a process name is randomic"""

    def __init__(self):
        description = ("Check if the process name seems to be randomly "
                       "generated. \nSet the column (-c) to be the one having "
                       "the process name.")
        super(RandomStringChecker, self).__init__(description)

    def process(self, csv_split_line):
        value = csv_split_line[0]
        models_fpath = ["ng_model_executable_2.pickle",
                        "ng_model_executable_3.pickle",
                        "fr_executable_names.pickle"]
        if value.endswith(".exe"):
            value = value[:-4]
        value = value.lower()
        if value in _WHITELIST:
            return
        fentr_model, fng_models, fmodel = fmdl.load_all(*models_fpath)
        res = fmdl.predict_query_string(value, fmodel, fentr_model,
                                        fng_models, False, is_folder=False,
                                        is_proc=True)
        is_random, _, _ = res
        return is_random


if __name__ == "__main__":
    RandomStringChecker().run()
