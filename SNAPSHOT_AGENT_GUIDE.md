# AI Snapshot Reporting Agent

A comprehensive reporting tool for media monitoring with three core commands:

1. **Create Snapshot** - Capture URL screenshots and create Word documents
2. **Create 24-Hour Coverage Report** - Generate coverage reports in Word format
3. **Create/Update Excel Tracker** - Maintain a central tracking spreadsheet

## File Naming Convention

All files follow a strict naming convention for organization:

### Snapshot Reports
```
ADC_[CLIENT_NAME]_[MAGAZINE_NAME]_[YYYYMMDD].docx
```
**Example:** `ADC_DENODO_TECHNEWS_20260403.docx`

### 24-Hour Coverage Reports
```
ADC_[CLIENT]_[PRESS_RELEASE_NAME]_[YYYYMMDD].docx
```
**Example:** `ADC_DENODO_Q1_LAUNCH_20260403.docx`

### Excel Tracker
```
ADC/clients/tracker.xlsx
```

## Features

All reports include:
- Client logo at the top-left
- Active Digital Communications logo at the top-right
- Professional formatting
- Metadata (date, client, publication, etc.)
- Summary statistics
- Detailed coverage data

## Installation

```bash
pip install -r requirements.txt
```

Required packages:
- `python-docx>=0.8.11` - Create/edit Word documents
- `selenium>=4.0.0` - Take website screenshots
- `pillow>=9.0.0` - Image processing
- `openpyxl>=3.1.0` - Excel manipulation
- `pandas>=1.3.0` - Data processing
- `anthropic>=0.7.0` - AI API access

## Command Reference

### 1. Create Snapshot

**Description:** Take a screenshot of a URL and create a Word document with logos.

**Basic Usage:**
```bash
python -m media_monitor snapshot \
  --url "https://example.com/article" \
  --client "Denodo" \
  --magazine "TechNews" \
  --date "2026-04-03"
```

**With Logos:**
```bash
python -m media_monitor snapshot \
  --url "https://example.com/article" \
  --client "Denodo" \
  --magazine "TechNews" \
  --date "2026-04-03" \
  --headline "Denodo Launches New Platform" \
  --client-logo "/path/to/client_logo.png" \
  --active-logo "/path/to/active_logo.png"
```

**Parameters:**
- `--url` (required) - URL to capture
- `--client` (required) - Client name
- `--magazine` (required) - Magazine/publication name
- `--date` (optional) - Publication date (YYYY-MM-DD), defaults to today
- `--headline` (optional) - Article headline
- `--client-logo` (optional) - Path to client logo image
- `--active-logo` (optional) - Path to Active logo image

**Output:** `ADC_[CLIENT]_[MAGAZINE]_[DATE].docx`

---

### 2. Create 24-Hour Coverage Report

**Description:** Generate a comprehensive coverage report for the last 24 hours.

**Basic Usage:**
```bash
python -m media_monitor coverage-24h \
  --client "Denodo" \
  --campaign "Q1 Platform Launch"
```

**With Logos:**
```bash
python -m media_monitor coverage-24h \
  --client "Denodo" \
  --campaign "Q1 Platform Launch" \
  --client-logo "/path/to/client_logo.png" \
  --active-logo "/path/to/active_logo.png"
```

**Parameters:**
- `--client` (required) - Client name
- `--campaign` (required) - Campaign or press release name
- `--client-logo` (optional) - Path to client logo image
- `--active-logo` (optional) - Path to Active logo image

**Requirements:**
- The database must be populated with coverage records (use `collect` command first)

**Output:** `ADC_[CLIENT]_[CAMPAIGN]_[DATE].docx` in `reports/coverage/`

**Report Includes:**
- Summary statistics (total articles, UMV, impressions)
- Detailed coverage table with:
  - Source
  - Headline
  - Publication date
  - UMV
  - Impressions
  - Tier

---

### 3. Create/Update Excel Tracker

**Description:** Manage a central Excel tracker for all coverage.

**Update Tracker (add new records):**
```bash
python -m media_monitor tracker update --client "Denodo"
```

**Load/View Tracker:**
```bash
python -m media_monitor tracker load --client "Denodo"
```

**Parameters:**
- `action` (required) - `update` or `load`
- `--client` (optional) - Filter by client name

**Tracker Columns:**
1. Date Added
2. Client
3. Source
4. Publication
5. Headline
6. URL
7. Media Type
8. Tier
9. UMV
10. Impressions
11. Message Pull-Through
12. Coverage Period

**Output:** `ADC/clients/tracker.xlsx`

---

## Workflow Example

### Step 1: Collect Coverage Data

```bash
# Option A: Use sample CSV
python -m media_monitor collect --csv sample_manual_scan.csv

# Option B: Use Google Search (mocked)
python -m media_monitor collect --google
```

### Step 2: Create Individual Snapshots

```bash
python -m media_monitor snapshot \
  --url "https://technews.com/article" \
  --client "Denodo" \
  --magazine "TechNews" \
  --client-logo "logos/denodo.png" \
  --active-logo "logos/active.png"
```

### Step 3: Generate 24-Hour Coverage Report

```bash
python -m media_monitor coverage-24h \
  --client "Denodo" \
  --campaign "Q1 Launch" \
  --client-logo "logos/denodo.png" \
  --active-logo "logos/active.png"
```

### Step 4: Update Tracker

```bash
python -m media_monitor tracker update --client "Denodo"
```

### Step 5: View Tracker

```bash
python -m media_monitor tracker load --client "Denodo"
```

---

## Output Directory Structure

```
Montor-/
├── reports/
│   ├── snapshots/
│   │   ├── ADC_DENODO_TECHNEWS_20260403.docx
│   │   ├── ADC_DENODO_TECHNEWS_20260404.docx
│   │   └── ...
│   └── coverage/
│       ├── ADC_DENODO_Q1_LAUNCH_20260403.docx
│       └── ...
├── ADC/
│   └── clients/
│       └── tracker.xlsx
```

---

## Logo Guidelines

Both client and Active logos should be:
- **Format:** PNG or JPG
- **Dimensions:** 200x100 pixels minimum
- **Resolution:** 72 DPI or higher
- **File Size:** Under 1MB

### Logo Placement
- **Client Logo:** Left side of header (1.5" width)
- **Active Logo:** Right side of header (1.5" width)

---

## Using with AI Agent

The agent can intelligently process:
- Screenshot quality optimization
- Automatic headline extraction
- Coverage metric calculation
- Tier classification
- Multi-language support (headlines in Arabic, English, etc.)

### AI-Powered Features (Future)

```python
from media_monitor.snapshot_reporting import create_snapshot
from anthropic import Anthropic

client = Anthropic()

# Extract headline from screenshot
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_base64,
                    },
                },
                {
                    "type": "text",
                    "text": "Extract the headline from this article screenshot."
                }
            ],
        }
    ],
)
```

---

## Troubleshooting

### Screenshot Fails
- Ensure ChromeDriver is installed and in PATH
- Check if the URL is accessible
- Verify firewall/proxy settings

### Logo Not Appearing
- Verify file paths are correct
- Check image format (PNG/JPG supported)
- Ensure images are not corrupted

### Tracker Issues
- Ensure `ADC/clients/` directory exists
- Check write permissions
- Verify OpenPyXL is installed

### No Data in Reports
- Run `collect` command first to populate database
- Check sample_manual_scan.csv for data
- Verify records have required fields

---

## API Reference

### snapshot_reporting.create_snapshot()

```python
def create_snapshot(
    client_name: str,
    magazine_name: str,
    publishing_date: str,
    url: str,
    headline: Optional[str] = None,
    client_logo_path: Optional[str] = None,
    active_logo_path: Optional[str] = None,
) -> Optional[Path]:
    """
    Create a snapshot of a publication URL.
    
    Returns:
        Path to created Word document, or None if failed
    """
```

### snapshot_reporting.create_24h_coverage()

```python
def create_24h_coverage(
    client_name: str,
    press_release_name: str,
    coverage_data: List[Dict],
    client_logo_path: Optional[str] = None,
    active_logo_path: Optional[str] = None,
) -> Optional[Path]:
    """
    Create 24-hour coverage report.
    
    Returns:
        Path to created Word document, or None if failed
    """
```

### snapshot_reporting.create_or_update_tracker()

```python
def create_or_update_tracker(
    records: List[Dict],
    client_name: Optional[str] = None,
) -> Optional[Path]:
    """
    Create or update Excel tracker.
    
    Returns:
        Path to tracker file, or None if failed
    """
```

---

## Support

For issues or questions:
- Check the troubleshooting section
- Review command examples above
- Verify all required dependencies are installed
- Check file permissions on output directories
