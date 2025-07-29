import re
import pandas as pd

#read SPSS recode file
inc_path = r"C:\Users\lenovo\Downloads\dataverse_files (3)\SPSS recode job HISCO into HISCLASS.inc"

with open(inc_path, 'r', encoding='utf-8', errors='ignore') as f:
    inc_text = f.read()

#extract (code=class)
pairs = re.findall(r'\((\-?\d+)=(-?\d+)\)', inc_text)

mapping_df = pd.DataFrame(pairs, columns=['hisco', 'hisclass'])
# keep 0（if HISCO length is 5）
mapping_df['hisco'] = mapping_df['hisco'].str.zfill(5)
mapping_df['hisclass'] = mapping_df['hisclass'].astype(int)

#save
output_path = r'D:\PY\FinalProject\1\hisco_hisclass_mapping.csv'
mapping_df.to_csv(output_path, index=False)

print(f"HISCO→HISCLASS write to：{output_path}")

