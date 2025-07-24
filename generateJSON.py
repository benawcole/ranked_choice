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
    results_file_path = "./2024-results-adjusted.xlsx"
    mapping_file_path = "./Mapping Proposal 1.xlsx"

load_voter_data(results_file_path)
load_mapping_data(mapping_file_path)

def check_threshold_percentage(constituency, threshold_percent):
    new_threshold_percent = threshold_percent
    while constituency.minimum_percentage >= new_threshold_percent:
        new_threshold_percent += threshold_percent
        print(f"Threshold percentage for {constituency.name}'s Round {constituency.knockout_counter + 1} is too low. New threshold: {new_threshold_percent}%.")
    while constituency.maximum_percentage <= new_threshold_percent:
        new_threshold_percent -= threshold_percent
        print(f"Threshold percentage for {constituency.name}'s Round {constituency.knockout_counter + 1} is too high. New threshold: {new_threshold_percent}%.")
    return new_threshold_percent

def threshold_percent_simulation():
    threshold_percent = float(input("Increase threshold percentage by increments of:   %" + "\b"*3))
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

def loser_knockout_simulation():
    country = {}
    for c in constituencies.constituencyrepo:
        if c.check_for_winner():
            c.save_round_to_payload(bumper=1)
        while not c.check_for_winner():
            c.knockout_loser()
            c.redistribute_votes(mapping_df)
            c.save_round_to_payload()
        country[c.name] = c.info

def generate_JSON(constituencies):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(country, f, ensure_ascii=False, indent=4)

def generate_CSV(constituencies):
    rows = []
    for c in constituencies.constituencyrepo:
        first_party = next(iter(c.sorted_votes))
        for party, votes in c.votes.items():
            rows.append({
                "Constituency Name": c.name,
                "MP Name": c.mp,
                "Country": c.country,
                "Party": party,
                "Votes": votes,
                "Total Votes": c.total_votes,
                "Knockout Round": c.knockout_counter,
                "Filtered":c.filtered,
                "First Party": first_party
            })
    return pd.DataFrame(rows)







loser_knockout_simulation()

df = generate_df(constituencies)
df.to_csv("tableau_export.csv", index=False)