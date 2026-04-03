# Quick Start Guide - AI Snapshot Reporting Agent

Get started with the snapshot reporting agent in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Prepare Your Logos

Place your logos in a `logos/` directory:
```
logos/
├── denodo_logo.png
└── active_logo.png
```

Recommended size: 200x100 pixels

## 3. Three Core Commands

### Command 1: Create a Snapshot
Capture a URL and create a Word document with your logos.

```bash
python -m media_monitor snapshot \
  --url "https://example.com/article" \
  --client "Denodo" \
  --magazine "TechNews" \
  --client-logo "logos/denodo_logo.png" \
  --active-logo "logos/active_logo.png"
```

**Output:** `reports/snapshots/ADC_DENODO_TECHNEWS_20260403.docx`

---

### Command 2: Create 24-Hour Coverage Report
Generate a professional coverage report in Word format.

```bash
python -m media_monitor coverage-24h \
  --client "Denodo" \
  --campaign "Q1 Launch" \
  --client-logo "logos/denodo_logo.png" \
  --active-logo "logos/active_logo.png"
```

**Requirements:** You must run `collect` first to populate the database.

```bash
# Populate database with sample data
python -m media_monitor collect --csv sample_manual_scan.csv

# Then create the report
python -m media_monitor coverage-24h --client "Denodo" --campaign "Q1 Launch"
```

**Output:** `reports/coverage/ADC_DENODO_Q1_LAUNCH_20260403.docx`

---

### Command 3: Create/Update Excel Tracker
Maintain a central tracking spreadsheet for all your coverage.

```bash
# Update tracker with new records
python -m media_monitor tracker update --client "Denodo"

# View tracker records
python -m media_monitor tracker load --client "Denodo"
```

**Output:** `ADC/clients/tracker.xlsx`

---

## 4. File Organization

After running the commands, your directory structure will look like:

```
Montor-/
├── reports/
│   ├── snapshots/          ← Individual publication snapshots
│   │   └── ADC_DENODO_TECHNEWS_20260403.docx
│   └── coverage/           ← 24-hour coverage reports
│       └── ADC_DENODO_Q1_LAUNCH_20260403.docx
├── ADC/
│   └── clients/
│       └── tracker.xlsx    ← Central tracking file
├── logos/
│   ├── denodo_logo.png
│   └── active_logo.png
```

---

## 5. Complete Workflow Example

```bash
# Step 1: Load sample data
python -m media_monitor collect --csv sample_manual_scan.csv

# Step 2: Create a snapshot of a specific article
python -m media_monitor snapshot \
  --url "https://technewsme.com" \
  --client "Denodo" \
  --magazine "TechNews ME" \
  --headline "Denodo Launches Enterprise Platform" \
  --client-logo "logos/denodo_logo.png" \
  --active-logo "logos/active_logo.png"

# Step 3: Generate 24-hour coverage report
python -m media_monitor coverage-24h \
  --client "Denodo" \
  --campaign "Enterprise Platform Launch" \
  --client-logo "logos/denodo_logo.png" \
  --active-logo "logos/active_logo.png"

# Step 4: Update the tracker
python -m media_monitor tracker update --client "Denodo"

# Step 5: View tracker data
python -m media_monitor tracker load --client "Denodo"
```

---

## 6. Customization

### Snapshot Customization

Add more metadata to your snapshots:

```bash
python -m media_monitor snapshot \
  --url "https://example.com" \
  --client "Denodo" \
  --magazine "IT Pro" \
  --date "2026-04-01" \
  --headline "Breaking News: Denodo Advances" \
  --client-logo "logos/denodo_logo.png" \
  --active-logo "logos/active_logo.png"
```

### Track Multiple Clients

The tracker supports multiple clients:

```bash
# Update Denodo coverage
python -m media_monitor tracker update --client "Denodo"

# Update Snowflake coverage
python -m media_monitor tracker update --client "Snowflake"

# View specific client data
python -m media_monitor tracker load --client "Snowflake"
```

---

## 7. Configuration

Edit `config_snapshot_agent.yaml` to customize:
- Logo sizes and positions
- Document styling (fonts, colors)
- Screenshot settings (resolution, timeout)
- Excel tracker columns
- Output directories

---

## 8. Troubleshooting

### "Failed to take screenshot"
- Make sure the URL is accessible
- Check your internet connection
- Ensure ChromeDriver is installed

### "Logos not appearing in document"
- Verify file paths are correct
- Check that image files exist
- Use PNG or JPG format only

### "Tracker file not found"
- Run `mkdir -p ADC/clients` to create directory
- Check write permissions on directory

### "No records in coverage report"
- Run `collect` command first to load data
- Use `python -m media_monitor validate` to check database

---

## 9. Advanced Usage

### Python API Usage

```python
from media_monitor.snapshot_reporting import (
    create_snapshot,
    create_24h_coverage,
    create_or_update_tracker,
)

# Create snapshot programmatically
create_snapshot(
    client_name="Denodo",
    magazine_name="TechNews",
    publishing_date="2026-04-03",
    url="https://example.com",
    client_logo_path="logos/denodo_logo.png",
    active_logo_path="logos/active_logo.png",
)
```

### Using with AI Features

```bash
# Extract headlines using Claude AI
python example_ai_snapshot_agent.py
```

---

## 10. Next Steps

1. **Customize logos**: Replace placeholder logos with your actual brand assets
2. **Test workflow**: Try the complete workflow with your data
3. **Automate**: Set up scheduled reporting with cron/scheduler
4. **AI integration**: Configure Anthropic API key for intelligent analysis

```bash
# Set API key for AI features
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Support

Full documentation: See `SNAPSHOT_AGENT_GUIDE.md`

Examples: See `example_ai_snapshot_agent.py`

Configuration: Edit `config_snapshot_agent.yaml`

---

## File Naming Convention Reference

| Item | Format | Example |
|------|--------|---------|
| Snapshot | `ADC_[CLIENT]_[MAGAZINE]_[DATE].docx` | `ADC_DENODO_TECHNEWS_20260403.docx` |
| 24h Coverage | `ADC_[CLIENT]_[CAMPAIGN]_[DATE].docx` | `ADC_DENODO_Q1_LAUNCH_20260403.docx` |
| Tracker | `ADC/clients/tracker.xlsx` | `ADC/clients/tracker.xlsx` |

---

**Ready to go!** Start with `python -m media_monitor snapshot --help` for more options.
