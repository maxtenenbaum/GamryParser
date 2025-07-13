# This is an example for how you would set up an aging study
# All outputs for the project should be directed to the ./raw_outputs folder

# This script will watch for new files in the folder,
# process them as they hit the folder, update a batch dataframe,
# and update a Streamlit application for live updates

import sys
import os
sys.path.append(os.path.abspath(".."))
from gamryparser import Parser

# Find files in raw data folder
raw_outputs_dir = "example_project/raw_outputs"
files = [os.path.join(raw_outputs_dir, file) for file in os.listdir(raw_outputs_dir)]

# Run batch processor from GamryParser
all_data = Parser.batch_dta(files)

# Output an aggregate .csv for each experiment to ./processed_outputs
for exp in all_data.keys():
    all_data[exp].to_csv(f"example_project/processed_outputs/{exp}.csv")

