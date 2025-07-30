import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')

#year
df['year'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce').dt.year

#start and end year
intro_year = 1718
transport_years = df.loc[df['punishment_category'].str.lower() == 'transport', 'year'].dropna().astype(int)
last_year = transport_years.max()

#filter
df = df[~df['punishment_category'].isin(['unknown', 'notguilty', 'nopunish'])]

def era_label(y):
    if y < intro_year:
        return 'Pre-transport'
    elif intro_year <= y <= last_year:
        return 'Transport era'
    else:
        return 'Post-transport'

df['era'] = df['year'].apply(era_label)

#compute
dist = df.groupby(['era', 'punishment_category']).size().unstack(fill_value=0)
dist_prop = dist.div(dist.sum(axis=1), axis=0)
dist_prop = dist_prop.reindex(['Pre-transport', 'Transport era', 'Post-transport'], fill_value=0)

#plot
eras = ['Pre-transport', 'Transport era', 'Post-transport']
categories = dist_prop.columns.tolist()
x = range(len(categories))
width = 0.25

plt.figure(figsize=(12, 5))
for i, era in enumerate(eras):
    plt.bar([j + (i-1)*width for j in x],
            dist_prop.loc[era],
            width,
            label=era)

plt.xticks(x, categories, rotation=45, ha='right')
plt.xlabel('Punishment Category')
plt.ylabel('Proportion of Cases')
plt.title(f'Punishment Distribution by Era\n(1718 introduction, last transport {last_year})')
plt.legend(title='Era')
plt.tight_layout()
plt.show()
