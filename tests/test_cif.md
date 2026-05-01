# Test: CIF Field Validation

## Prompt for OpenCode:
```
Test the `cif` field for a job from Solr.

VALIDATION RULES:
1. CIF must be numeric (Romanian CUI/CIF format)
2. If CIF is missing → search web: "COMPANY NAME CIF Romania"
3. Verify CIF on ANAF: https://static.anaf.ro/static/10/Anaf/codfiscal.html?cod=<CIF>
4. Check companies in Solr company core: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/company/select?q=id:<CIF>"

TEST STEPS:
1. Get a job without CIF: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=-cif:[*+TO+*]&rows=1&fl=url,company"
2. Search web for company CIF
3. Update with FULL PUSH including CIF
4. Verify CIF is set correctly

PASS CRITERIA:
- CIF is numeric (e.g., "6719278")
- CIF exists in Romanian Trade Register
- Update uses FULL PUSH (not atomic update)
