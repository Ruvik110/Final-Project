import pandas as pd
import re
from rapidfuzz import process, fuzz

#read files
london = pd.read_csv(r'C:\Users\lenovo\Downloads\dataverse_files (4)\lndn1866_01.csv', sep='\t', engine='python', encoding='utf-8')
subset = pd.read_csv('subset_with_occupation.csv', encoding='utf-8')

#preprocess
def normalize(txt):
    if pd.isna(txt):
        return ''
    s = txt.strip().lower()
    return re.sub(r'[^a-z0-9\s]', '', s)

london['occ_clean'] = london['occupation'].apply(normalize)
subset['occ_clean'] = subset['occupation'].apply(normalize)

choices = london['occ_clean'].tolist()
hisco_map = dict(zip(london['occ_clean'], london['hisco']))

#RapidFuzz match
def match_to_hisco(occ, threshold=75):
    if not occ:
        return None
    res = process.extractOne(
        query=occ,
        choices=choices,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold
    )
    if res:
        match_str, score, idx = res
        return hisco_map.get(match_str)
    return None

#apply and generate new column
subset['matched_hisco'] = subset['occ_clean'].apply(lambda x: match_to_hisco(x, threshold=70))

#check
total = len(subset)
matched = subset['matched_hisco'].notna().sum()
print(f"Total: {total},success ：{matched}")

#save
subset.to_csv('subset_with_hisco_fuzzy.csv', index=False, encoding='utf-8')
print("subset_with_hisco_fuzzy.csv")
