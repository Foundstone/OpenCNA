#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Jorge Couchet"

EPSILON_CHARACTER = '*'
FOLDER_SEPARATOR = '\\'


def normalize_line(line):
    return (line.rstrip()).lower()

def process_snapshot_paths(snapshots_file_name):
    snpashot_paths = set()
    with open(snapshots_file_name, 'r+') as handler:
        try:
            for line in handler:
                lline = list(line)
                if lline[0] == '"':
                    lline[0] = ''
                if lline[-1] == '"':
                    lline[-1] = ''
                line = (''.join(lline)).rstrip()
                line_split = line.split(FOLDER_SEPARATOR)
                path = reduce(lambda x, y: x + FOLDER_SEPARATOR + y,
                              [x for x in line_split[0:len(line_split) - 1] if x])
                snpashot_paths.add(path)
        except Exception:
            print 'There was a problem while processing the file: ' + str(snapshots_file_name)
    return snpashot_paths
