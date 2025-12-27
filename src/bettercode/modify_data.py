# code for datalad example

import pandas as pd
import sys

assert len(sys.argv) == 2, "Usage: python modify_data.py <path_to_demographics_csv>"

# remove Motivation variables from demographics.csv
df = pd.read_csv(sys.argv[1])
df = df.loc[:, ~df.columns.str.contains('Motivation')]
df.to_csv(sys.argv[1], index=False)