# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import os
import sys
import argparse

import glob
import logging
import zipfile
import shutil

import process_list
import system_info
import netstat


_TMP_DIR = "/tmp"
_SHARE_INPUT = "/shared/input"
_SHARE_OUTPUT = "/shared/output"

_PARSERS = {
    process_list.ProcessListParser: ["*-process-list.log", "*-tasklist.log"],
    system_info.SystemInfoParser: ["*-systeminfo.log"],
    netstat.NetstatParser: ["*-netstat.log"],
    # "web-history.log": "web-history"
}


def _parse_arguments():
    parser = argparse.ArgumentParser(description=("Normalize a rastrea2r "
                                                  "endpoint snapshot to csv"))
    return parser.parse_args()


def process_snapshot(fname, out_folder):
    is_webhistory = os.path.basename(fname).startswith("webhistory-")
    zip_ref = zipfile.ZipFile(fname, 'r')
    extract_file_names = zip_ref.namelist()
    for fname_ in extract_file_names:
        if not fname_.startswith(extract_file_names[0]):
            dirname = os.path.dirname(fname_)
            dirname = dirname if dirname else fname_
            sys.stderr.write(("The zip file from rastrea2r does not have only "
                              "one folder: " + extract_file_names[0] + " and "
                              + dirname + "\n"))
            sys.exit(1)
    unzip_location = zip_ref.extract(extract_file_names[0], path=_TMP_DIR)
    for fname_ in extract_file_names[1:]:
        zip_ref.extract(fname_, path=_TMP_DIR)
    zip_ref.close()

    if is_webhistory:
        if os.path.isdir(out_folder):
            shutil.rmtree(out_folder)
        shutil.move(unzip_location, out_folder)
    else:
        date = os.listdir(unzip_location)
        if len(date) > 1:
            logging.error(("The zip file from rastrea2r contains more than one "
                           "snapshot: " + ", ".join(date)))
            sys.exit(1)

        date = date[0]
        logs_folder = os.path.join(unzip_location, date)

        for parser_obj in _PARSERS:
            fname_regexs = _PARSERS[parser_obj]
            fnames = []
            for fname_regex in fname_regexs:
                fname = glob.glob(os.path.join(logs_folder, fname_regex))
                if not fname:
                    logging.error(
                        "No file in the snapshot matches the regex " + fname_regex)
                    sys.exit(1)
                fnames.append(fname[0])
            out_fname = ".".join(os.path.basename(
                fnames[0]).split(".")[:-1]) + ".csv"
            out_fname = os.path.join(out_folder, out_fname)
            parser = parser_obj(fnames, out_fname)
            parser.normalize()


def main():
    """Entrypoint"""
    in_path = _SHARE_INPUT
    if os.path.isdir(in_path):
        fnames = []
        for fname in os.listdir(in_path):
            if fname.endswith(".zip"):
                fnames.append(os.path.join(in_path, fname))
    else:
        fnames = [in_path]

    for fname in fnames:
        out_folder = os.path.basename(fname)[:-4]
        out_folder = os.path.join(_SHARE_OUTPUT, out_folder)
        process_snapshot(fname, out_folder)


if __name__ == "__main__":
    _parse_arguments()
    main()
