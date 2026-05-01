# Test: Location Romania Validation

## Prompt for OpenCode:
```
Test if a job's location(s) are in Romania.

RULES:
1. Job MUST have at least ONE location in Romania
2. Romanian cities: "Bucuresti", "Cluj-Napoca", "Timisoara", "Iasi", "Constanta", "Brasov", etc.
3. If job has MULTIPLE locations and ANY is in Romania → VALID (keep job)
4. If NO location is in Romania → **DELETE FROM SOLR**

VALID ROMANIAN LOCATIONS:
- "Bucuresti", "Bucuresti Sectorul 1-6"
- "Cluj-Napoca", "Timisoara", "Iasi", "Constanta", "Brasov"
- "Ilfov", "Ilfov, Tunari", etc.
- Any Romanian county/city

NON-ROMANIAN LOCATIONS (DELETE if ALL are foreign):
- "New York", "London", "Berlin", "Paris", "San Francisco", etc.
- Multiple foreign cities with NO Romanian city → DELETE

TEST STEPS:
1. Get a job from Solr:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:published&rows=1&fl=url,location,title"

2. Check location array:
   - If location contains ANY Romanian city → VALID (process normally)
   - If ALL locations are outside Romania → **DELETE**:
     curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
       "https://solr.peviitor.ro/solr/job/update?commit=true" \
       -d '{"delete": ["<JOB_URL>"]}'

3. For jobs with multiple locations (some Romanian, some foreign):
   → VALID (keep it, Romanian jobseekers can apply)

4. If location field is empty/missing:
   → Open job URL in Chrome
   → Extract location from page
   → If not in Romania → DELETE

PASS CRITERIA:
- Job has at least one Romanian location → KEEP
- All locations are foreign → DELETE
- Multiple locations with at least one Romanian → KEEP

DELETE COMMAND (if no Romanian location):
curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -d '{"delete": ["<JOB_URL>"]}'

EXAMPLE:
- location: ["Bucuresti", "Cluj"] → KEEP (both Romanian)
- location: ["New York", "San Francisco"] → DELETE (no Romanian city)
- location: ["Bucuresti", "London"] → KEEP (has Romanian city)
```
