# Test: Workmode Field Validation

## Prompt for OpenCode:
```
Test the `workmode` field for a job from Solr.

VALIDATION RULES:
1. MUST be one of: "remote", "on-site", or "hybrid"
2. Extract from job page:
   - "remote" / "de acasa" / "work from home" → remote
   - "hybrid" / "mix" → hybrid
   - Physical office / shop / store → on-site (default)
3. Check OLX API params for remote flags: data.params[] where key="remote_recruitment"

TEST STEPS:
1. Get a job without workmode: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=-workmode:[*+TO+*]&rows=1&fl=url,company,workmode"
2. Open job URL or check OLX API for workmode indicators
3. Update with FULL PUSH including workmode
4. Verify update

PASS CRITERIA:
- Workmode is exactly "remote", "on-site", or "hybrid"
- No other values allowed
- Update uses FULL PUSH (not atomic update)
