import pandas as pd
import platform
from pprint import pprint
from ConstituencyClasses import *

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

c = input("Enter constituency or ONS ID: ")
constituency = constituencies.get_single_constituency(c)
while not constituency.check_for_winner():
    # mapping = input(f"Please confirm the loaded mapping matrix:\n{mapping_file_path[2:]}\n\n{mapping_df}\n\n(Y/N): ")
    # if mapping.lower() == "y":
    #     while not constituency.check_for_winner():
    #         constituency.knockout_loser()
    #         print(  f"=== ROUND {constituency.knockout_counter} ===\n\n",
    #                 f"--- Remaining parties (Total - {sum(constituency.remaining_votes.values())}):\n    { {k: v for k, v in constituency.remaining_votes.items() if v > 0} }\n",
    #                 f"--- Extra votes (Total - {sum(constituency.extra_votes.values())}):\n    { {k: v for k, v in constituency.extra_votes.items() if v > 0} }")
    #         summing_df = constituency.redistribute_votes(mapping_df)
    #         print(  f"\n{summing_df}\n\n--- Redistributed votes:\n", 
    #                 f"\b--- { {k: v for k, v in constituency.sorted_votes.items() if v > 0} }",
    #                 f"   (± {abs(constituency.total_votes - constituency.new_total_votes)} votes)\n")   
    #     else:
    #         mapping_file_path = input("\nPlease load the relevant mapping matrix file path: ")
    #         load_mapping_data(mapping_file_path)
    # else:
    #     print(f"{next(iter(constituency.sorted_votes.keys()))} has {round((next(iter(constituency.sorted_votes.values()))/constituency.new_total_votes)*100, 1)}% of the vote after {constituency.knockout_counter} rounds.\n")
    #     pass
    mapping = input(f"Please confirm the loaded mapping matrix:\n{mapping_file_path[2:]}\n\n{mapping_df}\n\n(Y/N): ")
    if mapping.lower() == "y":
        while not constituency.check_for_winner():
            print(f"\n=== ROUND {constituency.knockout_counter + 1} ===")
            print(f"Current vote shares: {constituency.sorted_votes}")
            print(f"Top: {constituency.maximum_percentage}% | Bottom: {constituency.minimum_percentage}%\n")

            constituency.knockout_loser()
            print(f"Knocked out: {list(constituency.extra_votes.keys())[0]} with {list(constituency.extra_votes.values())[0]} votes")

            summing_df = constituency.redistribute_votes(mapping_df)
            constituency.save_round_to_payload()

            print(f"Redistribution matrix:\n{summing_df}\n")
            print(f"New votes: {constituency.sorted_votes}\n")
    else:
        mapping_file_path = input("\nPlease load the relevant mapping matrix file path: ")
        load_mapping_data(mapping_file_path)
