# Peviitor Job Validator

This project validates jobs from Solr by checking if the job URLs are still available and updating the job data.

## Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── validate-jobs.yml      # Main validation workflow
│       └── test-page-1.yml        # Test page 1 workflow
├── AGENTS.md                      # Agent instructions
├── INSTRUCTIONS.md                # Detailed instructions
├── OLX.md                         # OLX API documentation
├── opencode.json                  # OpenCode configuration
├── start-chrome.ps1               # Chrome startup script (Windows)
├── .gitignore
└── README.md
```

## Workflow

The GitHub Actions workflow (`validate-jobs.yml`) runs every 5 minutes and:

1. Queries Solr for jobs with `status: scraped`
2. Opens each job URL in Chrome
3. Verifies job data (salary, tags, workmode, etc.)
4. If job is expired: deletes from Solr
5. If job is valid: updates with `status: verified` and today's date
6. Verifies the update in Solr

## Manual Run

You can manually trigger the workflow from GitHub Actions or use the `workflow_dispatch` input to specify how many jobs to validate.

## Solr Credentials

Set the following secrets in your GitHub repository:
- `SOLR_USER`: Solr username
- `SOLR_PASSWD`: Solr password

## Local Development

1. Start Chrome with remote debugging:
   ```bash
   google-chrome --remote-debugging-port=9222
   ```
   
   Or on Windows:
   ```powershell
   .\start-chrome.ps1
   ```

2. Configure OpenCode with your credentials in environment variables

3. Follow the workflow in `INSTRUCTIONS.md` and `AGENTS.md`
