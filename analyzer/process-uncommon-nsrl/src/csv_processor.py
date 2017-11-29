# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import abc

import sys
import csv
import argparse
import collections


class CsvProcessor(object):
    """Base class for a csv processor that reads specific columns and creates
    new ones.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, description, parser=None):
        self.columns_indices = None
        if parser is None:
            parser = argparse.ArgumentParser(description=description,
                                             add_help=False)
            parser.add_argument("-c", required=True,
                                help=("list of column names (or indices), "
                                      "separated by comma, used as input"))
            parser.add_argument("-o", required=False,
                                help=("new column names of the output"))
        self.args = parser.parse_args()

    def __check_columns_existance(self, columns, header):
        for col in columns:
            if col not in header:
                sys.stderr.write(("The given column " + col + " is not "
                                  "an existing one"))
                sys.exit(1)

    def __compute_columns_indices(self, header):
        columns = self.args.c
        columns = columns.split(",")
        columns_are_numbers = True
        for col in columns:
            if not col.isdigit():
                columns_are_numbers = False
                break
            else:
                if int(col) < 1 or int(col) > len(header):
                    sys.stderr.write(("The given column " + col + " is not "
                                      "a valid index for the columns in the csv file"))
                    sys.exit(1)

        if columns_are_numbers:
            res = [int(c) - 1 for c in columns]
        else:
            self.__check_columns_existance(columns, header)
            res = []
            for col in columns:
                res.append(header.index(col))
        return res

    def run_process(self):
        """Main function, which calls the abstract process method"""
        output_writer = csv.writer(sys.stdout)
        first_row = True
        for row in csv.reader(iter(sys.stdin.readline, '')):
            if first_row:
                self.columns_indices = self.__compute_columns_indices(row)
                first_row = False
                if self.args.o:
                    output_writer.writerow(row + self.args.o.split(","))
                else:
                    output_writer.writerow(row)
            else:
                filtered_row = [row[i] for i in self.columns_indices]
                new_fields = self.process(filtered_row)
                if isinstance(new_fields, collections.Iterable):
                    row = row + [str(x) for x in list(new_fields)]
                else:
                    row = row + [str(new_fields)]
                output_writer.writerow(row)

    def run(self):
        """Main method"""
        self.run_process()

    @abc.abstractmethod
    def process(self, csv_split_line):
        """Process a csv line, which was already parsed."""
        return
