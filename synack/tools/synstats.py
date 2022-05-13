from synack import synack
from datetime import datetime
from os import path
import csv
import json
import os

os.makedirs("vulns", exist_ok=True)

s = synack()
s.connectToPlatform()
s.getSessionToken()

vulns = s.getVulns("accepted")

vulns_data = []
count = 0
for v in vulns:
    if count % 50 == 0:
        print("Analyzing %d of %d" % (count, len(vulns)))
    count = count + 1

    vuln_fname = "vulns/%s.json" % v['id']
    # read extended vuln data
    if not path.exists(vuln_fname):
        expanded_vuln = s.getVuln(v['id'])
        with open(vuln_fname,"w") as f:
            json.dump(expanded_vuln, f, ensure_ascii=False, indent=4)
    else:
        with open(vuln_fname,"r") as f:
            expanded_vuln = json.load(f)
    
    vulns_data.append({
        "id": v['id'],
        "title": v['title'],
        # not sure what to do with timestamp format :)
        "created_at": expanded_vuln['created_at'],
        "resolved_at": expanded_vuln['resolved_at'],
        "amount": v['market_value_final'],
        "subcategory": v['category'],
        "category": v['category_parent'],
        "target": v['listing']['codename'],
        "cvss": expanded_vuln['cvss_final'],
        "quality": expanded_vuln['quality_score']
    })


columns = ["id", "created_at", "title", "amount", "category", "subcategory", "target", "cvss", "quality", "created_at", "resolved_at"]
now = datetime.now()
filename = "synstats-%s-%s-%s.csv"%(str(now.year),str(now.month),str(now.day))
with open(filename,"w") as f:
    writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(vulns_data)
