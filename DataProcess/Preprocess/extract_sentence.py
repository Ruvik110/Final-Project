import os
import csv
import xml.etree.ElementTree as ET

input_folder = r"D:\PY\4775434\OBO_XML_7-2\sessionsPapers"
output_file  = 'imprison_with_term.csv'

csv_columns = [
    "trial_id","year","date","defendant_id",
    "defendant_name","surname","given","gender",
    "age","occupation","offence_category","offence_subcategory",
    "victim_name","verdict_category","verdict_subcategory",
    "punishment_category","punishment_subcategory","punishment_term"
]

def find_persname(trial, did):
    for p in trial.findall(".//persName[@type='defendantName']"):
        if p.get('id') == did:
            return p
    for p in trial.findall(".//persName"):
        if p.get('id') == did:
            return p
    for hi in trial.findall(".//hi[@rend='smallCaps']"):
        for p in hi.findall(".//persName"):
            if p.get('id') == did:
                return p
    return None

def extract_term_text(rs_elem):
    #free text as sentence
    texts = []
    for node in rs_elem.itertext():
        texts.append(node.strip())
    full = " ".join(t for t in texts if t)
    return full

def parse_xml(fp):
    try:
        tree = ET.parse(fp)
    except ET.ParseError:
        return []
    root = tree.getroot()

    #punishment join
    pun_mapping = {}
    for jp in root.findall(".//join[@result='defendantPunishment']"):
        parts = jp.get('targets','').split()
        if len(parts) < 2: continue
        did = parts[0]
        for rs_id in parts[1:]:
            pun_mapping.setdefault(rs_id, []).append(did)

    recs = []
    for trial in root.findall(".//div1[@type='trialAccount']"):
        tid = trial.get('id','')
        d_e = trial.find(".//interp[@type='date']")
        date = d_e.get('value','') if d_e is not None else ''
        y_e = trial.find(".//interp[@type='year']")
        year = (y_e.get('value') if (y_e is not None and y_e.get('value'))
                else date[:4])

        #defendants' ids
        defs = {p.get('id') for p in trial.findall(".//persName[@type='defendantName']") if p.get('id')}
        for j in trial.findall(".//join"):
            for t in j.get('targets','').split():
                if 'defend' in t or t.startswith('def'):
                    defs.add(t)

        for did in defs:
            for jc in trial.findall(".//join[@result='criminalCharge']"):
                tg = jc.get('targets','').split()
                if did not in tg: continue

                data = {c: "" for c in csv_columns}
                data.update({
                    "trial_id":     tid,
                    "year":         year,
                    "date":         date,
                    "defendant_id": did
                })

                #persName
                p = find_persname(trial, did)
                if p is not None:
                    sn = p.find(f"./interp[@type='surname'][@inst='{did}']")
                    gn = p.find(f"./interp[@type='given'][@inst='{did}']")
                    if sn is not None: data['surname'] = sn.get('value','')
                    if gn is not None: data['given']   = gn.get('value','')
                    data['defendant_name'] = f"{data['given']} {data['surname']}".strip()
                    ge = p.find(f"./interp[@type='gender'][@inst='{did}']")
                    ag = p.find(f"./interp[@type='age'][@inst='{did}']")
                    if ge is not None: data['gender'] = ge.get('value','')
                    if ag is not None: data['age']    = ag.get('value','')
                    occ = p.find(f"./interp[@type='occupation'][@inst='{did}']")
                    if occ is not None and occ.get('value'):
                        data['occupation'] = occ.get('value')
                    else:
                        for jo in trial.findall(".//join[@result='persNameOccupation']"):
                            t2 = jo.get('targets','').split()
                            if did in t2:
                                other = t2[1] if t2[0]==did else t2[0]
                                rs_occ = trial.find(f".//rs[@id='{other}'][@type='occupation']")
                                if rs_occ is not None and rs_occ.text:
                                    data['occupation'] = rs_occ.text.strip()
                                    break

                #offence
                off_id = next((x for x in tg if '-offence' in x), None)
                if off_id:
                    rs_off = trial.find(f".//rs[@id='{off_id}']")
                    if rs_off is not None:
                        oc = rs_off.find(".//interp[@type='offenceCategory']")
                        os = rs_off.find(".//interp[@type='offenceSubcategory']")
                        if oc is not None: data['offence_category']    = oc.get('value','')
                        if os is not None: data['offence_subcategory'] = os.get('value','')

                #verdict
                ver_id = next((x for x in tg if '-verdict' in x), None)
                if ver_id:
                    rs_ver = trial.find(f".//rs[@id='{ver_id}']")
                    if rs_ver is not None:
                        vc = rs_ver.find(".//interp[@type='verdictCategory']")
                        vs = rs_ver.find(".//interp[@type='verdictSubcategory']")
                        if vc is not None: data['verdict_category']    = vc.get('value','')
                        if vs is not None: data['verdict_subcategory'] = vs.get('value','')

                #victim
                for ov in trial.findall(".//join[@result='offenceVictim']"):
                    t3 = ov.get('targets','').split()
                    if did in t3 and off_id in t3:
                        vic = next((x for x in t3 if '-victim' in x), None)
                        if vic:
                            vn = trial.find(f".//persName[@id='{vic}']")
                            if vn is not None:
                                su = vn.find(f"./interp[@type='surname'][@inst='{vic}']")
                                gi = vn.find(f"./interp[@type='given'][@inst='{vic}']")
                                s = su.get('value','') if su is not None else ''
                                g2= gi.get('value','') if gi is not None else ''
                                data['victim_name'] = f"{g2} {s}".strip()
                        break

                #punishment & term
                for pr_id, dids in pun_mapping.items():
                    if did in dids:
                        rs_pun = trial.find(f".//rs[@id='{pr_id}']")
                        if rs_pun is None: continue
                        pc = rs_pun.find(".//interp[@type='punishmentCategory']")
                        ps = rs_pun.find(".//interp[@type='punishmentSubcategory']")
                        if pc is not None:
                            data['punishment_category']    = pc.get('value','')
                        if ps is not None:
                            data['punishment_subcategory'] = ps.get('value','')
                        term = extract_term_text(rs_pun)
                        data['punishment_term'] = term
                #keep imprisonment
                if data['punishment_category'].lower() == 'imprison':
                    recs.append(data)

    return recs

def write_to_csv(data, of):
    with open(of, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=csv_columns)
        w.writeheader()
        w.writerows(data)

def process_files(input_folder, output_file):
    all_recs = []
    for root, dirs, files in os.walk(input_folder):
        for fn in files:
            if fn.lower().endswith('.xml'):
                all_recs.extend(parse_xml(os.path.join(root, fn)))
    write_to_csv(all_recs, output_file)
    print(f" {len(all_recs)} records to  {output_file}")

if __name__ == '__main__':
    process_files(input_folder, output_file)

