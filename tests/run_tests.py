# This file works for MacOS and Linux, please add the sys.path to run it using Windows
# Run the fule from the HotelRecommendationSystem directory

import glob
import subprocess
import os, sys

# Get a list of all test_*.py files in the tests directory
# Run this from the src
test_files = glob.glob('tests/test_*.py')
print(test_files)

# Run coverage for each file
for file in test_files:
    command = f'coverage run -m pytest -q {file}'
    subprocess.run(command, shell=True)

    # Display the coverage report
    file_tested = file.split('test_')[1]
    command = f'coverage report --show-missing --include=src/{file_tested} --omit=/tests/'
    subprocess.run(command, shell=True)