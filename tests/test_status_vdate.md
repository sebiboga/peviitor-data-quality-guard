# Test: Status and Vdate Fields Validation

## Prompt for OpenCode:
```
Test the `status` and `vdate` fields for a job from Solr.

VALIDATION RULES:
1. Status MUST be one of: "scraped", "tested", "published", "verified"
2. Vdate = verification date (ISO8601 format: "2026-05-01T00:00:00Z")
3. Status transitions:
   - "scraped" → "tested" (URL works but not fully scraped / CAPTCHA blocked)
   - "scraped" → "verified" (fully scraped with all details)
   - "tested" → "verified" (after full scrape)
   - NOT a job → DELETE from Solr
4. Vdate should be set when status changes to "verified" or "tested"

TEST STEPS:
1. Get a job: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:scraped&rows=1&fl=url,status,vdate"
2. Process the job (open in Chrome or check OLX API)
3. Update status to "verified" or "tested" with vdate = today
4. Verify update

PASS CRITERIA:
- Status is valid value
- Vdate is set when status is "verified" or "tested"
- Vdate format is ISO8601: "YYYY-MM-DDTHH:MM:SSZ"
- Update uses FULL PUSH (not atomic update)
