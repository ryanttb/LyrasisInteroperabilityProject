#!/usr/bin/env python3
import json
import re
import sys

path = sys.argv[1]
with open(path) as f:
    d = json.load(f)

for i in sorted(d["items"], key=lambda x: x["title"]):
    m = re.search(r"Behavior Scenario ([A-Z][0-9, ]+):", i["title"])
    sid = m.group(1).replace(" ", "") if m else "?"
    labels = [l["name"] for l in i.get("labels", [])]
    print(f"{sid}\t#{i['number']}\t{i['state']}\t{i['title']}\t{i['html_url']}\t{','.join(labels)}")
