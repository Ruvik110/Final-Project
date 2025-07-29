import pandas as pd

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')

#extract
df_with_occ = df[df['occupation'].notna() & (df['occupation'] != 'unknown')].copy()

#check
print(f"Total {len(df_with_occ)} ")
print(df_with_occ[['trial_id','defendant_id','defendant_name','occupation']].head())

#save
df_with_occ.to_csv('subset_with_occupation.csv', index=False)
