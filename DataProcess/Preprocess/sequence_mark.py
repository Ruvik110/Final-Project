import pandas as pd

#read
df = pd.read_csv('habitual_offenders_sorted.csv',
                 dtype={'defendant_name': str, 'birth_year': int, 'date': str})

#date
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.sort_values(['defendant_name', 'birth_year', 'date'])

#mark
df['offense_number'] = df.groupby(['defendant_name', 'birth_year']).cumcount() + 1

#save
output_path = 'habitual_offenders_with_sequence.csv'
df.to_csv(output_path, index=False, encoding='utf-8')

print(f"New CSV with offense sequence saved to: {output_path}")
