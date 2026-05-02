#!/usr/bin/env python3
import sys, json, os

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        data = json.load(f)
else:
    data = json.load(sys.stdin)

if data['response']['numFound'] == 0:
    print('NO JOBS IN SOLR')
    sys.exit(1)

doc = data['response']['docs'][0]
vdate = doc.get('vdate', '')
today = os.environ.get('TODAY', '')

print('JOB FROM SOLR:')
print(f"URL: {doc.get('url', 'N/A')}")
print(f"Title: {doc.get('title', 'N/A')}")
print(f"Company: {doc.get('company', 'N/A')}")
print(f"Location: {doc.get('location', 'N/A')}")
print(f"Date: {doc.get('date', 'N/A')}")
print(f"Status: {doc.get('status', 'N/A')}")
print(f"vdate: {vdate if vdate else 'MISSING'}")
print()

if vdate and vdate.startswith(today):
    print('DECISION: SKIP (already validated today)')
    sys.exit(2)
else:
    print('DECISION: TAKE (job to validate)')
    with open('/tmp/job_url.txt', 'w') as f:
        f.write(doc['url'])
    with open('/tmp/job_data.json', 'w') as f:
        json.dump(doc, f)
