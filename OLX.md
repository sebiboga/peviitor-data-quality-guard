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

1. **Get the offer ID by searching in the list API**:
   ```bash
   curl -s "https://www.olx.ro/api/v1/offers/?offset=0&limit=100&category_id=4&currency=RON" | jq '.data[] | select(.url | contains("PARTIAL_URL_SLUG")) | {id, title, status}'
   ```
   Replace `PARTIAL_URL_SLUG` with a unique part of the URL (e.g., `shop-gomega-image-s6`)

2. **Call the API** with numeric ID to get full job details:
   ```bash
   curl -s "https://www.olx.ro/api/v1/offers/<NUMERIC_ID>/"
   ```

3. **Extract data from API response**:
   - **company**: `user.company_name` (if null, use "OLX" or extract from title)
   - **salary**: `salary.from` and `salary.to` → format as "FROM-TO RON"
   - **location**: `location.city.name`
   - **workmode**: Check `params[]` for remote/hybrid flags or default to "on-site"
   - **tags**: Extract from `params[]`:
     - `type` → full-time/part-time
     - `tip_contract` → contract type
     - `nivel_experienta` → entry/mid/senior
     - `program_demunca` → schedule type
     - `open_for_students` → students
   - **status**: If `"status":"active"` → valid, otherwise DELETE

4. **For CIF** - search web for company CIF using the company name

5. **Update job in Solr** with FULL PUSH (all fields)

## Handling OLX Jobs in Verification Workflow

When peviitor.ro returns an OLX URL:
1. **Use OLX API** (not Chrome) to get job details
2. Extract offer ID from list API by matching URL slug
3. Call single offer API with numeric ID
4. If status is not "active" → DELETE from Solr
5. If active → extract all fields, find CIF, update Solr with FULL PUSH
6. **No Chrome needed for OLX jobs!**

## Example: Verify OLX Job

```bash
# Get job details from OLX API
curl -s "https://www.olx.ro/api/v1/offers/300079886/" | jq '.data'

# Check status
# If status is "active" → keep in Solr
# If status is not "active" → delete from Solr
```
