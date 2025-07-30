import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#read and filter
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')
df_nc = df[df['punishment_category'].str.lower() != 'death']

#filter
pattern = r'not\s*guilty|no\s*punish|unknown'
mask = df_nc['punishment_category'].str.lower().str.contains(pattern, na=False)
df_nc = df_nc[~mask]
df_nc = df_nc[df_nc['offence_category'].str.lower() != 'unknown']

pivot = df_nc.groupby(['offence_category', 'punishment_category']) \
             .size().unstack(fill_value=0)

#standardize
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

#plot
ax = pivot_pct.plot.barh(stacked=True, figsize=(10, 6))
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('Cases (%)')
plt.ylabel('Offence Category')
plt.title('Proportion of Non-Capital Punishments by Offence Category\n(excluding Not Guilty, NoPunish, Unknown, and Unknown Offences)')
plt.legend(title='Punishment Category', bbox_to_anchor=(1.0, 1.0))
plt.tight_layout()
plt.show()


