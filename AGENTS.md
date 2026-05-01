# Agent Instructions

When working with this project, follow these steps:

## CRITICAL: Process Jobs ONE BY ONE
**NEVER skip any job!** Process each job individually:
1. Take ONE job from Solr (sorted by date asc, without CIF, excluding none)
2. Run ALL tests from `tests/` folder on THAT job
3. If test FAILS → FIX the problem → RETEST that job
4. Only AFTER tests pass → move to next job
5. Repeat until all jobs are processed

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
1. **CHECK FOR 404 / EXPIRED**:
   - If HTTP 404 error → **DELETE from Solr immediately**
   - If page contains: "expired", "no longer available", "anunt expirat", "locul nu mai este disponibil" → **DELETE from Solr immediately**
2. Determine if it's a **real job** or **NOT a job**:
   - **NOT a job** (delete): Employee testimonials, company culture pages, "Meet our team" pages, 404 errors, expired jobs
   - **Real job**: Has job title, responsibilities, requirements, apply button/form

**DELETE CONDITIONS:**
- HTTP 404 error → `curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" "https://solr.peviitor.ro/solr/job/update?commit=true" -d '{"delete": ["<JOB_URL>"]}'`
- Page shows "expired", "anunt expirat" → DELETE
- Not a real job (testimonial, company page) → DELETE

### Step 2b: Validate with Puppeteer (MANDATORY before DELETE)
**CRITICAL**: Never delete a job without verifying with puppeteer first! Some sites (AECOM, Oracle) return HTTP 200 but show "job filled" dynamically.

Use this Node.js script:
```bash
node -e "
const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch({headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox']});
    const page = await browser.newPage();
    await page.goto('URL_HERE', {timeout: 15000});
    await new Promise(r => setTimeout(r, 3000));
    const text = await page.evaluate(() => document.body.innerText);
    const expired = ['no longer available','expired','404','job filled','ocupat','închis','similar jobs','joburi similare'].some(i => text.toLowerCase().includes(i));
    console.log(expired ? 'EXPIRED' : 'ACTIVE');
    await browser.close();
})();
"
```

**Why puppeteer?** Curl only checks HTTP status. Puppeteer executes JavaScript and reads the actual page content after dynamic loading!

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
Use **FULL PUSH** (complete document array) - NOT atomic update (which creates broken entries with /company#, /cif# suffixes):

**FULL PUSH Format (WRAP IN ARRAY):**
```bash
curl -u "$SOLR_AUTH" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -d "[{\"url\": \"<JOB_URL>\", \
  \"title\": \"<title>\", \
  \"company\": \"<company>\", \
  \"cif\": \"<cif>\", \
  \"location\": [\"<city>\"], \
  \"salary\": [\"<salary>\"], \
  \"workmode\": \"<workmode>\", \
  \"tags\": [\"tag1\", \"tag2\"], \
  \"status\": \"verified\", \
  \"date\": \"<scrape_date>\", \
  \"vdate\": \"2026-05-01T00:00:00Z\"}]"
```

**Important:** 
- Wrap document in `[...]` (array)
- Include ALL fields that are present (missing fields will be deleted!)

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
**CRITICAL RULE: ALL JOBS ARE SUBJECT TO BE TESTED - WE DO NOT SKIP ANY JOB BY ANY MEANS!!!**

This means:
- OLX jobs → TEST
- ADOBE jobs → TEST
- DELGAZ jobs → TEST
- EVERY job in Solr → TEST

**CRITICAL RETEST RULE: If any test is FAILING we DO FIX all problems then we RETEST that job once again!**

**ALL TESTS FOR EACH JOB:**
- `tests/test_url.md` - Check URL validity (404, expired, not-a-job)
- `tests/test_deleted_url.md` - **RUN ONLY AFTER DELETE ACTION**
- `tests/test_location_romania.md` - Check Romanian cities
- `tests/test_missing_fields.md` - Verify all 11 Job Model fields
- `tests/test_extra_fields.md` - Remove non-model fields
- `tests/test_company.md` - UPPERCASE + ANAF verify
- `tests/test_cif.md` - Numeric CIF verification
- `tests/test_salary.md` - "MIN-MAX RON" array format
- `tests/test_workmode.md` - remote/on-site/hybrid only
- `tests/test_tags.md` - Max 10 tags with experience level
- `tests/test_location.md` - Array of Romanian cities
- `tests/test_status_vdate.md` - Valid status + ISO8601
- `tests/test_expirationdate.md` - Date + 30 days

**CRITICAL**: Run ALL applicable tests for EVERY job before marking complete!

### Required Tests for Each Job:
0. **URL** (`tests/test_url.md`): Check 404, expired, not-a-job → DELETE if invalid
1. **Deleted URL** (`tests/test_deleted_url.md`): Verify deleted URL is NO longer in Solr
2. **Location Romania** (`tests/test_location_romania.md`): MUST have at least one Romanian city → DELETE if ALL foreign
3. **Missing Fields** (`tests/test_missing_fields.md`): Verify ALL 11 Job Model fields are present
4. **Company** (`tests/test_company.md`): Must be UPPERCASE, verify via web search
5. **CIF** (`tests/test_cif.md`): Must be numeric, verify on ANAF/listafirme.ro
6. **Salary** (`tests/test_salary.md`): Format "MIN-MAX RON", must be array
7. **Workmode** (`tests/test_workmode.md`): Only "remote", "on-site", "hybrid"
8. **Tags** (`tests/test_tags.md`): Max 10 tags, include experience level
9. **Location** (`tests/test_location.md`): Array of Romanian city names
10. **Status/Vdate** (`tests/test_status_vdate.md`): Valid status, ISO8601 format
11. **Expirationdate** (`tests/test_expirationdate.md`): Scrape date + 30 days

### Test Execution:
For each test file:
1. Read the test prompt from `tests/<test_file>.md`
2. Execute the validation steps
3. If invalid → update with **FULL PUSH** (not atomic update!)
4. Verify the field is correctly set in Solr

**Remember**: "Run tests from `tests/` folder for EVERY job field!"
