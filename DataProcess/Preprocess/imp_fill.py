import pandas as pd

#load both datasets
df_imp   = pd.read_csv('imprison_with_sentence_years.csv')
df_fill  = pd.read_csv('filled2_final.csv')

#trial_id to match offence_category/subcategory
fill_cat = df_fill.drop_duplicates('trial_id').set_index('trial_id')['offence_category']
fill_sub = df_fill.drop_duplicates('trial_id').set_index('trial_id')['offence_subcategory']

# missing to fill
df_imp['offence_category'] = df_imp['offence_category'].fillna(df_imp['trial_id'].map(fill_cat))
df_imp['offence_subcategory'] = df_imp['offence_subcategory'].fillna(df_imp['trial_id'].map(fill_sub))

#check
print("missing offence_category：", df_imp['offence_category'].isna().sum())
print("missing offence_subcategory：", df_imp['offence_subcategory'].isna().sum())

#save
df_imp.to_csv('imprison_filled_correct.csv', index=False)
