# Technologies Used in peviitor-data-quality-guard

## Core Technologies

### Data Storage & Search
- **Apache Solr** - Search platform powering peviitor.ro
  - Job Core: `https://solr.peviitor.ro/solr/job`
  - Company Core: `https://solr.peviitor.ro/solr/company`
  - Schema: `https://solr.peviitor.ro/solr/job/schema`
  - Authentication: Basic Auth (`SOLR_USER`, `SOLR_PASSWD`)

### AI & Models
- **OpenCode AI** - Interactive CLI tool for software engineering tasks
  - Model: **big-pickle** (open:big-pickle)
  - Capabilities: Code editing, bash execution, web search, puppeteer automation

## Automation & Testing

### Browser Automation
- **Puppeteer** (Node.js)
  - Headless Chrome automation
  - Validates job pages (expired, 404, dynamic content)
  - Detects: "no longer available", "job filled", "ocupat"
  - Usage: `node -e "const puppeteer = require('puppeteer'); ..."`

### Scripting & Tools
- **Bash** - Shell commands, curl for Solr REST API
- **Python 3** - JSON processing with `json.tool`, data validation
- **Node.js** - Puppeteer scripts, JavaScript automation
- **curl** - HTTP requests to Solr, web APIs
  - Flags: `-g` (disable globbing), `-s` (silent), `-u` (auth)

## APIs & Data Sources

### peviitor.ro Platform
- **peviitor_core** - Data models (Job Model, Company Model)
  - GitHub: `https://github.com/peviitor-ro/peviitor_core`
  - README: `https://github.com/peviitor-ro/peviitor_core/blob/main/README.md`
- **peviitor API** - Job search
  - Endpoint: `https://api.peviitor.ro/v1/search/?page=1`

### External APIs
- **OLX API** - For OLX job verification
  - Endpoint: `https://www.olx.ro/api/v1/offers/<ID>`
- **ANAF API** - Company CIF validation
- **listafirme.ro**, **risco.ro**, **metricbiz.ro** - Romanian company data
- **WebSearch (Exa AI)** - Finding company CIF, validating information

## CI/CD & Workflows

### GitHub Actions
- **ubuntu-latest** runners (migrated from self-hosted pi400)
- **YAML workflows** (`.github/workflows/`)
  - `validate-jobs.yml` - Automated job validation
- **GitHub Secrets**:
  - `SOLR_USER` = "solr"
  - `SOLR_PASSWD` = "SolrRocks"

## Data Models & Validation

### Job Model (11 fields)
1. `url` (string, required) - Unique key
2. `title` (text_general, required)
3. `company` (string) - UPPERCASE
4. `cif` (string) - Numeric CIF/CUI
5. `location` (text_general[]) - Romanian cities
6. `tags` (text_general[]) - Max 10 tags
7. `workmode` (string) - "remote"/"on-site"/"hybrid"
8. `date` (pdate) - ISO8601
9. `status` (string) - "scraped"/"tested"/"published"/"verified"
10. `vdate` (pdate) - Verification date
11. `expirationdate` (pdate) - Date + 30 days

### Company Model (10 fields)
- `id` (string, required) - CIF/CUI
- `company` (string, required) - Legal name
- `brand`, `group`, `status`, `location`, `website`, `career`, `lastScraped`, `scraperFile`

## Validation Tests (`tests/` folder)
- `test_url.md` - 404, expired, not-a-job → DELETE
- `test_deleted_url.md` - Verify URL gone from Solr
- `test_location_romania.md` - Romanian cities check
- `test_missing_fields.md` - Verify all 11 Job Model fields
- `test_extra_fields.md` - Remove non-model fields
- `test_company.md` - UPPERCASE + ANAF verify
- `test_cif.md` - Numeric CIF verification
- `test_salary.md` - "MIN-MAX RON" array format (NO "0-0 RON"!)
- `test_workmode.md` - remote/on-site/hybrid only
- `test_tags.md` - Max 10 tags with experience level
- `test_location.md` - Array of Romanian cities
- `test_status_vdate.md` - Valid status + ISO8601
- `test_expirationdate.md` - Date + 30 days

## Key Workflows

### FULL PUSH (Complete Document Replace)
```bash
curl -X POST "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -u "solr:SolrRocks" -H "Content-Type: application/json" \
  -d '[{
    "url": "...",
    "title": "...",
    "company": "UPPERCASE",
    "cif": "12345678",
    "location": ["City1", "City2"],
    "tags": ["tag1", "tag2"],
    "workmode": "on-site",
    "date": "2026-05-01T00:00:00Z",
    "status": "verified",
    "vdate": "2026-05-01T12:00:00Z",
    "expirationdate": "2026-05-31T00:00:00Z"
  }]'
```

### DELETE Job
```bash
curl -X POST "https://solr.peviitor.ro/solr/job/update?commit=true" \
  -u "solr:SolrRocks" -H "Content-Type: application/json" \
  -d '{"delete": ["<JOB_URL>"]}'
```

### Puppeteer Validation (MANDATORY before DELETE)
```javascript
const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.goto(url, {timeout: 15000});
    await new Promise(r => setTimeout(r, 3000));
    const text = await page.evaluate(() => document.body.innerText);
    const expired = ['no longer available','expired','404','job filled','ocupat']
        .some(i => text.toLowerCase().includes(i));
    console.log(expired ? 'EXPIRED' : 'ACTIVE');
    await browser.close();
})();
```

## Critical Rules
1. **ALL JOBS ARE SUBJECT TO BE TESTED - NO EXCEPTIONS** (OLX, ADOBE, DELGAZ, EVERY job!)
2. **Process ONE BY ONE** - Never skip jobs
3. **FULL PUSH only** - Atomic updates create broken `/company#` suffixes
4. **Puppeteer MANDATORY** - HTTP 200 doesn't mean job is active (dynamic content!)
5. **If test FAILS → FIX → RETEST that job**
6. **Run ALL tests from `tests/` folder** for EVERY job
7. **test_deleted_url.md ONLY after DELETE action**

## Project Structure
```
peviitor-data-quality-guard/
├── INSTRUCTIONS.md          # Main workflow + test references
├── AGENTS.md               # Agent instructions + test references
├── TECHNOLOGIES.md         # This file - all technologies used
├── OLX.md                  # OLX API documentation
├── .github/workflows/      # GitHub Actions YAML
├── tests/                   # Validation tests (13 test files)
│   ├── test_url.md
│   ├── test_deleted_url.md
│   └── ... (11 more)
└── .gitignore
```
