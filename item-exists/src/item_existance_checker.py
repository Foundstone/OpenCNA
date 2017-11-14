import os
import csv
import cPickle as pickle

from trainable_csv_processor import TrainableCsvProcessor


_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_MODEL_DIR = os.path.join("..", "models")
_MODEL_FNAME = os.path.join(_MODEL_DIR, "nsrl.pkl")


class ItemExistanceChecker(TrainableCsvProcessor):

    def __init__(self):
        description = ("Check if an input string is in the training set. By "
                       "default, it checks the existance in the executable "
                       "items of the NSRL.")
        super(ItemExistanceChecker, self).__init__(description)
        self.data = set()

    def process(self, csv_split_line):
        if self.args.m:
            with open(os.path.join(_MODEL_DIR, self.args.m)) as handler:
              self.data = pickle.load(handler)
        elif not self.data:
            with open(_MODEL_FNAME) as handler:
              self.data = pickle.load(handler)

        value = [csv_split_line[i] for i in self.columns_indices][0]
        return value in self.data

    def train(self):
        data = set()
        csv_reader = csv.reader(self.file_in)
        for row in csv_reader:
            self.data.add(row[0])
        pickle.dump(self.data, self.file_out)


if __name__ == "__main__":
    processor = ItemExistanceChecker()
    processor.run()
