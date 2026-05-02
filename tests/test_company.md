# Test: Company Field Validation

## Prompt for OpenCode:
```
Test the `company` field for a job from Solr (status:verified or published).

VALIDATION RULES:
1. Company name MUST be UPPERCASE (e.g., "MEGA IMAGE SRL" not "Mega Image SRL")
2. Company name MUST match the LEGAL NAME from Trade Register (not just UPPERCASE)
3. Verify real company name using demoanaf.ro API: https://demoanaf.ro/api/company/<CIF>
4. If CIF missing → search web for "COMPANY NAME CIF Romania" → get CIF → verify on demoanaf.ro

TEST STEPS:
1. Get a job from Solr: 
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=url,company,cif"

2. Check if company field is UPPERCASE → if NOT, convert to UPPERCASE

3. **VERIFY LEGAL NAME VIA DEMOANAF.RO (CRITICAL!)**:
   - If CIF exists: curl -s "https://demoanaf.ro/api/company/<CIF>" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['name'] if d['success'] else 'ERROR')"
   - Compare demoanaf name with Solr company name
   - If DIFFERENT → update BOTH job and company cores with demoanaf legal name

4. Update with FULL PUSH (if needed):
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
     "https://solr.peviitor.ro/solr/job/update?commit=true" \
     -d '[{"url": "<URL>", "company": "<LEGAL_NAME_FROM_DEMOANAF>", ...ALL_OTHER_FIELDS...}]'

5. Update company core with legal name:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
     "https://solr.peviitor.ro/solr/company/update?commit=true" \
     -d '[{"id": "<CIF>", "company": "<LEGAL_NAME_FROM_DEMOANAF>", "lastScraped": "2026-05-01T00:00:00Z"}]'

6. Verify update: 
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<URL>&fl=company"

DEMOANAF API ENDPOINT:
- GET https://demoanaf.ro/api/company/<CIF> → returns {"success": true, "data": {"name": "...", "cui": ..., ...}}

PASS CRITERIA:
- Company name is UPPERCASE
- Company name matches LEGAL NAME from demoanaf.ro (not just UPPERCASE version of scraped name)
- Update uses FULL PUSH (not atomic update)
- Company core also updated with legal name
