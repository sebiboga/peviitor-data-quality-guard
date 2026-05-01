# Test: Company Field Validation

## Prompt for OpenCode:
```
Test the `company` field for a job from Solr (status:verified or published).

VALIDATION RULES:
1. Company name MUST be UPPERCASE (e.g., "MEGA IMAGE SRL" not "Mega Image SRL")
2. If company name is lowercase/mixed case → transform to UPPERCASE
3. Check company CUI from ANAF or listafirme.ro to verify real name
4. Company should match the legal name from Trade Register

TEST STEPS:
1. Get a job from Solr: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=url,company,cif"
2. Check if company field is UPPERCASE
3. If NOT → update with FULL PUSH:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
     "https://solr.peviitor.ro/solr/job/update?commit=true" \
     -d '[{"url": "<URL>", "company": "<UPPERCASE_NAME>", ...ALL_OTHER_FIELDS...}]'
4. Verify update: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<URL>&fl=company"

PASS CRITERIA:
- Company name is UPPERCASE
- Company matches legal name (from CUI check)
- Update uses FULL PUSH (not atomic update)
