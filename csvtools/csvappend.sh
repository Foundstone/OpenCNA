#!/bin/sh

# Example: 
# $ csvappend.sh first_file.csv second_file.csv
# Assuming that second_file.csv only has a header and one row, this script appends the second_file.csv to every row of first_file.csv
# Useful, for instance, to add the "OS_name" and "OS_version"

{ head -1 $2; yes `head -2 $2 | tail -1` | head -`wc -l $1 | awk '{print $1-1}'`; } > /tmp/temp_csv_replicated.csv
csvjoin $1 /tmp/temp_csv_replicated.csv
