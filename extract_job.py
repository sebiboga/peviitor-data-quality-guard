#!/usr/bin/env python3
import sys, json, os

# Citește din fișier dacă e specificat, altfel din stdin
if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        data = json.load(f)
else:
    data = json.load(sys.stdin)

if data['response']['numFound'] == 0:
    print('NU MAI SUNT JOBURI ÎN SOLR')
    sys.exit(1)

doc = data['response']['docs'][0]
vdate = doc.get('vdate', '')
today = os.environ.get('TODAY', '')

print('JOB EXTRAS DIN SOLR:')
print(f"URL: {doc.get('url', 'N/A')}")
print(f"Title: {doc.get('title', 'N/A')}")
print(f"Company: {doc.get('company', 'N/A')}")
print(f"Location: {doc.get('location', 'N/A')}")
print(f"Date: {doc.get('date', 'N/A')}")
print(f"Status: {doc.get('status', 'N/A')}")
print(f"vdate: {vdate if vdate else 'LIPSĂ'}")
print()

# FIX: Verifică că vdate nu e gol și începe cu today
if vdate and vdate.startswith(today):
    print('DECIZIE: SKIP (vdate începe cu azi)')
    print('JOB DEJA VALIDAT ASTĂZI')
    sys.exit(2)
else:
    print('DECIZIE: TAKE (job de validat)')
    with open('/tmp/job_url.txt', 'w') as f:
        f.write(doc['url'])
    with open('/tmp/job_data.json', 'w') as f:
        json.dump(doc, f)
