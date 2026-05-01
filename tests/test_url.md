# Test: URL Validation (404, Expired, Not a Job)

## Prompt for OpenCode:
```
Test the job URL for 404 errors, expired jobs, or non-job pages.

VALIDATION RULES:
1. **HTTP 404 / Page Not Found** → DELETE from Solr immediately
2. **Page contains expiration text** → DELETE from Solr immediately
   - Text to check: "expired", "no longer available", "anunt expirat", "locul nu mai este disponibil", "job expired", "oferta a expirat"
3. **Not a job description** → DELETE from Solr
   - Employee testimonials
   - Company culture pages ("Meet our team", "About us")
   - "What does X do" articles
   - Company career pages (no specific job)

TEST STEPS:
1. Get a job URL from Solr: 
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=status:published&rows=1&fl=url,title"

2. Open the URL in Chrome using chrome-devtools:
   - Use `chrome-devtools_navigate_page` to open URL
   - Take snapshot to see content
   - Check HTTP status (if accessible via chrome-devtools)

3. **CHECK FOR DELETE CONDITIONS:**
   a) If HTTP 404 → DELETE:
      curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
        "https://solr.peviitor.ro/solr/job/update?commit=true" \
        -d '{"delete": ["<URL>"]}'
   
   b) If page contains "expired"/"anunt expirat" → DELETE (same command)
   
   c) If not a real job (testimonial/company page) → DELETE (same command)

4. Verify deletion:
   curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<URL>&wt=json"

PASS CRITERIA:
- URL returning HTTP 404 → job is deleted from Solr
- Page with "expired"/"anunt expirat" text → job is deleted from Solr
- Non-job pages (testimonials, company pages) → job is deleted from Solr
- Real jobs with valid descriptions → proceed to field extraction (other tests)

DELETE COMMAND:
curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -d '{"delete": ["<JOB_URL>"]}'
```
