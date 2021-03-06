#! /usr/bin/env python
"""
mbed SDK
Copyright (c) 2019 ARM Limited
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
LIBRARIES BUILD
"""

# Script to automatically update the configuration parameters list in
# each configuration doc page with the output from `mbed compile --config -v`
# for the page's appropriate prefix.
#
# By default, when run from the check_tools directory, the script runs
# through each Markdown file in `docs/reference/configuration/`. An
# optional file or directory path may be passed in a parameter to run the
# script on a specific file or directroy outside the default path. 
#
# Note that you need to run this with a local copy of whichever version of
# Mbed OS you wish to update the configuration parameters with.
#
# You can run this script with:
# python config-update.py <OPTIONAL FILE/DIR PATH>

import sys, os
import re
import subprocess

def split_into_pairs(l):
    """ Split the provided list into a, b pairs.
        [1, 2, 3, 4] -> [[1, 2], [3, 4]]
    Args:
    l - list of values to be split

    Returns:
    List of split pairs
    """
    for i in range(0, len(l), 2):
        yield l[i:i + 2]

def main(file):
    file_h = open(file, 'r+')
    file   = file_h.read()

    # Collect indices of markdown code block ticks, split into start,end pairs
    # with `split_into_pairs` below. Collect the config parameter prefix used in
    # the current block if viable and replace the contents with the output of
    # the Mbed CLI config verbose list command.
    snippet_indices = [m.start() for m in re.finditer('```', file)]

    blocks = {}
    for i in range(0, int(len(snippet_indices) / 2)):
        # Need to rerun on every loop as the indices change each iteration
        snippet_indices = [m.start() for m in re.finditer('```', file)]
        ranges = list(split_into_pairs(snippet_indices))
        start  = ranges[i][0]
        end    = ranges[i][1]

        try:
            blocks[i] = file[start : end + 3]
            if ('Name: ' in blocks[i]):
                lib = blocks[i].split('Name: ')[1].split('.')[0]
                print("=================   %s   =================" % lib)
                out = str(subprocess.check_output(["mbed", "compile", "--config", "-v", "--prefix", lib]))
                file = file[:start+4] + out[:out.index("Macros") - 1] + file[end:]

        # Originally added for debugging purposes, catch and display exceptions before
        # continuing without exiting to provide a complete list of errors found
        except Exception as e:
            print("Error")
            print(e)
            print("____________________")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            pass

    file_h.truncate(0)
    file_h.seek(0)
    file_h.write(file)
    file_h.close()

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        path = '../docs/reference/configuration'
    else:
        path = sys.argv[1]

    if (path == '-h' or path == '--help'):
        print("By default the script runs out of the docs tools directory and iterates through reference/configuration.\n"
              "You may pass in a directory path that will run on all files contained within, or a single file path optionally.")
        exit(0)

    if (os.path.isfile(path)):
        main(path)
    elif (os.path.isdir(path)):
        for doc in os.listdir(path):
            if (doc != 'configuration.md'):
                print('_____ %s _____' % os.path.join(path, doc))
                main(os.path.join(path, doc))
    else:
        print("Please provide a valid file or directory path")
