# Test: Missing Fields Validation (Job Model Compliance)

## Prompt for OpenCode:
```
Test if a job from Solr has ALL fields from the Job Model.

JOB MODEL FIELDS (11 total):
1. `url` (required) - string
2. `title` (required) - string
3. `company` (optional) - string (UPPERCASE!)
4. `cif` (optional) - string
5. `location` (optional) - string[]
6. `tags` (optional) - string[] (max 10)
7. `workmode` (optional) - string ("remote"/"on-site"/"hybrid")
8. `date` (optional) - pdate (ISO8601)
9. `status` (optional) - string ("scraped"/"tested"/"published"/"verified")
10. `vdate` (optional) - pdate (ISO8601)
11. `expirationdate` (optional) - pdate (ISO8601)

REQUIRED FIELDS (must be present):
- `url`
- `title`

TEST STEPS:
1. Get a job from Solr:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=*"

2. Check which fields are present vs missing from Job Model:
   - Required: url, title → MUST be present
   - Optional: if missing → can be added later

3. If REQUIRED field is missing (url or title):
   → This shouldn't happen (url is unique key, title should be set by scraper)
   → If title missing: DELETE job (invalid)

4. If OPTIONAL fields are missing:
   → Extract from job page / OLX API
   → Update with FULL PUSH including all fields

5. Verify update with FULL PUSH.

PASS CRITERIA:
- Required fields (url, title) are present
- If optional fields missing → extract and update with FULL PUSH
- Update uses FULL PUSH (not atomic update)
- Job has as many fields as possible (ideally all 11)

COMMAND TO CHECK MISSING FIELDS:
curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=<JOB_URL>&fl=*&wt=json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
doc = data['response']['docs'][0]
model_fields = ['url', 'title', 'company', 'cif', 'location', 'tags', 'workmode', 'date', 'status', 'vdate', 'expirationdate']
print('PRESENT:', [f for f in model_fields if f in doc])
print('MISSING:', [f for f in model_fields if f not in doc])
"
```
