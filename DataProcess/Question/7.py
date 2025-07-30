import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\subset_with_hisco_classified.csv', dtype={'matched_hisco_str': str})

#filter
df = df[df['hisclass'] != -1]

#define and map
def map_social_group(hc):
    if hc in [1, 2]:
        return 'Upper Class'
    elif hc in [3, 4, 5, 6]:
        return 'Middle Class'
    else:
        return 'Lower Class'

df['social_group'] = df['hisclass'].apply(map_social_group)

#keep category
keep_cats = {'death', 'transport', 'imprison', 'corporal', 'miscpunish'}
df = df[df['punishment_category'].isin(keep_cats)]

#compute rate
prop_df = (
    df
    .groupby(['social_group', 'punishment_category'])
    .size()
    .groupby(level=0, group_keys=False)
    .apply(lambda x: x / x.sum())
    .reset_index(name='proportion')
)

pivot = prop_df.pivot(
    index='social_group',
    columns='punishment_category',
    values='proportion'
).fillna(0)

pivot = pivot[['death', 'transport', 'imprison', 'corporal', 'miscpunish']]

#plot
ax = pivot.plot(
    kind='bar',
    stacked=True,
    figsize=(8,5),
    colormap='tab20'
)
ax.set_ylabel('Proportion')
ax.set_xlabel('Social Group')
ax.set_title('Proportion of Punishment Categories by Social Group\n(Excluding noPunish/Unknown/notguilty)')
ax.legend(title='Punishment Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
