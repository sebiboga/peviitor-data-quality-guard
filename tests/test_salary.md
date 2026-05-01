# Test: Salary Field Validation

## Prompt for OpenCode:
```
Test the `salary` field for a job from Solr.

VALIDATION RULES:
1. Format MUST be "MIN-MAX CURRENCY" (e.g., "3200-4300 RON")
2. Convert "lei" to "RON"
3. If single salary (e.g., "3200 RON") → keep as "3200-3200 RON" or "3200 RON"
4. Salary must be array: ["MIN-MAX RON"]
5. Extract from job page or OLX API (salary.from + salary.to)

TEST STEPS:
1. Get a job from Solr: curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:verified&rows=1&fl=url,salary,company"
2. Check salary format matches "MIN-MAX RON" (array)
3. If wrong format → extract correct salary and update with FULL PUSH
4. Verify update

PASS CRITERIA:
- Salary is in format "MIN-MAX RON" (or "MIN RON")
- Salary is an array: ["3200-4300 RON"]
- Currency is RON (not lei, EUR, etc.)
- **INVALID salaries: "0-0 RON", "0 RON", empty, null → OMIT the salary field completely!**
- Update uses FULL PUSH (not atomic update)

INVALID SALARY EXAMPLES (MUST BE OMITTED):
- "0-0 RON" ❌
- "0 RON" ❌
- "" ❌
- null ❌
- [] ❌
