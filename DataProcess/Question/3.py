import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\imprison_filled_correct.csv')

#extract guilty
bands = ['theftunder5s', 'theftunder40s', 'theftunder1s', 'theftunder100s']
df_theft = df[(df['verdict_category'] == 'guilty') &
              (df['verdict_subcategory'].isin(bands))]

#compute by band
avg_sent = (df_theft
            .groupby('verdict_subcategory')['sentence_years']
            .mean()
            .reindex(bands))

#plot
plt.figure(figsize=(6,4))
avg_sent.plot(kind='bar', color='orange', edgecolor='black')
plt.xlabel('Value Band')
plt.ylabel('Average Sentence (years)')
plt.title('Average Sentence by Theft Value Band (Guilty Verdict)')
plt.xticks(rotation=45, ha='right')
plt.ylim(0, avg_sent.max() * 1.1)
for idx, val in enumerate(avg_sent):
    plt.text(idx, val + 0.02, f"{val:.2f}", ha='center')
plt.tight_layout()
plt.show()
