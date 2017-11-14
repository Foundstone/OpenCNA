import abc

import argparse
import argcomplete

# TODO: fix me
from __init__ import __version__
from csv_processor import CsvProcessor


class TrainableCsvProcessor(CsvProcessor):
    """Base class for a csv processor that processes csv and it can be trained.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, description):
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

        actions = parser.add_subparsers(help="Available actions", 
                                        dest="action")
        train_parser = actions.add_parser("train", help=("Retrain the "
                                          "model. By default it uses a csv "
                                          "file read from stdin"))
        train_parser.add_argument("-i", required=False,
                                  help=("input csv file name to train, "
                                  "if omitted, stdin is used"))
        train_parser.add_argument("-o", required=True,
                                  help=("pickle (pkl) file of the model, "
                                  "it must be stored in the docker shared "
                                  "folder."))
        process_parser = actions.add_parser("process",
                                            help="Process a csv file")
        process_parser.add_argument("-m", required=False,
                                    help=("pickle file of the model, "
                                    "it must be stored in the docker shared "
                                    "folder. If missing, the predefined "
                                    "model is used"))
        process_parser.add_argument("-i", required=False,
                                    help=("input csv file name to process, "
                                    "if omitted, stdin is used. "))
        process_parser.add_argument("-o", required=False,
                                    help=("output csv file name, if omitted, "
                                    "stdout is used"))
        process_parser.add_argument("-c", required=True, 
                                    help=("list of column names (or indices), "
                                    "separated by comma, used as input"))
        process_parser.add_argument("-n", required=False,
                                    help=("new column name of the output"))
        super(TrainableCsvProcessor, self).__init__(description, parser)


    @abc.abstractmethod
    def train(self):
        """Process a csv line, which was already parsed."""
        return


    def run_train(self):
        self.train()


    def run(self):
        """Main method used to process the csv received from stdin, and printed
        to stdout.
        """
        if self.args.action == "process":
            self.run_process()
        elif self.args.action == "train":
            self.run_train()
