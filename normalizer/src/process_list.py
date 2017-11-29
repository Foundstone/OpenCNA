# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import sys
import os
import itertools
import codecs
import logging
import re
import csv
import pandas as pd  # this is

from r7r_parser import R7rParser


_FNAME_REGEX = r".*\d{14}-(.*?)-.*.log"


class ProcessListParser(R7rParser):
    """Parse process-list log file"""

    def __init__(self, input_fnames, output_fname):
        super(ProcessListParser, self).__init__(input_fnames, output_fname)
        self.logger = logging.getLogger(__name__)

    def _is_a_line_separator(self, line):
        return line == '\r\n' or line == '\n'

    def normalize(self):
        self.logger.info(
            'process_list parser. Start processing: ' + str(self.input_fnames))
        match = re.match(_FNAME_REGEX, os.path.basename(self.input_fnames[0]))
        if not match:
            logging.error(('process_list parser. Failure: the input file '
                           'name ' + self.input_fnames[0] + ' does not match '
                           'the regex ' + _FNAME_REGEX))
            sys.exit(1)
        host_name = match.groups()[0]

        try:
            process_list = []
            header_process_list = []
            with codecs.open(self.input_fnames[0], encoding='utf-16') as handler:
                for key, group in itertools.groupby(handler, self._is_a_line_separator):
                    if not key:
                        mylist = list(group)
                        if mylist:
                            data = {}
                            it_list = []
                            for item in mylist:
                                item_par = item.split('=')
                                data[item_par[0]] = item_par[1].rstrip("\r\n")
                                it_list.append(item_par[1].rstrip("\r\n"))
                                if not item_par[0] in header_process_list:
                                    header_process_list.append(item_par[0])
                            process_list.append(it_list)

            header_task_list = []
            tasklist_list = []
            with open(self.input_fnames[1]) as infile:
                for line in infile:
                    if 'CPU Time Window Title' in line:
                        while not re.match(r'\s*\r?\n', line):
                            if 'Modules' in line:
                                break
                            line = next(infile, '')
                            if not line:
                                break
                    if line.startswith(' '):
                        size = len(tasklist_list)
                        tasklist_list[size - 1] += line.strip().rstrip("\r\n")
                    else:
                        if not line.startswith('='):
                            if line.strip().rstrip("\r\n"):
                                tasklist_list.append(line.strip())

            pid_end = tasklist_list[0].find('PID') + len('PID')
            pid_start = tasklist_list[0].find('PID') + len('PID') - 8
            image_name = tasklist_list[0][:pid_start].strip().replace(' ', '_')
            pid = tasklist_list[0][pid_start:pid_end].strip().replace(' ', '_')
            modules = tasklist_list[0][pid_end:].strip().replace(' ', '_')
            header_task_list.append(image_name)
            header_task_list.append(pid)
            header_task_list.append(modules)

            task_list = []
            for _, iitt in enumerate(tasklist_list[1:]):
                tasklist_item = []
                image_name_value = iitt[:pid_start].strip()
                pid_value = iitt[pid_start:pid_end].strip()
                modules_value = iitt[pid_end:].strip()
                tasklist_item.append(image_name_value)
                tasklist_item.append(pid_value)
                tasklist_item.append(modules_value)
                task_list.append(tasklist_item)

            df_process_list = pd.DataFrame(
                process_list, columns=header_process_list)
            df_task_list = pd.DataFrame(task_list, columns=header_task_list)
            df_result = df_process_list.merge(df_task_list, left_on='ProcessId',
                                              right_on='PID', how='outer')

            result = [["Host_Name", "PID", "Name", "Description",
                       "CommandLine", "Parent_PID", "Executable_Path", "Modules"]]
            for _, row in df_result.iterrows():
                pid = row['ProcessId'] if pd.isnull(row['PID']) else row['PID']
                name = row['Name'] if not pd.isnull(row['Name']) else ''
                description = row['Description'] if not pd.isnull(
                    row['Description']) else ''
                command_line = row['CommandLine'] if not pd.isnull(
                    row['CommandLine']) else ''
                parent_pid = row['ParentProcessId'] if not pd.isnull(
                    row['ParentProcessId']) else ''
                executable_path = row['ExecutablePath'] if not pd.isnull(
                    row['ExecutablePath']) else ''
                modules = row['Modules'] if not pd.isnull(
                    row['Modules']) else ''
                this_line = [host_name, pid, name, description, command_line,
                             parent_pid, executable_path, modules]
                result.append(this_line)

            self.logger.info(
                'process_list parser. Writing output: ' + str(self.output_fname))
            folder = os.path.dirname(self.output_fname)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(self.output_fname, "w") as handler:
                csv_writer = csv.writer(handler)
                csv_writer.writerows(result)

        except NameError as e:
            logging.exception(
                'running_process.py Failure: ' + str(e.message))
            sys.exit(1)
        except Exception, e:
            logging.exception(
                'running_process.py Failure: ' + str(e.message))
            sys.exit(1)
