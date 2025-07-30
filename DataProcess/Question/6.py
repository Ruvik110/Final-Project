import pandas as pd
import matplotlib.pyplot as plt

#read
df = pd.read_csv(r'D:\PY\FinalProject\1\filled2_final.csv')

#year
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df = df[(df['year'] >= 1674) & (df['year'] <= 1913)]

#compute
corporal_df = df[df['punishment_category'].str.lower() == 'corporal'].copy()
subcat_counts = corporal_df['punishment_subcategory']\
    .fillna('no_subcategory')\
    .value_counts()
print("Corporal punishment subcategory counts:")
print(subcat_counts)
subcat_counts.to_csv(r'D:\PY\FinalProject\1\corporal_subcategories_counts.csv', header=['count'])

#mark
df['is_corporal'] = df['punishment_category'].str.lower().fillna('').eq('corporal')

#compute
annual = df.groupby('year').agg(
    total_cases=('is_corporal', 'count'),
    corporal_cases=('is_corporal', 'sum')
)
annual['corporal_rate'] = annual['corporal_cases'] / annual['total_cases'] * 100

#plot
plt.figure(figsize=(12, 6))
plt.plot(annual.index, annual['corporal_rate'], marker='o', linestyle='-')
plt.title('Annual Rate of Corporal Punishment (1674–1913)')
plt.xlabel('Year')
plt.ylabel('Corporal Punishment Rate (%)')
plt.grid(True)
plt.tight_layout()
plt.show()
