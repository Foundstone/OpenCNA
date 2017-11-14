import os
from csv_processor import CsvProcessor
import random
import fr_model as fmdl


_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class RandomStringChecker(CsvProcessor):

    def __init__(self):
        description = ("Check if the strings in a row seem to be randomly"
                       "generated.")
        super(RandomStringChecker, self).__init__(description)

    def process(self, csv_split_line):
        value = [csv_split_line[i] for i in self.columns_indices][0]
        models_fpath = ["ng_model_folder_2.pickle", "ng_model_folder_3.pickle",
                        "fr_folder_names.pickle"]
        fentr_model, fng_models, fmodel = fmdl.load_all(*models_fpath)
        res = fmdl.predict_query_string(value, fmodel, fentr_model, \
                                        fng_models, False)
        is_random, description = res
        return is_random


if __name__ == "__main__":
    processor = RandomStringChecker()
    processor.run()
