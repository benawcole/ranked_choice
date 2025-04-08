import pandas as pd
import platform
import pprint
from ConstituencyClasses import *
import json

# Load the Excel files
def load_voter_data(file_path):
    # Load the data from the results
    results_excel_data = pd.ExcelFile(file_path)
    global results_df 
    results_df = results_excel_data.parse()
    global constituencies
    constituencies = ConstituencyRepo()
    constituencies.load_data(results_df)

def load_mapping_data(file_path):
    # Load the data from the mapping proposal
    mapping_excel_data = pd.ExcelFile(file_path)
    global mapping_df
    mapping_df = mapping_excel_data.parse()
    mapping_df.index = ['Con', 'Lab', 'LD', 'RUK', 'Green', 'SNP', 'PC', 'DUP', 'SF', 'SDLP', 'UUP', 'APNI', 'Ind', 'Other']

if platform.system() == "Windows":
    results_file_path = r'D:\Documents\Python\Ranked Choice Voting\2024-results-adjusted.xlsx'
    mapping_file_path = "" #JOHN FILL THIS IN
if platform.system() == "Darwin":
    results_file_path = "/Users/benawcole/Desktop/Ranked Choice/2024-results-adjusted.xlsx"
    mapping_file_path = "/Users/benawcole/Desktop/Ranked Choice/Mapping Proposal 1.xlsx"

load_voter_data(results_file_path)
load_mapping_data(mapping_file_path)

threshold_percent = float(input("Increase threshold percentage by increments of:   %" + "\b"*3))

def check_threshold_percentage(constituency, threshold_percent):
    while constituency.minimum_percentage > threshold_percent:
        threshold_percent += threshold_percent
        print(f"Threshold percentage for {constituency.name}'s Round {constituency.knockout_counter + 1} is too low. Doubling to {threshold_percent}.")
    while constituency.maximum_percentage < threshold_percent:
        threshold_percent -= threshold_percent
        print(f"Threshold percentage for {constituency.name}'s Round {constituency.knockout_counter + 1} is too low. Doubling to {threshold_percent}.")

constituencyOBJ = {}
for c in constituencies.constituencyrepo:
    constituency = constituencies.get_single_constituency(c.name)
    p = constituency.minimum_percentage
    print(constituency.name, constituency.minimum_percentage)
    if constituency.check_for_winner():
        constituency.add_to_payload(bumper=1)
    while not constituency.check_for_winner():
        check_threshold_percentage(constituency, threshold_percent)
        constituency.remove_lower_percentile(threshold_percent)
        constituency.redistribute_votes(mapping_df)
        constituency.save_round_to_payload()
    constituencyOBJ[constituency.name] = constituency.info

constituencyJSON = json.dumps(constituencyOBJ)
print(constituencyJSON)