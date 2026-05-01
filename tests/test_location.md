# Test: Location Field Validation

## Prompt for OpenCode:
```
Test the `location` field for a job from Solr.

VALIDATION RULES:
1. Location MUST be array of strings: ["City"] or ["City1", "City2"]
2. Use Romanian city names (e.g., "Bucuresti", "Cluj-Napoca", not "Bucharest")
3. Extract from:
   - OLX API: data.location.city.name
   - Job page: location mentions
4. Multiple locations possible (e.g., ["Bucuresti", "Cluj-Napoca"])

TEST STEPS:
1. Get a job from Solr: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=url,location,company"
2. Check if location is array format
3. If location is string (not array) → fix with FULL PUSH
4. Verify update

PASS CRITERIA:
- Location is an array: ["City"] or ["City1", "City2"]
- Uses Romanian city names
- Update uses FULL PUSH (not atomic update)
