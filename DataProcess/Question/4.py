import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\imprison_filled_correct.csv')

#define violent
subcats_map = {
    "breakingPeace": ["assault", "wounding", "riot", "threateningBehaviour", "unknown"],
    "kill":          ["murder", "manslaughter", "infanticide", "pettyTreason", "other", "unknown"],
    "sexual":        ["rape", "indecentAssault", "assaultWithIntent",
                      "assaultWithSodomiticalIntent", "sodomy", "unknown"],
    "violentTheft":  ["robbery", "highwayRobbery", "other", "unknown"]
}

#fill unknown
df['offence_subcategory'] = df['offence_subcategory'].fillna('unknown')

#filter
df_filtered = df[df.apply(
    lambda r: r['offence_category'] in subcats_map
              and r['offence_subcategory'] in subcats_map[r['offence_category']],
    axis=1
)]

#compute overall
full_table_avg  = df['sentence_years'].mean()
violent_avg     = df_filtered['sentence_years'].mean()

#compute average per offence category
avg_by_cat = (
    df_filtered
    .groupby('offence_category')['sentence_years']
    .mean()
    .reset_index()
    .rename(columns={'sentence_years': 'AverageSentence'})
)

#plot
plt.figure(figsize=(8, 5))
bars = plt.bar(avg_by_cat['offence_category'], avg_by_cat['AverageSentence'], color='orange',edgecolor='black')

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,  # x-coordinate = center of the bar
        height + 0.02,                      # y-coordinate = just above the bar
        f"{height:.2f}",                   # label text
        ha='center',                       # horizontal alignment
        va='bottom'                        # vertical alignment
    )

#full-table average
plt.axhline(full_table_avg, color='red', linestyle='--',
            label=f'Overall Avg ({full_table_avg:.2f} yrs)')

#violent-crime average
plt.axhline(violent_avg, color='blue', linestyle=':',
            label=f'Violent-crime Avg ({violent_avg:.2f} yrs)')

plt.xlabel('Offence Category')
plt.ylabel('Average Sentence (years)')
plt.title('Average Imprisonment Sentence by Violent Offence Category')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.show()

