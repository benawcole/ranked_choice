import pandas as pd
import platform

# Load the Excel file
if platform.system() == "Windows":
    file_path = 'D:\Documents\Python\Ranked Choice Voting\HoC-GE2024-results-by-constituency.xlsx'
if platform.system() == "Darwin":
    file_path = '/Users/benawcole/Desktop/Ranked Choice/HoC-GE2024-results-by-constituency.xlsx'
excel_data = pd.ExcelFile(file_path)

# Load the data from the relevant sheet
df = excel_data.parse('Data')
print(df)

# Define party columns
parties = [
    'Con', 'Lab', 'LD', 'RUK', 'Green',
    'SNP', 'PC', 'DUP', 'SF',
    'SDLP', 'UUP', 'APNI',
    'Winner if IND or other', 'All other candidates'
]

# Preserve original valid votes from the dataset
df['Valid votes (Original)'] = df['Valid votes']

# Create columns for redistributed votes
for party in parties:
    df[party + ' (Redistributed)'] = df[party]

# Define the political orientation and alignment of each party
party_orientation = {
    'Con': 'Right',
    'Lab': 'Left',
    'LD': 'Center',
    'Green': 'Left',
    'SNP': 'Left',
    'PC': 'Left',
    'DUP': 'Right',
    'SF': 'Left',
    'SDLP': 'Left',
    'UUP': 'Right',
    'APNI': 'Center',
    'RUK': 'Right',
    'Winner if IND or other': 'Center',
    'All other candidates': 'Not Applicable'
}

party_alignment = {
    'Con': 'Not Applicable',
    'Lab': 'Not Applicable',
    'LD': 'Not Applicable',
    'Green': 'Not Applicable',
    'SNP': 'Nationalist',
    'PC': 'Nationalist',
    'DUP': 'Unionist',
    'SF': 'Nationalist',
    'SDLP': 'Nationalist',
    'UUP': 'Unionist',
    'APNI': 'Not Applicable',
    'RUK': 'Not Applicable',
    'Winner if IND or other': 'Not Applicable',
    'All other candidates': 'Not Applicable'
}

# Elimination criteria for parties
elimination_criteria = 10  # 5%


def create_dynamic_redistribution_map(row, remaining_parties):
    redistribution_map = {}

    # List of ONS IDs with custom alignment/orientation overrides
    left_override_ids = ['E14001102', 'E14001196', 'E14001327', 'E14001098', 'E14001305']
    unionist_override_ids = ['N05000013']

    # Get the ONS ID for the current row
    ons_id = row['ONS ID']  # Assuming the 'ONS ID' column exists in the dataframe

    # Create stock arrays to count remaining parties by alignment and orientation
    alignment_counts = {
        'Unionist': len([p for p in remaining_parties if party_alignment[p] == 'Unionist']),
        'Nationalist': len([p for p in remaining_parties if party_alignment[p] == 'Nationalist']),
        'Not Applicable': len([p for p in remaining_parties if party_alignment[p] == 'Not Applicable']),
    }

    orientation_counts = {
        'Left': len([p for p in remaining_parties if party_orientation[p] == 'Left']),
        'Center': len([p for p in remaining_parties if party_orientation[p] == 'Center']),
        'Right': len([p for p in remaining_parties if party_orientation[p] == 'Right']),
        'Not Applicable': len([p for p in remaining_parties if party_orientation[p] == 'Not Applicable']),
    }

    for party in parties:
        if row[party + ' %'] < elimination_criteria:
            redistribution_map[party] = {}

            # Override alignment/orientation for specific ONS IDs
            if ons_id in left_override_ids:
                party_align = 'Not Applicable'
                party_orient = 'Left'
            elif ons_id in unionist_override_ids:
                party_align = 'Unionist'
                party_orient = 'Not Applicable'
            else:
                # Default alignment/orientation logic
                party_align = party_alignment[party]
                party_orient = party_orientation[party]

            # Step 1: Redistribute based on alignment, but skip if alignment = 'Not Applicable'
            if party_align != 'Not Applicable' and party_align in alignment_counts and alignment_counts[
                party_align] > 0:
                alignment_share = 1.0 / alignment_counts[party_align]
                for target_party in remaining_parties:
                    if party_alignment[target_party] == party_align:
                        redistribution_map[party][target_party] = alignment_share
                continue  # Skip to the next party if alignment redistribution is done

            # Step 2: If no aligned parties, redistribute based on orientation
            if party_orient in orientation_counts and orientation_counts[party_orient] > 0:
                orientation_share = 1.0 / orientation_counts[party_orient]
                for target_party in remaining_parties:
                    if party_orientation[target_party] == party_orient:
                        redistribution_map[party][target_party] = orientation_share
                continue  # Skip to the next party if orientation redistribution is done

            # Step 3: If alignment and orientation have no matches, redistribute equally
            num_remaining = len(remaining_parties)
            for target_party in remaining_parties:
                redistribution_map[party][target_party] = 1.0 / num_remaining

    return redistribution_map


def calculate_initial_percentages(df):
    """
    This function ensures that the initial percentages for each party are calculated
    based on the existing vote counts.
    """
    for party in parties:
        if f'{party} %' not in df.columns:
            df[party + ' %'] = df[party] / df['Valid votes'] * 100
    return df


def redistribute_votes(row, remaining_parties):
    """
    Redistribute the votes for knocked-out parties to the remaining parties
    based on their alignment or orientation.
    """
    redistribution_map = create_dynamic_redistribution_map(row, remaining_parties)

    for party in parties:
        if row[party] == 0:  # Check if this party has been eliminated
            if party not in redistribution_map or not redistribution_map[party]:
                print(f"Warning: No redistribution map for {party}")
                continue  # Skip if no valid redistribution map exists for this party
            for target_party, proportion in redistribution_map[party].items():
                row[target_party] += row[party + ' (Redistributed)'] * proportion  # Add redistributed votes
            row[party + ' (Redistributed)'] = 0  # Set eliminated party's votes to 0

    return row


def track_majority(df, round_label):
    """
    This function tracks the party with the highest votes after each round
    and checks if that party has a majority (i.e., more than 50% of valid votes).
    """
    df[f'Majority ({round_label})'] = df[[party + f' % ({round_label})' for party in parties]].max(axis=1) > 50
    return df


def perform_redistribution(df):
    # Step 1: Calculate initial percentages if they don't exist
    df = calculate_initial_percentages(df)

    # Track initial majority before redistribution
    df['Majority (Before Round 1)'] = df[[party + ' %' for party in parties]].max(axis=1) > 50

    # First round: Eliminate parties under 5% and redistribute votes
    for index, row in df.iterrows():
        if any(row[party + ' %'] > 50 for party in parties):
            continue  # Skip if majority already exists
        remaining_parties = [party for party in parties if row[party + ' %'] >= elimination_criteria]
        row = redistribute_votes(row, remaining_parties)
        df.loc[index] = row

    # Recalculate percentages and votes after first redistribution (Round 1)
    for party in parties:
        df[party + ' (Votes Round 1)'] = df[party + ' (Redistributed)']  # Store the new vote counts
        df[party + ' % (Round 1)'] = df[party + ' (Votes Round 1)'] / df['Valid votes'] * 100

    # Track whether a majority is found after Round 1
    df = track_majority(df, 'Round 1')

    # Second round: Knock out the smallest remaining party and redistribute votes
    for index, row in df.iterrows():
        if any(row[party + ' % (Round 1)'] > 50 for party in parties):
            continue  # Skip if majority exists after Round 1
        remaining_parties = [party for party in parties if row[party + ' % (Round 1)'] > 0]
        smallest_party = min(remaining_parties, key=lambda p: row[p + ' (Votes Round 1)'])
        row[smallest_party] = 0  # Eliminate the smallest party
        remaining_parties = [party for party in parties if row[party] > 0]  # Update remaining parties
        row = redistribute_votes(row, remaining_parties)  # Redistribute the votes
        df.loc[index] = row

    # Recalculate percentages and votes after second redistribution (Round 2)
    for party in parties:
        df[party + ' (Votes Round 2)'] = df[party + ' (Redistributed)']  # Store the new vote counts
        df[party + ' % (Round 2)'] = df[party + ' (Votes Round 2)'] / df['Valid votes'] * 100

    # Track whether a majority is found after Round 2
    df = track_majority(df, 'Round 2')

    return df


# Example call to the function
df = perform_redistribution(df)

# Save the modified DataFrame to a new Excel file
output_file_path = 'D:\Documents\Python\Ranked Choice Voting\HoC-GE2024-results-with-redistribution.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Redistributed election results saved to {output_file_path}")