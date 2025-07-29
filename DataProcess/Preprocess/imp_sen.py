import re
import pandas as pd

#load
df = pd.read_csv("imprison_with_term.csv")

if 'punishment_term' not in df.columns:
    for c in df.columns:
        if c.lower().strip() == 'punishment_term':
            df.rename(columns={c: 'punishment_term'}, inplace=True)
            break

num_pattern = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen"
               r"|seventeen|eighteen|nineteen|twenty|twenty one|twenty two)")
unit_pattern = r"(year|years|month|months|week|weeks|day|days)"
regex = re.compile(rf"({num_pattern})\s+{unit_pattern}", re.IGNORECASE)

word2num = {
    'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,
    'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,
    'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,
    'eighteen':18,'nineteen':19,'twenty':20,'twenty one':21,'twenty two':22
}

def to_number(token: str) -> int:
    token = token.lower()
    return int(token) if token.isdigit() else word2num.get(token, 0)

def term_to_years(text: str) -> float:
    if not isinstance(text, str):
        return float('nan')
    matches = regex.findall(text)
    if not matches:
        return float('nan')
    total_years = 0.0
    for num_token, unit in matches:
        n = to_number(num_token)
        u = unit.lower()
        if 'year' in u:
            total_years += n
        elif 'month' in u:
            total_years += n / 12
        elif 'week' in u:
            total_years += n / 52
        elif 'day' in u:
            total_years += n / 365
    return total_years if total_years > 0 else float('nan')

#calulate
df['sentence_years'] = df['punishment_term'].apply(term_to_years)
df['sentence_months'] = (df['sentence_years'] * 12).round(2)
df['sentence_days'] = (df['sentence_years'] * 365).round(0) 

df.to_csv("imprison_with_sentence_years.csv", index=False)
print("imprison_with_sentence_years.csv generated")
