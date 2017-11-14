#!/usr/bin/python
# -*- coding: utf-8 -*-

EPSILON_CHARACTER = '*'
FOLDER_SEPARATOR = '\\'

def normalize_line(line):
    return (line.rstrip()).lower()

def process_snapshot_paths(snapshots_file_name):
    snpashot_paths = set()
    with open(snapshots_file_name, 'r+') as f:
        try:
            for line in f:
                lline = list(line)
                if lline[0] == '"':
                    lline[0] = ''
                if lline[-1] == '"':
                    lline[-1] = ''
                line = (''.join(lline)).rstrip()
                line_split = line.split(FOLDER_SEPARATOR)
                path = reduce(lambda x,y: x + FOLDER_SEPARATOR + y, filter(lambda x: x != '', line_split[0:len(line_split)-1]))
                snpashot_paths.add(path)
        except:
            print 'There was a problem processing the file: {}'.format(snapshots_file_name)
    return snpashot_paths

