# Test: Deleted URL Not in Solr

## Prompt for OpenCode:
```
Test that a deleted job URL is NO longer present in Solr.

RULES:
1. When a job is deleted from Solr (via {"delete": ["<URL>"]}), it should NOT appear in any Solr query
2. Verify deletion by searching for the URL in Solr
3. If URL still exists → deletion failed (try again or check permissions)

TEST STEPS:
1. After deleting a job URL:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
     "https://solr.peviitor.ro/solr/job/update?commit=true" \
     -d '{"delete": ["<JOB_URL>"]}'

2. Verify deletion (URL should NOT be found):
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<JOB_URL>&wt=json&fl=url"

3. Check response:
   - If "numFound": 0 → ✅ DELETION SUCCESSFUL
   - If "numFound": 1 → ❌ DELETION FAILED (URL still in Solr)

4. Alternative verification (using wildcard):
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:*PARTIAL_SLUG*&wt=json&fl=url"

PASS CRITERIA:
- Deleted URL returns "numFound": 0 in Solr
- URL is completely removed from Solr index
- No trace of deleted URL in any Solr query

VERIFICATION COMMANDS:
# Check if URL still exists
curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<JOB_URL>&wt=json&fl=url"

# Expected SUCCESS response:
{
  "response": {
    "numFound": 0,  # ✅ GONE!
    "docs": []
  }
}

# Expected FAILURE response:
{
  "response": {
    "numFound": 1,  # ❌ STILL THERE!
    "docs": [{"url": "<JOB_URL>"}]
  }
}

# Check with wildcard (if full URL unknown)
curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:*PARTIAL*&wt=json&fl=url"
```
