from pprint import pprint

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
            "CON": self.con,
            "LAB": self.lab,
            "LD": self.ld,
            "RUK": self.ruk,
            "GRN": self.green,
            "SNP": self.snp,
            "PC": self.pc,
            "DUP": self.dup,
            "SF": self.sf,
            "SDLP": self.sdlp,
            "UUP": self.uup,
            "APNI": self.apni,
            "IND": self.ind,
            "OTHER": self.other
        }
        self.votes = dict(sorted(self.votes.items(), key=lambda item: item[1], reverse=True))
        self.total_votes = con + lab + ld + ruk + green + snp + pc + dup + sf + sdlp + uup + apni + ind + other

    def remove_lower_percentile(self, factor):
        print("> Applying filter...")
        self.remaining_parties = {}
        self.extra_votes = {}
        for k, v in self.votes.items():
            if v >= self.total_votes * int(factor)/100:
                self.remaining_parties[k] = v
            elif not v == 0:
                self.extra_votes[k] = v
        print(f"\n--- Remaining parties:\n--- {self.remaining_parties}")
        print(f"--- Extra votes:\n--- {self.extra_votes}\n")
        
    
    def redistribute_votes(self, mapping):
        if self.extra_votes == 0:
            raise Exception("No votes to redistribute - please use remove_lower_percentile()")


    def __repr__(self):
        return f"{self.name} - Party: {next(iter(self.votes))} ({self.mp})"

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
            if constituency.name == constituency_str:
                print(f"\n=== {constituency.name.upper()} ===")
                pprint(constituency.votes, sort_dicts=False)
                print("")
                return constituency
        raise Exception("Constituency not found") 
            
    def get_all_constituencies(self):
        if self.constituencyrepo == []:
            raise Exception("No data in repo - please use load_data()")
        return self.constituencyrepo
