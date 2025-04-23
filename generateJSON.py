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
    new_threshold_percent = threshold_percent
    while constituency.minimum_percentage >= new_threshold_percent:
        new_threshold_percent += threshold_percent
        print(f"Threshold percentage for {constituency.name}'s Round {constituency.knockout_counter + 1} is too low. New threshold: {new_threshold_percent}%.")
    while constituency.maximum_percentage <= new_threshold_percent:
        new_threshold_percent -= threshold_percent
        print(f"Threshold percentage for {constituency.name}'s Round {constituency.knockout_counter + 1} is too high. New threshold: {new_threshold_percent}.")
    return new_threshold_percent

def generate_JSON(constituencies):
    country = {}

    for c in constituencies.constituencyrepo:
        if c.check_for_winner():
            c.save_round_to_payload(bumper=1)
        while not c.check_for_winner():
            new_threshold_percent = check_threshold_percentage(c, threshold_percent)
            c.remove_lower_percentile(new_threshold_percent)
            c.redistribute_votes(mapping_df)

            c.save_round_to_payload()
        country[c.name] = c.info

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(country, f, ensure_ascii=False, indent=4)


def generate_df(constituencies):
    country = {}

    for c in constituencies.constituencyrepo:
        if c.check_for_winner():
            c.save_round_to_payload(bumper=1)
        while not c.check_for_winner():
            new_threshold_percent = check_threshold_percentage(c, threshold_percent)
            c.remove_lower_percentile(new_threshold_percent)
            c.redistribute_votes(mapping_df)
            c.save_round_to_payload()
            
        country[c.name] = [
            self.con,
            self.lab,
            self.ld,
            self.ruk,
            self.green,
            self.snp,
            self.pc,
            self.dup,
            self.sf,
            self.sdlp,
            self.uup,
            self.apni,
            self.ind,
            self.other
        ]
    

# constituencyJSON = json.dumps(constituencyOBJ)
# print(constituencyJSON)