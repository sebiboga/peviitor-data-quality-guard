# Agent Instructions

When working with this project, follow these steps:

## 1. Read Documentation First
- Start by reading `INSTRUCTIONS.md` in this directory to understand the project context
- Check for any existing documentation before making assumptions

## 2. Job & Company Models
To understand the data models:
1. Fetch from GitHub: `https://github.com/peviitor-ro/peviitor_core/blob/main/README.md`
2. Or use the cached info in `INSTRUCTIONS.md`

## 3. Accessing Solr Schemas
When asked to read Solr schemas:

### Job Core
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/schema"
```

### Company Core
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/company/schema"
```

**Important**: 
- Use `curl` with `-u "$SOLR_USER:$SOLR_PASSWD"` for Basic Auth (or GitHub secrets)
- WebFetch alone won't work due to 401 errors - curl/bash is required
- Do NOT hardcode credentials - use environment variables or GitHub secrets

## 4. Key Differences from Documentation
- The README in peviitor_core describes the conceptual model
- The Solr schemas show the actual implementation (field types, indexing)
- Some fields may differ slightly between conceptual and implementation

## 5. Authentication
- Solr credentials: Use `SOLR_USER` and `SOLR_PASSWD` environment variables or GitHub secrets (`secrets.SOLR_USER`, `secrets.SOLR_PASSWD`)
- Always use Basic Auth via curl `-u` flag

## 6. Verification Workflow (from peviitor.ro first page)

### Step 1: Get Jobs from API
```bash
curl -s "https://api.peviitor.ro/v1/search/?page=1"
```
This returns the first page of jobs with their URLs.

### Step 2: Check Each Job URL
For each job URL:
1. Open the URL in Chrome using Chrome DevTools (`chrome-devtools_navigate_page`)
2. Take a snapshot to see the content
3. **CHECK FOR 404 / EXPIRED**:
   - If HTTP 404 error → **DELETE from Solr immediately**
   - If page contains: "expired", "no longer available", "anunt expirat", "locul nu mai este disponibil" → **DELETE from Solr immediately**
4. Determine if it's a **real job** or **NOT a job**:
   - **NOT a job** (delete): Employee testimonials, company culture pages, "Meet our team" pages, 404 errors, expired jobs
   - **Real job**: Has job title, responsibilities, requirements, apply button/form

**DELETE CONDITIONS:**
- HTTP 404 error → `curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" "https://solr.peviitor.ro/solr/job/update?commit=true" -d '{"delete": ["<JOB_URL>"]}'`
- Page shows "expired", "anunt expirat" → DELETE
- Not a real job (testimonial, company page) → DELETE

### Step 3: For Real Jobs - Extract Data
From the job page, extract:
- **company**: Company name visible on page (convert to UPPERCASE)
- **cif**: Search web for "COMPANY NAME CIF Romania" if not on page
- **salary**: "MIN-MAX RON" format (convert "lei" to "RON")
- **workmode**: "remote", "on-site", or "hybrid" (check job location flexibility)
- **tags** (max 10): Include:
  - Experience level: entry-level, mid-level, senior-level
  - Job type: full-time, part-time, internship
  - Contract: permanent-contract, temporary
  - Skills/industry: retail, IT, marketing, etc.
  - Other: students, flexible-schedule, qualified, etc.

### Step 4: Update Company Core
If company is new or needs updating:
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/company/update?commit=true" \
  -d "{\"add\": {\"doc\": {\"id\": \"<CIF>\", \
  \"company\": {\"set\": \"<company_name>\"}, \
  \"brand\": {\"set\": \"<brand>\"}, \
  \"website\": {\"set\": [\"<website>\"]}, \
  \"career\": {\"set\": [\"<career_page>\"]}, \
  \"lastScraped\": {\"set\": \"2026-03-09T00:00:00Z\"}}}}"
```

### Step 5: Push Job Update
Use atomic update with today's date:
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -d "{\"add\": {\"doc\": {\"url\": \"<JOB_URL>\", \
  \"company\": {\"set\": \"<company>\"}, \
  \"cif\": {\"set\": \"<cif>\"}, \
  \"salary\": {\"set\": \"<salary>\"}, \
  \"workmode\": {\"set\": \"<workmode>\"}, \
  \"tags\": {\"set\": [\"tag1\", \"tag2\"]}, \
  \"status\": {\"set\": \"verified\"}, \
  \"vdate\": {\"set\": \"2026-03-09T00:00:00Z\"}}}}"
```

### Step 6: Verify the Update
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<JOB_URL>&wt=json"
```

### Step 7: Delete Non-Job Pages
If URL is not a real job:
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -d "{\"delete\": [\"<JOB_URL>\"]}"
```

## 7. OLX Jobs
See [OLX.md](./OLX.md) for how to verify and scrape OLX jobs using their official API.

## 8. Testing All Job Fields
**CRITICAL**: After validating a job, run ALL tests in `tests/` folder:

### Required Tests for Each Job:
0. **URL** (`tests/test_url.md`): Check 404, expired, not-a-job → DELETE if invalid
1. **Missing Fields** (`tests/test_missing_fields.md`): Verify ALL 11 Job Model fields are present
2. **Company** (`tests/test_company.md`): Must be UPPERCASE, verify via web search
3. **CIF** (`tests/test_cif.md`): Must be numeric, verify on ANAF/listafirme.ro
4. **Salary** (`tests/test_salary.md`): Format "MIN-MAX RON", must be array
5. **Workmode** (`tests/test_workmode.md`): Only "remote", "on-site", "hybrid"
6. **Tags** (`tests/test_tags.md`): Max 10 tags, include experience level
7. **Location** (`tests/test_location.md`): Array of Romanian city names
8. **Status/Vdate** (`tests/test_status_vdate.md`): Valid status, ISO8601 format
9. **Expirationdate** (`tests/test_expirationdate.md`): Scrape date + 30 days

### Test Execution:
For each test file:
1. Read the test prompt from `tests/<test_file>.md`
2. Execute the validation steps
3. If invalid → update with **FULL PUSH** (not atomic update!)
4. Verify the field is correctly set in Solr

**Remember**: "Run tests from `tests/` folder for EVERY job field!"
