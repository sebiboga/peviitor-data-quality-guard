# Test: Expirationdate Field Validation

## Prompt for OpenCode:
```
Test the `expirationdate` field for a job from Solr.

VALIDATION RULES:
1. Expirationdate = scrape date + 30 days (if not set)
2. Format: ISO8601 ("YYYY-MM-DDTHH:MM:SSZ")
3. If job is from OLX: check API `valid_to_time` field
4. If job is expired → DELETE from Solr

TEST STEPS:
1. Get a job without expirationdate: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=-expirationdate:[*+TO+*]&rows=1&fl=url,date,expirationdate,company"
2. Calculate expirationdate = date + 30 days
3. Update with FULL PUSH including expirationdate
4. Verify update

PASS CRITERIA:
- Expirationdate is set (date + 30 days)
- Format is ISO8601
- If job is expired → job is deleted from Solr
- Update uses FULL PUSH (not atomic update)
