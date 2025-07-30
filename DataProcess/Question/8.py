import pandas as pd
import matplotlib.pyplot as plt

#read
hab_df = pd.read_csv(r'D:\PY\FinalProject\1\habitual_offenders_with_sequence.csv', dtype={'trial_id': str})
imp_df = pd.read_csv(r'D:\PY\FinalProject\1\imprison_filled_correct.csv',    dtype={'trial_id': str})

#merge
merged = pd.merge(
    hab_df,
    imp_df[['trial_id', 'sentence_years']],
    on='trial_id',
    how='left'
)

merged = merged[merged['sentence_years'].notna()]
#save
out_path = r'D:\PY\FinalProject\1\merged_habitual_sentence.csv'
merged.to_csv(out_path, index=False)
print(f"Merged dataset saved to: {out_path}")

#mark
merged['offender_type'] = merged['offense_number'].astype(int) \
                            .apply(lambda x: 'First-time' if x == 1 else 'Habitual')

#compute
avg_sentence = (
    merged
    .groupby('offender_type')['sentence_years']
    .mean()
    .reindex(['First-time', 'Habitual'])     # 保证顺序
    .reset_index()
)

#plot
plt.figure(figsize=(6, 4))
plt.bar(avg_sentence['offender_type'],
        avg_sentence['sentence_years'],
        color=['#4E79A7', '#E15759'])

plt.ylabel('Average Sentence (years)')
plt.ylim(0, avg_sentence['sentence_years'].max() * 1.15)
plt.title('Average Sentence Length: First‑time vs Habitual Offenders')

for i, v in enumerate(avg_sentence['sentence_years']):
    plt.text(i, v + 0.02 * avg_sentence['sentence_years'].max(),
             f"{v:.2f}", ha='center')

plt.tight_layout()
plt.show()
