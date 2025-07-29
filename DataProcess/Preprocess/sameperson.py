import pandas as pd

#read
df = pd.read_csv('filled2_final.csv')

#filter verdict
df['verdict_category'] = df['verdict_category'].str.strip().str.lower().fillna('')
to_drop = {'miscverdict', 'notguilty', 'specialverdict'}
df = df[~df['verdict_category'].isin(to_drop)].copy()

df = df.dropna(subset=['surname', 'given', 'gender', 'age', 'year', 'date'])

#compute birth_year
df['year'] = df['year'].astype(int)
df['age']  = df['age'].astype(int)
df['birth_year'] = df['year'] - df['age']

#mark habitual
group_cols = ['surname', 'given', 'gender', 'birth_year']
date_counts = (
    df.groupby(group_cols)['date']
      .nunique()
      .reset_index(name='n_unique_dates')
)
df = df.merge(date_counts, on=group_cols, how='left')
df['is_habitual_offender'] = df['n_unique_dates'] > 1

#extract and sort
habitual = df[df['is_habitual_offender']].copy()
habitual['date'] = pd.to_datetime(habitual['date'], format='%Y%m%d', errors='coerce')
habitual = habitual.sort_values(
    by=['surname', 'given', 'birth_year', 'date']
).reset_index(drop=True)
habitual['date'] = habitual['date'].dt.strftime('%Y%m%d')

#save
habitual.to_csv('habitual_offenders_sorted.csv', index=False)

print("habitual_offenders_sorted.csv generated")
