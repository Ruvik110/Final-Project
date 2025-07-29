import os
import csv
import xml.etree.ElementTree as ET
from itertools import zip_longest

input_folder = r"D:\PY\4775434\OBO_XML_7-2\sessionsPapers"
output_file  = 'output14.csv'

csv_columns = [
    "trial_id","year","date","defendant_id",
    "defendant_name","surname","given","gender",
    "age","occupation","offence_category","offence_subcategory",
    "victim_name","verdict_category",
    "verdict_subcategory","punishment_category","punishment_subcategory"
]

def find_persname(trial, did):
    #find defendantName
    for p in trial.findall(".//persName[@type='defendantName']"):
        if p.get('id') == did: return p
    #persName
    for p in trial.findall(".//persName"):
        if p.get('id') == did: return p
    #smallCaps
    for hi in trial.findall(".//hi[@rend='smallCaps']"):
        for p in hi.findall(".//persName"):
            if p.get('id') == did: return p
    return None

def parse_xml(fp):
    try:
        tree = ET.parse(fp)
        root = tree.getroot()
    except ET.ParseError:
        return []

    recs = []
    for trial in root.findall(".//div1[@type='trialAccount']"):
        tid = trial.get('id','')
        #date/year
        d_e = trial.find(".//interp[@type='date']")
        date = d_e.get('value','') if d_e is not None else ''
        y_e = trial.find(".//interp[@type='year']")
        year = y_e.get('value','') if (y_e is not None and y_e.get('value')) else date[:4]

        #collect defendants
        defs = {p.get('id') for p in trial.findall(".//persName[@type='defendantName']") if p.get('id')}
        for j in trial.findall(".//join"):
            for t in j.get('targets','').split():
                if 'defend' in t or t.startswith('def'):
                    defs.add(t)

        for did in defs:
            #collect defendant's joins
            cc_list  = [j for j in trial.findall(".//join[@result='criminalCharge']")
                        if did in j.get('targets','').split()]
            pun_list = [j for j in trial.findall(".//join[@result='defendantPunishment']")
                        if did in j.get('targets','').split()]

            #zip together (if one side shorter, fill None)
            for jc, jp in zip_longest(cc_list, pun_list):
                data = {
                    "trial_id":     tid,
                    "year":         year,
                    "date":         date,
                    "defendant_id": did,
                    **{col:'' for col in csv_columns if col not in ['trial_id','year','date','defendant_id']}
                }

                #personal info
                p = find_persname(trial, did)
                if p is not None:
                    sn = p.find(f"./interp[@type='surname'][@inst='{did}']")
                    gn = p.find(f"./interp[@type='given'][@inst='{did}']")
                    data['surname']        = sn.get('value','') if sn is not None else ''
                    data['given']          = gn.get('value','') if gn is not None else ''
                    data['defendant_name'] = f"{data['given']} {data['surname']}".strip()
                    g  = p.find(f"./interp[@type='gender'][@inst='{did}']")
                    a  = p.find(f"./interp[@type='age'][@inst='{did}']")
                    if g is not None: data['gender'] = g.get('value','')
                    if a is not None: data['age']    = a.get('value','')
                    occ = p.find(f"./interp[@type='occupation'][@inst='{did}']")
                    if occ is not None and occ.get('value'):
                        data['occupation'] = occ.get('value')
                    else:
                        for jo in trial.findall(".//join[@result='persNameOccupation']"):
                            tg = jo.get('targets','').split()
                            if did in tg:
                                other = tg[1] if tg[0]==did else tg[0]
                                rs_occ = trial.find(f".//rs[@id='{other}'][@type='occupation']")
                                if rs_occ is not None and rs_occ.text:
                                    data['occupation'] = rs_occ.text.strip()
                                    break

                #offence & verdict
                if jc is not None:
                    tg = jc.get('targets','').split()
                    off = next((t for t in tg if '-off' in t), None)
                    if off:
                        rs = trial.find(f".//rs[@id='{off}']")
                        if rs is not None:
                            oc = rs.find(".//interp[@type='offenceCategory']")
                            os = rs.find(".//interp[@type='offenceSubcategory']")
                            if oc is not None: data['offence_category']    = oc.get('value','')
                            if os is not None: data['offence_subcategory'] = os.get('value','')
                    vr = next((t for t in tg if '-verdict' in t), None)
                    if vr:
                        rs = trial.find(f".//rs[@id='{vr}']")
                        if rs is not None:
                            vc = rs.find(".//interp[@type='verdictCategory']")
                            vs = rs.find(".//interp[@type='verdictSubcategory']")
                            if vc is not None: data['verdict_category']    = vc.get('value','')
                            if vs is not None: data['verdict_subcategory'] = vs.get('value','')

                    #victim
                    for ov in trial.findall(".//join[@result='offenceVictim']"):
                        tg2 = ov.get('targets','').split()
                        if did in tg2 and off in tg2:
                            vic = next((t for t in tg2 if '-victim' in t), None)
                            if vic:
                                vn = trial.find(f".//persName[@id='{vic}']")
                                if vn is not None:
                                    su = vn.find(f".//interp[@type='surname'][@inst='{vic}']")
                                    gi = vn.find(f".//interp[@type='given'][@inst='{vic}']")
                                    s = su.get('value','') if su is not None else ''
                                    g = gi.get('value','') if gi is not None else ''
                                    data['victim_name'] = f"{g} {s}".strip()
                            break

                #punishment
                if jp is not None:
                    tg = jp.get('targets','').split()
                    pun = next((t for t in tg if '-punish' in t), None)
                    if pun:
                        rs = trial.find(f".//rs[@id='{pun}']")
                        if rs is not None:
                            pc = rs.find(".//interp[@type='punishmentCategory']")
                            ps = rs.find(".//interp[@type='punishmentSubcategory']")
                            if pc is not None: data['punishment_category']    = pc.get('value','')
                            if ps is not None: data['punishment_subcategory'] = ps.get('value','')

                recs.append(data)

    return recs

def write_to_csv(data, of):
    with open(of, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=csv_columns)
        w.writeheader()
        w.writerows(data)

def process_files(input_folder, output_file):
    all_records = []
    for root, dirs, files in os.walk(input_folder):
        for fn in files:
            if fn.lower().endswith('.xml'):
                all_records.extend(parse_xml(os.path.join(root, fn)))
    write_to_csv(all_records, output_file)

if __name__ == '__main__':
    process_files(input_folder, output_file)
