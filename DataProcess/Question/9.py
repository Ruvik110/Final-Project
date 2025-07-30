import pandas as pd
import matplotlib.pyplot as plt

#load
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')

#year
df['year'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce').dt.year

#filter out non‑punishment
df = df[~df['punishment_category'].isin(['unknown', 'notguilty', 'nopunish'])]

#select punishment
cats = ['death', 'corporal', 'transport', 'imprison', 'miscpunish']

#compute annual counts & then proportions
yearly_counts = (
    df[df['punishment_category'].isin(cats)]
    .groupby(['year','punishment_category'])
    .size()
    .unstack(fill_value=0)[cats]
)
yearly_props = yearly_counts.div(yearly_counts.sum(axis=1), axis=0)

#plot
plt.figure(figsize=(10,5))
for cat in cats:
    plt.plot(yearly_props.index, yearly_props[cat], marker='o', label=cat)

#annotate the reform
reform_year = 1835
plt.axvline(reform_year, color='black', linestyle='--', linewidth=1, label='Prison Act 1835')

#labels & legend
plt.xlabel('Year')
plt.ylabel('Proportion of Cases')
plt.title('Annual Proportion of Punishment Types\n(Prison Act 1835 marked)')
plt.legend(loc='upper left',title='Punishment Category', bbox_to_anchor=(1.02, 1),borderaxespad=0)
plt.grid(True)
plt.tight_layout()
plt.show()
