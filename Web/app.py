import os, csv, functools
from flask import Flask, jsonify, render_template, abort, request
import pandas as pd
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# ── 数据文件映射 ─────────────────────────────────────────────
DATA_DIR = os.path.join(app.root_path, 'data')
FILES = {
    'base':     'filled2_final.csv',                     # 趋势 + 全局筛选
    'imprison': 'imprison_filled_correct.csv',      # 刑期
    'habitual': 'habitual_offenders_with_sequence.csv',  # 惯犯
    'social':   'subset_with_hisco_classified.csv'       # 社会阶层
}

@functools.lru_cache(maxsize=None)
def load_csv(key):
    """读取并缓存 CSV，数字字段自动转 int"""
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

# ── 路由 ───────────────────────────────────────────────────
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

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
    # category -> subcategory map
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
    # 按年统计 count
    year_counts = filtered.groupby('year').size().reset_index(name='count')
    # 计算每年总案件数
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
                'description': 'Judgment of Death Act 1823: Allowed judges to commute the death sentence for all crimes except murder and treason.'
            },
            {
                'year': 1832,
                'title': 'Punishment of Death, etc. Act 1832',
                'description': 'Punishment of Death, etc. Act 1832: Abolished the death penalty for over 100 offences, including many non-violent crimes.'
            },
            {
                'year': 1841,
                'title': 'Substitution Act 1841',
                'description': 'Substitution Act 1841: Further reduced the number of capital offences, substituting transportation or imprisonment for death in many cases.'
            },
            {
                'year': 1868,
                'title': 'Capital Punishment Amendment Act 1868',
                'description': 'Capital Punishment Amendment Act 1868: Required that executions be carried out within prison walls, ending public executions in the UK.'
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
                'description': 'Transportation Act 1717: This act established transportation as a punishment for various crimes, allowing convicts to be sent to the American colonies for labor.'
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
    # 选择数据源
    if group_by == 'hisclass':
        df_bar = pd.read_csv('data/subset_with_hisco_classified.csv', low_memory=False)
    else:
        df_bar = df.copy()
    filtered = df_bar.copy()
    if start_year and end_year:
        filtered = filtered[(filtered['year'] >= start_year) & (filtered['year'] <= end_year)]
    elif start_year:
        filtered = filtered[filtered['year'] == start_year]
    filtered = filtered[(filtered['verdict_category'] != 'notguilty') & (filtered['punishment_category'] != 'nopunish')]
    valid_punishments = ['death', 'corporal', 'transport', 'imprison', 'miscpunish']
    if exclude_death:
        valid_punishments = [p for p in valid_punishments if p != 'death']
    if group_by == 'hisclass':
        filtered = filtered[filtered['hisclass'].notna()]
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
    # 统计每种 group_by 下 punishment_category 的数量
    result = (
        filtered[filtered['punishment_category'].isin(valid_punishments)]
        .groupby([group_col, 'punishment_category'])
        .size()
        .reset_index(name='count')
    )
    # 统计每个 group_by 的总数
    group_totals = result.groupby(group_col)['count'].sum().to_dict()
    # group_by -> {punishment_category: 归一化rate}
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
    
    # 确定所有组和惩罚类别
    if group_by == 'hisclass':
        all_groups = ['Upper (1–2)', 'Middle (3–6)', 'Lower (7–12)']
    else:
        all_groups = sorted([g for g in filtered[group_col].dropna().unique().tolist() if g != 'unknown'])
    all_punishments = valid_punishments
    
    # 确保所有组都有完整的数据结构，缺失的punishment设为0
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
    # 读取 imprison 数据
    df_imprison = pd.read_csv('data/imprison_filled_correct.csv', low_memory=False)
    filtered = df_imprison.copy()
    if start_year and end_year:
        filtered = filtered[(filtered['year'] >= start_year) & (filtered['year'] <= end_year)]
    elif start_year:
        filtered = filtered[filtered['year'] == start_year]
    # 过滤有效刑期数据
    filtered = filtered[filtered['sentence_years'].notna()]
    filtered = filtered[filtered['sentence_years'] > 0]
    if analysis_type == 'avg_sentence':
        # 过滤掉 unknown 的 offence_category
        filtered = filtered[filtered['offence_category'] != 'unknown']
        # 按 offence_category 计算平均刑期
        result = filtered.groupby('offence_category')['sentence_years'].agg(['mean', 'count']).reset_index()
        result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
        result = result.sort_values('avg_sentence', ascending=False)
        return jsonify({
            'type': 'avg_sentence',
            'data': result.to_dict('records'),
            'categories': result['offence_category'].tolist(),
            'values': result['avg_sentence'].tolist(),
            'counts': result['case_count'].tolist()
        })
    elif analysis_type == 'theft_value':
        # 根据盗窃财物价值的刑期
        theft_categories = ['theftunder1s', 'theftunder5s', 'theftunder40s', 'theftunder100s']
        filtered = filtered[filtered['verdict_subcategory'].isin(theft_categories)]
        
        if filtered.empty:
            return jsonify({
                'type': 'theft_value',
                'data': [],
                'categories': [],
                'values': [],
                'counts': [],
                'message': 'No theft data available for selected criteria'
            })
        
        # 按 verdict_subcategory 计算平均刑期
        result = filtered.groupby('verdict_subcategory')['sentence_years'].agg(['mean', 'count']).reset_index()
        result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
        
        # 按价值排序（从低到高）
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
            'counts': result['case_count'].tolist()
        })
    elif analysis_type == 'violent_crime':
        # 暴力犯罪的平均刑期
        # 定义暴力犯罪子类别映射
        violent_subcats_map = {
            "breakingPeace": ["assault", "wounding", "riot", "threateningBehaviour", "unknown"],
            "kill":          ["murder", "manslaughter", "infanticide", "pettyTreason", "other", "unknown"],
            "sexual":        ["rape", "indecentAssault", "assaultWithIntent",
                              "assaultWithSodomiticalIntent", "sodomy", "unknown"],
            "violentTheft":  ["robbery", "highwayRobbery", "other", "unknown"]
        }
        
        # 正确的过滤逻辑：先按大类过滤，再按子类别过滤
        filtered_violent = pd.DataFrame()
        
        for category, subcategories in violent_subcats_map.items():
            # 先过滤出对应的大类
            category_data = filtered[filtered['offence_category'] == category]
            # 再过滤出对应的子类别
            category_filtered = category_data[category_data['offence_subcategory'].isin(subcategories)]
            # 添加到结果中
            filtered_violent = pd.concat([filtered_violent, category_filtered], ignore_index=True)
        
        if filtered_violent.empty:
            return jsonify({
                'type': 'violent_crime',
                'data': [],
                'categories': [],
                'values': [],
                'counts': [],
                'message': 'No violent crime data available for selected criteria'
            })
        
        # 按暴力犯罪4大类计算平均刑期
        result = filtered_violent.groupby('offence_category')['sentence_years'].agg(['mean', 'count']).reset_index()
        result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
        result = result.sort_values('avg_sentence', ascending=False)
        
        return jsonify({
            'type': 'violent_crime',
            'data': result.to_dict('records'),
            'categories': result['offence_category'].tolist(),
            'values': result['avg_sentence'].tolist(),
            'counts': result['case_count'].tolist()
        })
    elif analysis_type == 'habitual_vs_first':
        # 惯犯和初犯的刑期对比
        try:
            # 读取已合并的数据
            df_merged = pd.read_csv('data/merged_habitual_sentence.csv', low_memory=False)
            
            # 应用年份过滤
            if start_year and end_year:
                df_merged = df_merged[(df_merged['year'] >= start_year) & (df_merged['year'] <= end_year)]
            elif start_year:
                df_merged = df_merged[df_merged['year'] == start_year]
            
            # 过滤有效刑期数据
            df_merged = df_merged[df_merged['sentence_years'].notna()]
            df_merged = df_merged[df_merged['sentence_years'] > 0]
            
            # 根据 offense_number 分类
            df_merged['offender_type'] = df_merged['offense_number'].apply(
                lambda x: 'First-time Offender' if x == 1 else 'Habitual Offender'
            )
            
            # 按 offender_type 计算平均刑期
            result = df_merged.groupby('offender_type')['sentence_years'].agg(['mean', 'count']).reset_index()
            result = result.rename(columns={'mean': 'avg_sentence', 'count': 'case_count'})
            result = result.sort_values('avg_sentence', ascending=False)
            
            return jsonify({
                'type': 'habitual_vs_first',
                'data': result.to_dict('records'),
                'categories': result['offender_type'].tolist(),
                'values': result['avg_sentence'].tolist(),
                'counts': result['case_count'].tolist()
            })
        except Exception as e:
            return jsonify({
                'type': 'habitual_vs_first',
                'data': [],
                'categories': [],
                'values': [],
                'counts': [],
                'message': f'Error processing habitual offender data: {str(e)}'
            })
    else:
        return jsonify({'error': 'Invalid analysis_type'})

if __name__ == '__main__':
    app.run(debug=True)
