import abc

import os
import sys
import csv
import argparse
import argcomplete

# TODO: fix me
from __init__ import __version__


_SHARE_VOLUME = "/share"


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
            options = parser.add_argument_group("Optional arguments")
            options.add_argument("--help", "-h",
                                 help="Show this help message and exit",
                                 action="help")
            options.add_argument("--version",
                                 help="Display seekersdk version",
                                 action="version",
                                 version=__version__)
            parser.add_argument("-i", required=False, type=str,
                                help=("input csv file name to process, "
                                "if omitted, stdin is used. "))
            parser.add_argument("-o", required=False, type=str,
                                help=("output csv file name, if omitted, "
                                "stdout is used"))
            parser.add_argument("-c", required=True, 
                                help=("list of column names (or indices), "
                                "separated by comma, used as input"))
            parser.add_argument("-n", required=False,
                                help=("new column name of the output"))
        argcomplete.autocomplete(parser)
        self.args = parser.parse_args()
        if self.args.i:
            self.file_in = open(os.path.join(_SHARE_VOLUME, self.args.i))
        else:
            self.file_in = sys.stdin

        if self.args.o:
            self.file_out = open(os.path.join(_SHARE_VOLUME, self.args.o), "w")
        else:
            self.file_out = sys.stdout


    def __del__(self):
        if hasattr(self, 'args'):
            if self.args.i:
                self.file_in.close()
            if self.args.o:
                self.file_out.close()



    def __check_columns_existance(self, columns, header):
        for c in columns:
            if c not in header:
                sys.stderr.write(("The given column " + c + " is not "
                                  "an existing one"))
                # TODO: define the error code
                sys.exit(1)


    def __compute_columns_indices(self, header):
        columns = self.args.c
        columns = columns.split(",")
        columns_are_numbers = True
        for c in columns:
            if not c.isdigit():
                columns_are_numbers = False
                break
            else:
                if int(c) < 1 or int(c) > len(header):
                    sys.stderr.write(("The given column " + c + " is not "
                                  "a valid index for the columns in the csv file"))
                    # TODO: define the error code
                    sys.exit(1)

        if columns_are_numbers:
            res = [int(c)-1 for c in columns]
        else:
            self.__check_columns_existance(columns, header)
            res = []
            for c in columns:
                res.append(columns.index(c))
        return res


    def run_process(self):
        output_writer = csv.writer(self.file_out)
        first_row = True
        for row in csv.reader(iter(self.file_in.readline, '')):
            if first_row:
                self.columns_indices = self.__compute_columns_indices(row)
                first_row = False
                if self.args.n:
                    output_writer.writerow(row + [self.args.n])
                else:
                    output_writer.writerow(row)
            else:
                output_writer.writerow(row + [str(self.process(row))])


    def run(self):
        self.run_process()


    @abc.abstractmethod
    def process(self, csv_split_line):
        """Process a csv line, which was already parsed."""
        return
