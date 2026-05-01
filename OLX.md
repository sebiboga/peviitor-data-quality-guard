# OLX Jobs - API-Based Verification

OLX job listings require using the official OLX API instead of web scraping (OLX has CAPTCHA protection).

## OLX API Endpoints

### 1. List Jobs (with pagination)
```bash
curl -s "https://www.olx.ro/api/v1/offers/?offset=0&limit=50&category_id=4&currency=RON"
```

**Query Parameters:**
| Parameter | Description |
|-----------|-------------|
| `offset` | Pagination offset (0, 50, 100, ...) |
| `limit` | Results per page (max 50) |
| `category_id=4` | Jobs category |
| `currency=RON` | Filter by RON currency |

### 2. Get Single Job Details
```bash
curl -s "https://www.olx.ro/api/v1/offers/<OFFER_ID>/"
```
Replace `<OFFER_ID>` with the numeric ID from the job URL (e.g., `300079886` from `.../IDkj6ua.html`).

## OLX API Response Fields

From the API response, extract these fields:

| Field | Path | Description |
|-------|------|-------------|
| `url` | `data[].url` | Job URL |
| `title` | `data[].title` | Job title |
| `company` | `data[].user.company_name` | Company name |
| `status` | `data[].status` | "active" or other |
| `job_type` | `data[].params[]` where `key="type"` | full-time/part-time |
| `contract_type` | `data[].params[]` where `key="tip_contract"` | Contract type |
| `experience_level` | `data[].params[]` where `key="nivel_experienta"` | entry/mid/senior |
| `location` | `data[].location.city.name` | City name |
| `region` | `data[].location.region.name` | Region |
| `created` | `data[].created_time` | Posted date |
| `description` | `data[].description` | Full description (HTML) |

## Validating OLX Jobs

When you find an OLX job URL in peviitor.ro results:

1. **Extract the offer ID** from the URL:
   - URL: `https://www.olx.ro/oferta/loc-de-munca/lidl-vanzator-radauti-IDkcZUF.html`
   - ID: `300079886` (you need to call the list API to get IDs, or search in API response)

2. **Call the API** to get full job details:
   ```bash
   curl -s "https://www.olx.ro/api/v1/offers/<OFFER_ID>/"
   ```

3. **Check if job is active** - if `"status":"active"` then it's valid

4. **Extract company** from `user.company_name` field

5. **For CIF** - search web for company CIF using the company name

## Handling OLX Jobs in Verification Workflow

When peviitor.ro returns an OLX URL:
1. Try to fetch via WebFetch - if blocked by CAPTCHA → DELETE
2. If accessible → Use OLX API to get details and verify it's active
3. Extract company name from API and search for CIF
4. Update job in Solr with verified data

## Example: Verify OLX Job

```bash
# Get job details from OLX API
curl -s "https://www.olx.ro/api/v1/offers/300079886/" | jq '.data'

# Check status
# If status is "active" → keep in Solr
# If status is not "active" → delete from Solr
```
