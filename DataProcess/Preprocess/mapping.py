import pandas as pd

#load
mapping_df = pd.read_csv('hisco_hisclass_mapping.csv', dtype={'hisco': str})
mapping_df['hisco'] = mapping_df['hisco'].str.strip().str.zfill(5)
mapping_dict = dict(zip(mapping_df['hisco'], mapping_df['hisclass']))

#load
df = pd.read_csv('subset_with_hisco_fuzzy.csv', dtype=str)

#preprocess
df['matched_hisco'] = pd.to_numeric(df['matched_hisco'], errors='coerce').astype('Int64')
df['matched_hisco_str'] = df['matched_hisco'].astype(str).str.zfill(5)

#match hisclass, otherwise -1
df['hisclass'] = (
    df['matched_hisco_str']
      .map(mapping_dict)
      .fillna(-1)
      .astype(int)
)

#save
df.to_csv('subset_with_hisco_classified.csv', index=False, encoding='utf-8')
print("subset_with_hisco_classified.csv generated")
