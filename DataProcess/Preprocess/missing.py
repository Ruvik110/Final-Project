import pandas as pd

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\output14.csv')

#initial deduplication
df.drop_duplicates(inplace=True)

#normalize missing-value indicators
df.replace(['', ' ', 'nan', 'NaN'], pd.NA, inplace=True)

#fill and flag offence
for col in ['offence_category', 'offence_subcategory']:
    df[col] = df[col].fillna('unknown')
    df[f'{col}_missing'] = df[col] == 'unknown'

#occupation
df['occupation'] = df['occupation'].fillna('unknown')
df['occ_missing'] = df['occupation'] == 'unknown'

#gender & defendant_name
for col in ['gender', 'defendant_name']:
    df[col] = df[col].fillna('unknown')
    df[f'{col}_missing'] = df[col] == 'unknown'

#age
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df['age_missing'] = df['age'].isna()

#punishment_subcategory & verdict_subcategory
for col in ['punishment_subcategory', 'verdict_subcategory']:
    df[col] = df[col].fillna('unknown')
    df[f'{col}_missing'] = df[col] == 'unknown'

#verdict_category & punishment_category
df['verdict_category']    = df['verdict_category'].str.lower().fillna('unknown')
df['punishment_category'] = df['punishment_category'].str.lower().fillna('unknown')

mask_both_unknown = (
    (df['verdict_category'] == 'unknown') &
    (df['punishment_category'] == 'unknown')
)
df = df[~mask_both_unknown].copy()

#impute mode per year+offence for guilty, else 'notguilty'
mode_map = (
    df[df['verdict_category'] == 'guilty']
      .groupby(['year', 'offence_category'])['punishment_category']
      .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else 'unknown')
)
mask_missing_pun = df['punishment_category'].isna() | (df['punishment_category'] == 'unknown')
def impute_punishment(row):
    if row['verdict_category'] == 'guilty':
        return mode_map.get((row['year'], row['offence_category']), 'unknown')
    else:
        return 'notguilty'
df.loc[mask_missing_pun, 'punishment_category'] = (
    df.loc[mask_missing_pun].apply(impute_punishment, axis=1)
)
df['pun_cat_missing'] = df['punishment_category'].isna()

#impute verdict_category based on punishment_category for originally unknown verdicts
mask_verdict_unknown = df['verdict_category'] == 'unknown'
df.loc[mask_verdict_unknown, 'verdict_category'] = (
    df.loc[mask_verdict_unknown, 'punishment_category']
      .apply(lambda x: 'guilty' if x != 'notguilty' else 'notguilty')
)
df['ver_cat_missing'] = df['verdict_category'].isna()

#drop victim_name column
df.drop(columns=['victim_name'], inplace=True, errors='ignore')

#deduplication
df.drop_duplicates(inplace=True)

#save
df.to_csv('filled2_final.csv', index=False)



