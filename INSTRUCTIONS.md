# Instructions for Working with Peviitor Project

This directory contains project files for interacting with the peviitor.ro job search platform.

## Key Resources

### 1. Job & Company Models
Read the README from peviitor-core to understand the data models:
- **URL**: https://github.com/peviitor-ro/peviitor_core/blob/main/README.md
- **Content**: Job Model Schema and Company Model Schema

### 2. Solr Schemas
Access the live Solr instance to see the actual field definitions:
- **Base URL**: https://solr.peviitor.ro
- **Authentication**: Use `SOLR_USER` and `SOLR_PASSWD` environment variables or GitHub secrets

#### Job Core Schema
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/schema"
```

#### Company Core Schema
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/company/schema"
```

## Job Model Fields (from Solr)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Full URL to job detail page (unique key) |
| `title` | text_general | Yes | Position title |
| `company` | string | No | Hiring company name (UPPERCASE) |
| `cif` | string | No | CIF/CUI of the company |
| `location` | text_general[] | No | Romanian cities/addresses |
| `tags` | text_general[] | No | Skills/education/experience (max 10) |
| `workmode` | string | No | "remote", "on-site", "hybrid" |
| `date` | pdate | No | Scrape date (ISO8601) |
| `status` | string | No | "scraped", "tested", "published", "verified" |
| `vdate` | pdate | No | Verified date |
| `expirationdate` | pdate | No | Job expiration date |
| `salary` | text_general | No | Format: "MIN-MAX CURRENCY" |

**IMPORTANT**: When doing FULL PUSH, include ALL fields that are present. Missing fields will be deleted!

## Company Model Fields (from Solr)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | CIF/CUI (unique key) |
| `company` | string | Yes | Legal name from Trade Register |
| `brand` | string | No | Commercial brand name |
| `group` | string | No | Parent company group |
| `status` | string | No | "activ", "suspendat", "inactiv", "radiat" |
| `location` | text_general | No | Romanian cities/addresses |
| `website` | string[] | No | Official company website(s) |
| `career` | string[] | No | Career page URL(s) |
| `lastScraped` | string | No | Last scrape date (ISO8601) |
| `scraperFile` | string | No | Name of scraper file used |

## Workflow: Verifying Jobs from peviitor.ro First Page

### Step 1: Get Jobs from peviitor.ro API
Query the peviitor.ro API to get the first page of jobs:
```bash
curl -s "https://api.peviitor.ro/v1/search/?page=1"
```

### Step 2: Check Each Job URL
For each job URL from the API:
1. Open the URL in Chrome using Chrome DevTools
2. Determine if it's a **real job** or **not a job** (testimonials, company pages, etc.)
3. If NOT a real job (e.g., employee testimonials, company culture pages) → **DELETE from Solr**
4. If real job → proceed to extract data

### Step 3: For Real Jobs - Extract & Verify Data
Scrape the following from the job page:
- **company**: Company name (from page, convert to UPPERCASE)
- **cif**: Company CIF/CUI (search web if not on page)
- **salary**: Format "MIN-MAX RON" (convert "lei" to "RON")
- **workmode**: "remote", "on-site", or "hybrid" (check if job is in office, remote, or hybrid)
- **tags**: Up to 10 tags - include:
  - Experience level: entry-level, mid-level, senior-level
  - Skills/industry (e.g., "retail", "IT", "marketing")
  - Job type: "full-time", "part-time", "internship"
  - Contract: "permanent-contract", "temporary"
  - Other: "students", "flexible-schedule", "qualified", etc.

### Step 4: Find Company CIF
If CIF not visible on page:
1. Search web for "COMPANY NAME CIF Romania"
2. Use sources like listafirme.eu, risco.ro, or firme.ro
3. Also check if company already exists in Solr company core

### Step 5: Update Company Core (if new/needed)
Use **FULL PUSH** (complete document replace) - NOT atomic update:
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/company/update?commit=true" \
  -d "[{\"id\": \"<CIF>\", \
  \"company\": \"<company_name>\", \
  \"brand\": \"<brand_name>\", \
  \"website\": [\"<website>\"], \
  \"career\": [\"<career_page>\"], \
  \"lastScraped\": \"2026-03-09T00:00:00Z\"}]"
```

### Step 6: Push Job Update to SOLR
Use **FULL PUSH** (complete document replace) - NOT atomic update (which creates broken entries with /company#, /cif# suffixes):
```bash
curl -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
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

### Step 7: Verify the Update in SOLR
Always query SOLR to confirm all fields were updated correctly:
```bash
curl -g -u "$SOLR_USER:$SOLR_PASSWD" "https://solr.peviitor.ro/solr/job/select?q=url:<JOB_URL>&wt=json&fl=*"
```

### Step 8: Handle Non-Job Pages
If the URL is not a job description (testimonial, company page, etc.):
```bash
curl -g -u "$SOLR_USER:$SOLR_PASSWD" -X POST -H "Content-Type: application/json" \
  "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -d "{\"delete\": [\"<JOB_URL>\"]}"
```

## OLX Jobs
See [OLX.md](./OLX.md) for how to verify and scrape OLX jobs using their official API.

## Notes
- Use `curl` with `-u "$SOLR_USER:$SOLR_PASSWD"` for authentication (or GitHub secrets `SOLR_USER`/`SOLR_PASSWD`)
- The Solr instance uses `text_general` field type for most text fields
- Both cores have copy fields that aggregate text to `_text_` for full-text search
