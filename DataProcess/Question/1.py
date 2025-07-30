import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')

#year
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df = df[(df['year'] >= 1674) & (df['year'] <= 1913)]

#normalize
df['punishment_category'] = df['punishment_category'].str.lower().fillna('unknown')
df['is_death'] = (df['punishment_category'] == 'death').astype(int)

#annual
yearly = df.groupby('year')
total_cases = yearly.size()
death_cases = yearly['is_death'].sum()
death_rate = death_cases / total_cases * 100

plt.figure()
plt.plot(death_rate.index, death_rate.values)
plt.xlabel('Year')
plt.ylabel('Death Sentence Rate (%)')
plt.title('Annual Death Sentence Rate (1674–1913)')
plt.tight_layout()
plt.show()

#century
df['century'] = ((df['year'] - 1) // 100 + 1).astype(int)
century_group = df.groupby('century').agg(
    total_cases=('is_death', 'count'),
    death_cases=('is_death', 'sum')
)
century_group['death_rate'] = century_group['death_cases'] / century_group['total_cases'] * 100

plt.figure()
plt.plot(century_group.index, century_group['death_rate'], marker='o')
plt.xticks(century_group.index, [f"{c}th" for c in century_group.index])
plt.xlabel('Century')
plt.ylabel('Death Sentence Rate (%)')
plt.title('Death Sentence Rate by Century (1674–1913)')
plt.grid(True)
plt.tight_layout()
plt.show()

