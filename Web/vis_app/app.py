import os
import csv
import functools
from flask import Flask, jsonify, render_template, abort, request
import pandas as pd
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# data files
DATA_DIR = os.path.join(app.root_path, 'data')
FILES = {
    'base':     'filled2_final.csv',                     
    'imprison': 'imprison_filled_correct.csv',     
    'habitual': 'merged_habitual_sentence.csv',  
    'social':   'subset_with_hisco_classified.csv'      
}

@functools.lru_cache(maxsize=None)
def load_csv(key):
    path = os.path.join(DATA_DIR, FILES[key])
    if not os.path.exists(path):
        abort(500, f'Data file {path} not found')
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            for k, v in row.items():
                if v.isdigit():
                    row[k] = int(v)
            rows.append(row)
        return rows

data_path = 'data/filled2_final.csv'
df = pd.read_csv(data_path, low_memory=False)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/<key>')
def api_data(key):
    if key not in FILES:
        abort(404)
    return jsonify(load_csv(key))

@app.route('/api/options')
def get_options():
    offences = sorted(df['offence_category'].dropna().unique().tolist())
    offence_subcategories = sorted(df['offence_subcategory'].dropna().unique().tolist())
    punishments = sorted(df['punishment_category'].dropna().unique().tolist())
    punishment_subcategories = sorted(df['punishment_subcategory'].dropna().unique().tolist())
    # category to subcategory
    offcat_map = df.dropna(subset=['offence_category', 'offence_subcategory']) \
        .groupby('offence_category')['offence_subcategory'].unique().apply(list).to_dict()
    puncat_map = df.dropna(subset=['punishment_category', 'punishment_subcategory']) \
        .groupby('punishment_category')['punishment_subcategory'].unique().apply(list).to_dict()
    return jsonify({
        'offence_categories': offences,
        'offence_subcategories': offence_subcategories,
        'punishment_categories': punishments,
        'punishment_subcategories': punishment_subcategories,
        'offence_subcategories_map': offcat_map,
        'punishment_subcategories_map': puncat_map
    })

@app.route('/api/line_data')
def get_line_data():
    offence = request.args.get('offence_category')
    offence_sub = request.args.get('offence_subcategory')
    punishment = request.args.get('punishment_category')
    punishment_sub = request.args.get('punishment_subcategory')
    filtered = df.copy()
    if offence:
        filtered = filtered[filtered['offence_category'] == offence]
    if offence_sub:
        filtered = filtered[filtered['offence_subcategory'] == offence_sub]
    if punishment:
        filtered = filtered[filtered['punishment_category'] == punishment]
    if punishment_sub:
        filtered = filtered[filtered['punishment_subcategory'] == punishment_sub]
    # count by year
    year_counts = filtered.groupby('year').size().reset_index(name='count')
    total_counts = df.groupby('year').size().reset_index(name='total')
    merged = pd.merge(year_counts, total_counts, on='year', how='right').fillna(0)
    merged['rate'] = merged['count'] / merged['total']
    merged = merged.sort_values('year')
    merged['year'] = merged['year'].astype(int)
    return jsonify({
        'years': merged['year'].tolist(),
        'counts': merged['count'].astype(int).tolist(),
        'rates': merged['rate'].tolist()
    })

@app.route('/api/acts')
def get_acts():
    return jsonify({
        'year': 1835,
        'title': 'Prison Act 1835',
        'description': 'Prison Act 1835: This act established the first system of prison inspectors in England and Wales, aiming to improve prison conditions and administration.'
    })

@app.route('/api/campaigns')
def get_campaigns():
    return jsonify({
        'title': 'Campaign Against Death Sentence',
        'acts': [
            {
                'year': 1808,
                'title': 'Romilly\'s 1808 Act',
                'description': 'Romilly\'s 1808 Act: The first of a series of reforms by Sir Samuel Romilly, which began the process of reducing the number of capital offences in English law.'
            },
            {
                'year': 1823,
                'title': 'Judgment of Death Act 1823',
                'description': 'Judgment of Death Act 1823: Allowed judges to commute the death sentence for crimes except murder and treason.'
            },
            {
                'year': 1832,
                'title': 'Punishment of Death, etc. Act 1832',
                'description': 'Punishment of Death, etc. Act 1832: Reduced the number of capital crimes by two-thirds.'
            },
            {
                'year': 1841,
                'title': 'Substitution Act 1841',
                'description': 'Substitution Act 1841: Further reduced the number of capital offences, substituting transportation or imprisonment for death in many cases.'
            },
            {
                'year': 1868,
                'title': 'Capital Punishment Amendment Act 1868',
                'description': 'Capital Punishment Amendment Act 1868: Required that executions be carried out within prison, ending public executions in the UK.'
            }
        ]
    })

@app.route('/api/transportation')
def get_transportation():
    return jsonify({
        'title': 'Transportation',
        'acts': [
            {
                'year': 1717,
                'title': 'Transportation Act 1717',
                'description': 'Transportation Act 1717: This act established transportation as a punishment for various crimes, allowing convicts to be sent to the colonies for labor.'
            },
            {
                'year': 1857,
                'title': 'Penal Servitude Act 1857',
                'description': 'Penal Servitude Act 1857: This act introduced penal servitude as a form of imprisonment with hard labor, replacing transportation as a major form of punishment.'
            }
        ]
    })

@app.route('/api/bar_data')
def get_bar_data():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    exclude_death = request.args.get('exclude_death', default='0') == '1'
    group_by = request.args.get('group_by', default='offence_category')
    hisclass_detail = request.args.get('hisclass_detail', default='0') == '1'
    # select data
    if group_by == 'hisclass':
        df_bar = pd.read_csv('data/subset_with_hisco_classified.csv', low_memory=False)
    else:
        df_bar = df.copy()
    filtered = df_bar.copy()
    if start_year and end_year:
        filtered = filtered[(filtered['year'] >= start_year) & (filtered['year'] <= end_year)]
    elif start_year:
        filtered = filtered[filtered['year'] == start_year]
    filtered = filtered[(filtered['punishment_category'] != 'notguilty') & (filtered['punishment_category'] != 'nopunish')]
    valid_punishments = ['death', 'corporal', 'transport', 'imprison', 'miscpunish']
    if exclude_death:
        valid_punishments = [p for p in valid_punishments if p != 'death']
    if group_by == 'hisclass':
        filtered = filtered[filtered['hisclass'].notna()]
        if hisclass_detail:
            filtered['hisclass_group'] = filtered['hisclass'].astype(int).astype(str)
            filtered = filtered[filtered['hisclass_group'].isin([str(i) for i in range(1,13)])]
            group_col = 'hisclass_group'
        else:
            def hisclass_group(h):
                try:
                    h = int(h)
                    if 1 <= h <= 2:
                        return 'Upper (1–2)'
                    elif 3 <= h <= 6:
                        return 'Middle (3–6)'
                    elif 7 <= h <= 12:
                        return 'Lower (7–12)'
                except Exception:
                    return None
                return None
            filtered['hisclass_group'] = filtered['hisclass'].apply(hisclass_group)
            filtered = filtered[filtered['hisclass_group'].notna()]
            group_col = 'hisclass_group'
    else:
        filtered = filtered[filtered['offence_category'] != 'unknown']
        group_col = 'offence_category'

    result = (
        filtered[filtered['punishment_category'].isin(valid_punishments)]
        .groupby([group_col, 'punishment_category'])
        .size()
        .reset_index(name='count')
    )

    group_totals = result.groupby(group_col)['count'].sum().to_dict()
    # group_by to punishment
    data = {}
    for _, row in result.iterrows():
        group = row[group_col]
        pun = row['punishment_category']
        cnt = int(row['count'])
        total = group_totals[group]
        rate = cnt / total if total else 0
        if group not in data:
            data[group] = {}
        data[group][pun] = rate
    # determine groups and punishment categories
    if group_by == 'hisclass':
        if hisclass_detail:
            all_groups = [str(i) for i in range(1,13)]
        else:
            all_groups = ['Upper (1–2)', 'Middle (3–6)', 'Lower (7–12)']
    else:
        all_groups = sorted([g for g in filtered[group_col].dropna().unique().tolist() if g != 'unknown'])
    all_punishments = valid_punishments
    # ensure all groups complete
    for group in all_groups:
        if group not in data:
            data[group] = {}
        for punishment in all_punishments:
            if punishment not in data[group]:
                data[group][punishment] = 0
    
    return jsonify({
        'data': data,
        'groups': all_groups,
        'punishment_categories': all_punishments,
        'group_by': group_col
    })

@app.route('/api/imprison_data')
def get_imprison_data():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    analysis_type = request.args.get('analysis_type', default='avg_sentence')
    show_average = request.args.get('show_average', default='0') == '1'
    # imprison data
    df_imprison = pd.read_csv('data/imprison_filled_correct.csv', low_memory=False)
    filtered = df_imprison.copy()
    if start_year and end_year:
        filtered = filtered[(filtered['year'] >= start_year) & (filtered['year'] <= end_year)]
    elif start_year:
        filtered = filtered[filtered['year'] == start_year]
    # filter sentence years
    filtered = filtered[filtered['sentence_years'].notna()]
    filtered = filtered[filtered['sentence_years'] > 0]
    
    # total average
    total_average = round(filtered['sentence_years'].mean(), 2) if not filtered.empty else 0
    
    if analysis_type == 'avg_sentence':
        filtered = filtered[filtered['offence_category'] != 'unknown']
        # average sentence by offence_category
        result = filtered.groupby('offence_category')['sentence_years'].agg(['mean', 'count']).reset_index()
        result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
        # Round average sentences to 2 decimal places
        result['avg_sentence'] = result['avg_sentence'].round(2)
        result = result.sort_values('avg_sentence', ascending=False)
        
        return jsonify({
            'type': 'avg_sentence',
            'data': result.to_dict('records'),
            'categories': result['offence_category'].tolist(),
            'values': result['avg_sentence'].tolist(),
            'counts': result['case_count'].tolist(),
            'total_average': total_average if show_average else None
        })
    elif analysis_type == 'theft_value':
        # average sentence by theft value
        theft_categories = ['theftunder1s', 'theftunder5s', 'theftunder40s', 'theftunder100s']
        filtered = filtered[filtered['verdict_subcategory'].isin(theft_categories)]
        
        if filtered.empty:
            return jsonify({
                'type': 'theft_value',
                'data': [],
                'categories': [],
                'values': [],
                'counts': [],
                'message': 'No theft data available for selected criteria',
                'total_average': None
            })
        
        result = filtered.groupby('verdict_subcategory')['sentence_years'].agg(['mean', 'count']).reset_index()
        result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
        # Round average sentences to 2 decimal places
        result['avg_sentence'] = result['avg_sentence'].round(2)
        
        # sort by value
        value_order = {
            'theftunder1s': 1,
            'theftunder5s': 2,
            'theftunder40s': 3,
            'theftunder100s': 4
        }
        result['value_order'] = result['verdict_subcategory'].map(value_order)
        result = result.sort_values('value_order')
        
        return jsonify({
            'type': 'theft_value',
            'data': result.to_dict('records'),
            'categories': result['verdict_subcategory'].tolist(),
            'values': result['avg_sentence'].tolist(),
            'counts': result['case_count'].tolist(),
            'total_average': None
        })
    elif analysis_type == 'violent_crime':
        # define violent crime subcategories
        violent_subcats_map = {
            "breakingPeace": ["assault", "wounding", "riot", "threateningBehaviour", "unknown"],
            "kill":          ["murder", "manslaughter", "infanticide", "pettyTreason", "other", "unknown"],
            "sexual":        ["rape", "indecentAssault", "assaultWithIntent",
                              "assaultWithSodomiticalIntent", "sodomy", "unknown"],
            "violentTheft":  ["robbery", "highwayRobbery", "other", "unknown"]
        }
        
        filtered_violent = pd.DataFrame()
        
        for category, subcategories in violent_subcats_map.items():
            # by offence_category
            category_data = filtered[filtered['offence_category'] == category]
            # by offence_subcategory
            category_filtered = category_data[category_data['offence_subcategory'].isin(subcategories)]
            filtered_violent = pd.concat([filtered_violent, category_filtered], ignore_index=True)
        
        if filtered_violent.empty:
            return jsonify({
                'type': 'violent_crime',
                'data': [],
                'categories': [],
                'values': [],
                'counts': [],
                'message': 'No violent crime data available for selected criteria',
                'total_average': None
            })
        
        # average sentence by offence_category
        result = filtered_violent.groupby('offence_category')['sentence_years'].agg(['mean', 'count']).reset_index()
        result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
        # Round average sentences to 2 decimal places
        result['avg_sentence'] = result['avg_sentence'].round(2)
        result = result.sort_values('avg_sentence', ascending=False)
        
        # Calculate total average for all violent crime cases
        violent_total_average = round(filtered_violent['sentence_years'].mean(), 2)
        
        return jsonify({
            'type': 'violent_crime',
            'data': result.to_dict('records'),
            'categories': result['offence_category'].tolist(),
            'values': result['avg_sentence'].tolist(),
            'counts': result['case_count'].tolist(),
            'total_average': total_average if show_average else None,
            'violent_average': violent_total_average
        })
    elif analysis_type == 'habitual_vs_first':
        try:
            df_merged = pd.read_csv('data/merged_habitual_sentence.csv', low_memory=False)
            
            if start_year and end_year:
                df_merged = df_merged[(df_merged['year'] >= start_year) & (df_merged['year'] <= end_year)]
            elif start_year:
                df_merged = df_merged[df_merged['year'] == start_year]
            
            df_merged = df_merged[df_merged['sentence_years'].notna()]
            df_merged = df_merged[df_merged['sentence_years'] > 0]
            
            # by offense_number
            df_merged['offender_type'] = df_merged['offense_number'].apply(
                lambda x: 'First-time Offender' if x == 1 else 'Habitual Offender'
            )
            
            # average sentence by offender_type
            result = df_merged.groupby('offender_type')['sentence_years'].agg(['mean', 'count']).reset_index()
            result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
            # Round average sentences to 2 decimal places
            result['avg_sentence'] = result['avg_sentence'].round(2)
            result = result.sort_values('avg_sentence', ascending=False)
            
            return jsonify({
                'type': 'habitual_vs_first',
                'data': result.to_dict('records'),
                'categories': result['offender_type'].tolist(),
                'values': result['avg_sentence'].tolist(),
                'counts': result['case_count'].tolist(),
                'total_average': None
            })
        except Exception as e:
            return jsonify({
                'type': 'habitual_vs_first',
                'data': [],
                'categories': [],
                'values': [],
                'counts': [],
                'message': f'Error processing habitual offender data: {str(e)}',
                'total_average': None
            })
    else:
        return jsonify({'error': 'Invalid analysis_type'})

if __name__ == '__main__':
    app.run(debug=True)
