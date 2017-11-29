# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import abc
import logging


class R7rParser(object):
    """Abstract class to define parsers"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, input_fnames, output_fname):
        self.input_fnames = input_fnames
        self.output_fname = output_fname
        logging.basicConfig(format=("%(asctime)s,%(msecs)d %(levelname)-8s "
                                    "[%(filename)s:%(lineno)d] %(message)s"),
                            datefmt="%d-%m-%Y:%H:%M:%S",
                            level=logging.DEBUG)

    @abc.abstractmethod
    def normalize(self):
        return
