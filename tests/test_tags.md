# Test: Tags Field Validation

## Prompt for OpenCode:
```
Test the `tags` field for a job from Solr.

VALIDATION RULES:
1. Tags MUST be array of strings: ["tag1", "tag2", ...]
2. Max 10 tags per job
3. Include these types:
   - Experience level: "entry-level", "mid-level", "senior-level"
   - Job type: "full-time", "part-time", "internship"
   - Contract: "permanent-contract", "temporary", "contract"
   - Skills/industry: "retail", "IT", "marketing", "cashier", etc.
   - Other: "students", "flexible-schedule", "qualified"
4. Extract from OLX API params[]:
   - key="type" → full-time/part-time
   - key="nivel_experienta" → entry/mid/senior
   - key="program_demunca" → schedule type
   - key="open_for_students" → students

TEST STEPS:
1. Get a job from Solr: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=url,tags,company"
2. Check if tags array has relevant items (experience, job type, etc.)
3. If missing key tags → extract from job page/OLX API and update with FULL PUSH
4. Verify update (max 10 tags)

PASS CRITERIA:
- Tags is an array: ["tag1", "tag2", ...]
- At least 1 tag present
- Max 10 tags
- Includes experience level OR job type
- Update uses FULL PUSH (not atomic update)
