# Test: Extra Fields Validation (Remove Unnecessary Fields)

## Prompt for OpenCode:
```
Test if a job from Solr has EXTRA fields not in the Job Model, and remove them.

JOB MODEL FIELDS (11 total):
1. `url` (required)
2. `title` (required)
3. `company` (optional)
4. `cif` (optional)
5. `location` (optional)
6. `tags` (optional)
7. `workmode` (optional)
8. `date` (optional)
9. `status` (optional)
10. `vdate` (optional)
11. `expirationdate` (optional)

EXTRA FIELDS TO REMOVE:
- `description` (too long, not needed)
- `description_html` (not needed)
- `scraperFile` (not in model)
- `lastScraped` (not in model)
- Any other custom fields not in the 11 fields above

TEST STEPS:
1. Get a job from Solr with ALL fields:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=*"

2. List all fields present in the job document:
   python3 -c "
   import sys, json
   data = json.load(sys.stdin)
   doc = data['response']['docs'][0]
   model_fields = ['url', 'title', 'company', 'cif', 'location', 'tags', 'workmode', 'date', 'status', 'vdate', 'expirationdate']
   extra = [f for f in doc.keys() if f not in model_fields and not f.startswith('_')]
   print('EXTRA FIELDS:', extra)
   "

3. If EXTRA fields exist → Remove them with FULL PUSH:
   - Get ALL valid fields (11 fields) from the job
   - Create new document with ONLY the 11 Job Model fields
   - Use FULL PUSH: `[{"url": "...", "title": "...", ...}]` (only model fields)

4. Verify update:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<URL>&fl=*&wt=json"

PASS CRITERIA:
- Job has ONLY the 11 Job Model fields (no extra fields)
- Extra fields like `description`, `scraperFile`, etc. are removed
- Update uses FULL PUSH (send only valid fields, extra fields are dropped)
- `_version_` and `_root_` are internal Solr fields (ok to keep)

COMMAND TO REMOVE EXTRA FIELDS:
1. Get current job: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<URL>&fl=*&wt=json"
2. Extract only model fields:
   python3 -c "
   import sys, json
   data = json.load(sys.stdin)
   doc = data['response']['docs'][0]
   model_fields = ['url', 'title', 'company', 'cif', 'location', 'tags', 'workmode', 'date', 'status', 'vdate', 'expirationdate']
   clean_doc = {k: v for k, v in doc.items() if k in model_fields}
   print(json.dumps([clean_doc]))
   "
3. Update with FULL PUSH:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
     "https://solr.peviitor.ro/solr/job/update?commit=true" \
     -d '[{"url": "...", "title": "...", ...}]'  # only model fields
```
