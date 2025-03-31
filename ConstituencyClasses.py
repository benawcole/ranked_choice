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
    
    @property
    def sorted_votes(self):
        return dict(sorted(self.votes.items(), key=lambda item: item[1], reverse=True))

    def check_for_winner(self):
        if next(iter(self.sorted_votes.values())) > 0.5 * self.total_votes:
            self.filtered = True
            print(f"{next(iter(self.sorted_votes.keys()))} has >50% of the vote after {self.knockout_counter} rounds.\n")

    def remove_lower_percentile(self, percent):
        self.check_for_winner()
        if not self.filtered:
            self.remaining_votes = {k: 0 for k, v in self.sorted_votes.items()}
            self.extra_votes = {k: 0 for k, v in self.sorted_votes.items()}
            for k, v in self.sorted_votes.items():
                if v >= self.total_votes * int(percent)/100:
                    self.remaining_votes[k] = v
                else:
                    self.extra_votes[k] = v
            self.knockout_counter =+ 1
            return [self.remaining_votes, self.extra_votes]            
        
    def redistribute_votes(self, mapping_df):
        if self.extra_votes == {k: 0 for k, v in self.sorted_votes.items()}:
            raise Exception("No votes to redistribute - please increase the threshold percentage")
        summing_df = mapping_df.copy()
        # Turn all columns of extra parties to 0
        for k, v in self.remaining_votes.items():
            if v == 0:
                summing_df[k] = 0
        # Calculate redistribution of extra votes to non-0 parties
        for k, v in self.extra_votes.items():
            total_row = summing_df.loc[k].sum()
            for column in mapping_df:
                result = v * (summing_df.loc[k, column] / total_row)
                if result != 0 and not pd.isna(result):
                    summing_df.loc[k, column] = round(result, 0)
                elif summing_df.loc[k, column] == mapping_df.loc[k, column]:
                    summing_df.loc[k, column] = 0
        # add Total at the bottom 
        df_sum = summing_df.sum()
        summing_df.loc["Total"] = df_sum
        # add to winners' total
        self.new_total_votes = 0
        for k, v in self.remaining_votes.items():
            self.remaining_votes[k] = v + int(summing_df.loc["Total", k])
            self.new_total_votes += v + int(summing_df.loc["Total", k])
        self.votes = self.remaining_votes
        self.check_for_winner()
        return [{k: v for k, v in self.sorted_votes.items() if v > 0}, abs(self.total_votes - self.new_total_votes), summing_df]

    def __repr__(self):
        return f"{self.name} - Party: {next(iter(self.sorted_votes))} ({self.mp})"

class ConstituencyRepo:
    def __init__(self):
        self.constituencyrepo = []

    def load_data(self, df):
        i = 0
        while i < len(df):
            constituency = Constituency(i, 
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
                print(f"\n=== {str(constituency)} ===")
                pprint(constituency.sorted_votes, sort_dicts=False)
                print(f"\nTotal votes: {constituency.total_votes}\n")
                return constituency
        raise Exception("Constituency not found") 
            
    def get_all_constituencies(self):
        if self.constituencyrepo == []:
            raise Exception("No data in repo - please use load_data()")
        return self.constituencyrepo
