from pprint import pprint
import pandas as pd

class Constituency:
    def __init__(self, id, name, country, mp, con, lab, ld, ruk, green, snp, pc, dup, sf, sdlp, uup, apni, ind, other):
        self.id = id
        self.name = name
        self.country = country
        self.mp = mp
        self.con = int(con)
        self.lab = int(lab)
        self.ld = int(ld)
        self.ruk = int(ruk)
        self.green = int(green)
        self.snp = int(snp)
        self.pc = int(pc)
        self.dup = int(dup)
        self.sf = int(sf)
        self.sdlp = int(sdlp)
        self.uup = int(uup)
        self.apni = int(apni)
        self.ind = int(ind)
        self.other = int(other) #All other votes 2
        self.votes = {
            "Con": self.con,
            "Lab": self.lab,
            "LD": self.ld,
            "RUK": self.ruk,
            "Green": self.green,
            "SNP": self.snp,
            "PC": self.pc,
            "DUP": self.dup,
            "SF": self.sf,
            "SDLP": self.sdlp,
            "UUP": self.uup,
            "APNI": self.apni,
            "Ind": self.ind,
            "Other": self.other
        }
        self.total_votes = int(con + lab + ld + ruk + green + snp + pc + dup + sf + sdlp + uup + apni + ind + other)
        self.knockout_counter = 0
        self.filtered = False
        self.payload = {}
        self.input_percent = 0
        self.new_total_votes = self.total_votes
        self.save_round_to_payload(0)
    
    @property
    def info(self):
        return {"name":self.name,
                "country":self.country,
                "mp":self.mp,
                "votes": self.payload}

    @property
    def sorted_votes(self):
        return dict(sorted(self.votes.items(), key=lambda item: item[1], reverse=True))

    @property
    def minimum_percentage(self):
        d = {k: v for k, v in self.sorted_votes.items() if v > 0}
        return round(d[next(reversed(d))]*100/self.total_votes, 2)

    @property
    def maximum_percentage(self):
        d = {k: v for k, v in self.sorted_votes.items() if v > 0}
        return round(d[next(iter(d))]*100/self.total_votes, 2)

    def save_round_to_payload(self, bumper=0):
        self.payload[self.knockout_counter + bumper] = {  
            "maximum_percentage":self.maximum_percentage, #N.B. The thresholds for the FOLLOWING round
            "minimum_percentage":self.minimum_percentage,
            "input_percentage":self.input_percent,
            "votes":self.sorted_votes,
            "margin_of_error":abs(self.new_total_votes-self.total_votes)}

    def check_for_winner(self):
        print("NEXT ITER:" + f"{next(iter(self.sorted_votes.values()))}")
        if next(iter(self.sorted_votes.values())) > 0.5 * self.new_total_votes:
            self.filtered = True
        return self.filtered

    def remove_lower_percentile(self, percent):
        self.input_percent = percent
        if not self.check_for_winner():
            self.knockout_counter += 1
            self.remaining_votes = {k: 0 for k, v in self.sorted_votes.items()}
            self.extra_votes = {k: 0 for k, v in self.sorted_votes.items()}
            for k, v in self.sorted_votes.items():
                if v >= self.total_votes * float(percent)/100:
                    self.remaining_votes[k] = v
                else:
                    self.extra_votes[k] = v

    def knockout_loser(self):
        self.check_for_winner()
        if not self.filtered:
            non_zero_votes = {k: v for k, v in self.votes.items() if v > 0}
            loser = min(non_zero_votes, key=non_zero_votes.get)
            self.extra_votes = {loser: non_zero_votes[loser]}
            self.remaining_votes = {k: v for k, v in non_zero_votes.items() if k != loser}
            self.knockout_counter += 1
        else:
            print("else")

    # def redistribute_votes(self, mapping_df):
    #     if self.check_for_winner():
    #         return
    #     # if self.extra_votes == {k: 0 for k, v in self.sorted_votes.items()}:
    #     #     raise Exception("No votes to redistribute - please increase the threshold percentage")
    #     summing_df = mapping_df.copy()
    #     # Turn all columns of extra parties to 0
    #     for k, v in self.remaining_votes.items():
    #         if v == 0:
    #             summing_df[k] = 0
    #     # Calculate redistribution of extra votes to non-0 parties
    #     for k, v in self.extra_votes.items():
    #         total_row = summing_df.loc[k].sum()
    #         for column in mapping_df:
    #             result = v * (summing_df.loc[k, column] / total_row)
    #             if result != 0 and not pd.isna(result):
    #                 summing_df.loc[k, column] = round(result, 0)
    #             elif summing_df.loc[k, column] == mapping_df.loc[k, column]:
    #                 summing_df.loc[k, column] = 0
    #     # add Total at the bottom
    #     df_sum = summing_df.sum()
    #     summing_df.loc["Total"] = df_sum
    #     # add to winners' total
    #     self.new_total_votes = 0
    #     for k, v in self.remaining_votes.items():
    #         self.remaining_votes[k] = v + int(summing_df.loc["Total", k])
    #         self.new_total_votes += v + int(summing_df.loc["Total", k])
    #     self.votes = self.remaining_votes
    #     self.check_for_winner()
    #     self.save_round_to_payload()
    #     return summing_df

    def redistribute_votes(self, mapping_df):
        if self.check_for_winner():
            return
        summing_df = mapping_df.copy()

        # Ensure only parties still in the game can receive votes
        active_parties = [k for k, v in self.remaining_votes.items() if v > 0]

        # Zero out columns for eliminated parties in summing_df
        for party in summing_df.columns:
            if party not in active_parties:
                summing_df[party] = 0

        # Start redistributing
        for eliminated_party, votes_to_distribute in self.extra_votes.items():
            if votes_to_distribute == 0:
                continue

            # Get only the columns for active parties
            redistribution_row = summing_df.loc[eliminated_party, active_parties]

            total_weight = redistribution_row.sum()
            if total_weight == 0:
                print(f"⚠️ Warning: No redistribution mapping defined for '{eliminated_party}'. Skipping redistribution.")
                continue

            # Calculate redistribution without rounding yet
            redistributed = {}
            for recipient in active_parties:
                proportion = summing_df.loc[eliminated_party, recipient] / total_weight
                redistributed[recipient] = votes_to_distribute * proportion

            # Round while preserving the total using a trick
            rounded = {}
            cumulative = 0
            for recipient in active_parties:
                rounded[recipient] = int(round(redistributed[recipient]))
                cumulative += rounded[recipient]

            diff = cumulative - int(votes_to_distribute)
            if diff != 0:
                # Adjust for rounding error by subtracting from the largest bucket
                sorted_parties = sorted(rounded.items(), key=lambda x: -x[1])
                for recipient, _ in sorted_parties:
                    if diff == 0:
                        break
                    if rounded[recipient] > 0:
                        rounded[recipient] -= 1
                        diff -= 1

            # Apply the rounded redistribution
            for recipient in active_parties:
                summing_df.loc[eliminated_party, recipient] = rounded[recipient]

        # Add totals
        df_sum = summing_df.loc[self.extra_votes.keys()].sum()
        summing_df.loc["Total"] = df_sum

        # Update votes and totals
        self.new_total_votes = 0
        for party in active_parties:
            self.remaining_votes[party] += int(summing_df.loc["Total", party])
            self.new_total_votes += self.remaining_votes[party]

        self.votes = self.remaining_votes
        self.check_for_winner()
        self.save_round_to_payload()

        return summing_df

    def __str__(self):
        return f"{self.name} - Party: {next(iter(self.sorted_votes))} ({self.mp})"

class ConstituencyRepo:
    def __init__(self):
        self.constituencyrepo = []

    def load_data(self, df):
        i = 0
        while i < len(df):
            constituency = Constituency(
                                i, 
                                df["Constituency name"][i],
                                df["Country name"][i],
                                f"{df["Member first name"][i]} {df["Member surname"][i]}",
                                df["Party - Con"][i],
                                df["Party - Lab"][i],
                                df["Party - LD"][i],
                                df["Party - RUK"][i],
                                df["Party - Green"][i],
                                df["Party - SNP"][i],
                                df["Party - PC"][i],
                                df["Party - DUP"][i],
                                df["Party - SF"][i],
                                df["Party - SDLP"][i],
                                df["Party - UUP"][i],
                                df["Party - APNI"][i],
                                df["Party - Winner if IND or other"][i],
                                df["Party - All other candidates 2"][i])
            self.constituencyrepo.append(constituency)
            i += 1
        print(f"> Dataframe loaded to Repo\n")
    
    def sort_by_country(self):
        self.england = []
        for constituency in self.constituencyrepo:
            if constituency.country == "England":
                self.england.append(constituency)
        self.scotland = []
        for constituency in self.constituencyrepo:
            if constituency.country == "Scotland":
                self.scotland.append(constituency)
        self.wales = []
        for constituency in self.constituencyrepo:
            if constituency.country == "Wales":
                self.wales.append(constituency)
        self.northern_ireland = []
        for constituency in self.constituencyrepo:
            if constituency.country == "Northern Ireland":
                self.northern_ireland.append(constituency)
        print(f"> Data sorted by country")

    def get_single_constituency(self, constituency_str):
        if self.constituencyrepo == []:
            raise Exception("No data in repo - please use load_data()")
        for constituency in self.constituencyrepo:
            if constituency.name.lower() == constituency_str.lower():
                return constituency
        raise Exception("Constituency not found") 

    def print_single_constituency(self, constituency_str):
        if self.constituencyrepo == []:
            raise Exception("No data in repo - please use load_data()")    
        for constituency in self.constituencyrepo:    
            if constituency.name.lower() == constituency_str.lower():
                print(f"\n====== {str(constituency)} ======")
                pprint(constituency.sorted_votes, sort_dicts=False)
                print(f"\nTotal votes: {constituency.total_votes}\n")
        raise Exception("Constituency not found") 
   
    def get_all_constituencies(self):
        if self.constituencyrepo == []:
            raise Exception("No data in repo - please use load_data()")
        return self.constituencyrepo
