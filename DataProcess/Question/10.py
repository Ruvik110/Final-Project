import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')
df['year'] = pd.to_numeric(df['year'], errors='coerce').dropna().astype(int)
df = df[(df['year'] >= 1674) & (df['year'] <= 1913)]

#compute
total = df.groupby('year').size()
death = df['punishment_category'].str.lower().eq('death').groupby(df['year']).sum()
rate = (death / total * 100).fillna(0)

#plot
fig, ax = plt.subplots(figsize=(12, 6))
line_death, = ax.plot(
    rate.index, rate.values,
    color='orange', marker='o', markersize=4, linewidth=1.5,
    label='Death Sentence Rate'
)

#define
reforms = {
    1808: 'Romilly Act 1808',
    1823: 'Judgement of Death 1823',
    1832: 'The Punishment of Death, etc. Act 1832',
    1841: 'Substitution Act 1841',
    1868: 'Capital Punishment Amendment 1868'
}
colors = ['C1', 'C2', 'C3', 'C4', 'C5']

for (yr, label), color in zip(reforms.items(), colors):
    ax.axvline(
        yr, color=color, linestyle='--', linewidth=1.5,
        label=label
    )

#plot
ax.set_xlim(1674, 1913)
ax.set_ylim(0, rate.max() * 1.05)
ax.set_xlabel('Year')
ax.set_ylabel('Death Sentence Rate (%)')
ax.set_title('Annual Death Sentence Rate (1674–1913)\nwith Key Reform Movements')
ax.grid(alpha=0.3)

#legend
plt.legend()
# ax.legend(
#     loc='upper left',
#     bbox_to_anchor=(1.02, 1),
#     borderaxespad=0
# )

# plt.subplots_adjust(right=0.75)
plt.show()


