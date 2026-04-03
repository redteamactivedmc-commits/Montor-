"""
snapshot_reporting.py
---------------------
AI Agent for snapshot reporting with three main commands:

1. create_snapshot() - Takes screenshots of URLs and creates Word documents
2. create_24h_coverage() - Generates 24-hour coverage report in Word format
3. create_tracker() - Creates/updates Excel tracker sheet

File naming convention:
  • Snapshots: ADC_[client_name]_[magazine_name]_[publishing_date].docx
  • 24-hour coverage: ADC_[client]_[press_release_name]_[date].docx
  • Tracker: ADC/clients/tracker.xlsx

All files include client logo and Active logo at the top.
"""

from __future__ import annotations

import csv
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from io import BytesIO

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    HAS_EXCEL = True
except ImportError:
    HAS_EXCEL = False

import requests
from media_monitor.utils import get_logger, utcnow, ensure_dirs

log = get_logger(__name__)

# Directories
SNAPSHOTS_DIR = Path("reports/snapshots")
TRACKERS_DIR = Path("ADC/clients")
COVERAGE_DIR = Path("reports/coverage")


# ────────────────────────────────────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────

def ensure_snapshot_dirs():
    """Ensure all required directories exist."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    TRACKERS_DIR.mkdir(parents=True, exist_ok=True)
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)


def download_logo(url: str, max_height: float = 0.8) -> Optional[BytesIO]:
    """Download logo from URL and return as BytesIO object."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        log.warning(f"Failed to download logo from {url}: {e}")
        return None


def add_logo_header(doc: Document, client_logo_path: Optional[str], active_logo_path: Optional[str]):
    """Add client and Active logos to the top of Word document."""
    if not HAS_DOCX:
        log.warning("python-docx not installed, skipping logo header")
        return

    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.allow_autofit = False

    # Left cell - Client logo
    left_cell = table.rows[0].cells[0]
    if client_logo_path and os.path.exists(client_logo_path):
        try:
            paragraph = left_cell.paragraphs[0]
            run = paragraph.add_run()
            run.add_picture(client_logo_path, width=Inches(1.5))
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except Exception as e:
            log.warning(f"Failed to add client logo: {e}")

    # Right cell - Active logo
    right_cell = table.rows[0].cells[1]
    if active_logo_path and os.path.exists(active_logo_path):
        try:
            paragraph = right_cell.paragraphs[0]
            run = paragraph.add_run()
            run.add_picture(active_logo_path, width=Inches(1.5))
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        except Exception as e:
            log.warning(f"Failed to add Active logo: {e}")

    # Add spacing
    doc.add_paragraph()


def take_screenshot(url: str, headless: bool = True) -> Optional[BytesIO]:
    """Take screenshot of a URL using Selenium."""
    if not HAS_SELENIUM:
        log.warning("Selenium not installed, cannot take screenshots")
        return None

    try:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Wait for content to load
        driver.implicitly_wait(3)

        screenshot = driver.get_screenshot_as_png()
        driver.quit()

        return BytesIO(screenshot)
    except Exception as e:
        log.error(f"Failed to take screenshot of {url}: {e}")
        return None


# ────────────────────────────────────────────────────────────────────────────
#  COMMAND 1: CREATE SNAPSHOT
# ────────────────────────────────────────────────────────────────────────────

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
    Create a snapshot of a publication URL and save as Word document.

    Args:
        client_name: Client name (e.g., "Denodo")
        magazine_name: Publication/magazine name (e.g., "TechNews")
        publishing_date: Date of publication (e.g., "2026-04-03")
        url: URL to snapshot
        headline: Optional headline for the article
        client_logo_path: Path to client logo image
        active_logo_path: Path to Active logo image

    Returns:
        Path to created Word document, or None if failed
    """
    if not HAS_DOCX:
        log.error("python-docx not installed")
        return None

    ensure_snapshot_dirs()

    # Generate filename following convention: ADC_[client]_[magazine]_[date].docx
    safe_date = publishing_date.replace("-", "").replace("/", "")
    safe_client = client_name.replace(" ", "_").upper()
    safe_magazine = magazine_name.replace(" ", "_").upper()
    filename = f"ADC_{safe_client}_{safe_magazine}_{safe_date}.docx"
    filepath = SNAPSHOTS_DIR / filename

    try:
        doc = Document()

        # Add logos
        add_logo_header(doc, client_logo_path, active_logo_path)

        # Add title
        title = doc.add_heading(f"Media Snapshot Report", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add metadata
        doc.add_paragraph(f"Publication: {magazine_name}")
        doc.add_paragraph(f"Client: {client_name}")
        doc.add_paragraph(f"Date: {publishing_date}")
        doc.add_paragraph(f"URL: {url}")
        if headline:
            doc.add_paragraph(f"Headline: {headline}")

        # Add separator
        doc.add_paragraph("─" * 80)

        # Take screenshot and add to document
        log.info(f"Taking screenshot of {url}...")
        screenshot_io = take_screenshot(url)

        if screenshot_io and HAS_PIL:
            try:
                # Save screenshot to temporary file
                screenshot_io.seek(0)
                img = Image.open(screenshot_io)
                temp_img_path = SNAPSHOTS_DIR / f"temp_screenshot_{safe_date}.png"
                img.save(temp_img_path)

                # Add to document
                doc.add_paragraph("Screenshot:")
                doc.add_picture(str(temp_img_path), width=Inches(6.0))

                # Clean up temp file
                temp_img_path.unlink()
            except Exception as e:
                log.warning(f"Failed to add screenshot to document: {e}")
                doc.add_paragraph("[Screenshot could not be added]")

        # Add timestamp
        doc.add_paragraph()
        doc.add_paragraph(f"Report generated: {utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

        # Save document
        doc.save(str(filepath))
        log.info(f"✓ Snapshot saved → {filepath}")
        return filepath

    except Exception as e:
        log.error(f"Failed to create snapshot: {e}")
        return None


# ────────────────────────────────────────────────────────────────────────────
#  COMMAND 2: CREATE 24-HOUR COVERAGE REPORT
# ────────────────────────────────────────────────────────────────────────────

def create_24h_coverage(
    client_name: str,
    press_release_name: str,
    coverage_data: List[Dict],
    client_logo_path: Optional[str] = None,
    active_logo_path: Optional[str] = None,
) -> Optional[Path]:
    """
    Create a 24-hour coverage report in Word format.

    Args:
        client_name: Client name
        press_release_name: Name of press release or campaign
        coverage_data: List of coverage records (dicts with: source, headline, url, date, umv, impressions, etc.)
        client_logo_path: Path to client logo
        active_logo_path: Path to Active logo

    Returns:
        Path to created Word document, or None if failed
    """
    if not HAS_DOCX:
        log.error("python-docx not installed")
        return None

    ensure_snapshot_dirs()

    # Generate filename: ADC_[client]_[press_release]_[date].docx
    safe_client = client_name.replace(" ", "_").upper()
    safe_pr = press_release_name.replace(" ", "_").upper()
    current_date = utcnow().strftime("%Y%m%d")
    filename = f"ADC_{safe_client}_{safe_pr}_{current_date}.docx"
    filepath = COVERAGE_DIR / filename

    try:
        doc = Document()

        # Add logos
        add_logo_header(doc, client_logo_path, active_logo_path)

        # Add title
        title = doc.add_heading("24-Hour Coverage Report", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add metadata
        doc.add_paragraph(f"Campaign: {press_release_name}")
        doc.add_paragraph(f"Client: {client_name}")
        doc.add_paragraph(f"Report Date: {utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        doc.add_paragraph(f"Coverage Period: Last 24 Hours")

        # Summary statistics
        doc.add_paragraph()
        doc.add_heading("Summary Statistics", level=2)
        total_coverage = len(coverage_data)
        total_umv = sum(float(record.get("umv", 0)) for record in coverage_data if isinstance(record.get("umv"), (int, float, str)))
        total_impressions = sum(float(record.get("impressions", 0)) for record in coverage_data if isinstance(record.get("impressions"), (int, float, str)))

        doc.add_paragraph(f"Total Articles: {total_coverage}")
        doc.add_paragraph(f"Total UMV: ${total_umv:,.0f}")
        doc.add_paragraph(f"Total Impressions: {total_impressions:,.0f}")

        # Coverage breakdown
        doc.add_paragraph()
        doc.add_heading("Coverage Details", level=2)

        if coverage_data:
            # Create table
            table = doc.add_table(rows=1, cols=6)
            table.style = "Light Grid Accent 1"

            # Header row
            header_cells = table.rows[0].cells
            headers = ["Source", "Headline", "Date", "UMV", "Impressions", "Tier"]
            for i, header in enumerate(headers):
                header_cells[i].text = header
                header_cells[i].paragraphs[0].runs[0].font.bold = True

            # Data rows
            for record in coverage_data:
                row_cells = table.add_row().cells
                row_cells[0].text = str(record.get("source", ""))
                row_cells[1].text = str(record.get("headline", ""))[:50]
                row_cells[2].text = str(record.get("publication_date", ""))
                row_cells[3].text = f"${float(record.get('umv', 0)):,.0f}"
                row_cells[4].text = f"{float(record.get('impressions', 0)):,.0f}"
                row_cells[5].text = str(record.get("tier", ""))

        # Timestamp
        doc.add_paragraph()
        doc.add_paragraph(f"Report generated: {utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

        # Save document
        doc.save(str(filepath))
        log.info(f"✓ 24-hour coverage report saved → {filepath}")
        return filepath

    except Exception as e:
        log.error(f"Failed to create 24h coverage report: {e}")
        return None


# ────────────────────────────────────────────────────────────────────────────
#  COMMAND 3: CREATE/UPDATE EXCEL TRACKER
# ────────────────────────────────────────────────────────────────────────────

def create_or_update_tracker(
    records: List[Dict],
    client_name: Optional[str] = None,
) -> Optional[Path]:
    """
    Create or update the Excel tracker sheet.
    Location: ADC/clients/tracker.xlsx

    Args:
        records: List of coverage records to add
        client_name: Optional client name for filtering/organizing

    Returns:
        Path to tracker file, or None if failed
    """
    if not HAS_EXCEL:
        log.error("openpyxl/pandas not installed")
        return None

    ensure_snapshot_dirs()

    tracker_path = TRACKERS_DIR / "tracker.xlsx"

    try:
        # Load or create workbook
        if tracker_path.exists():
            wb = load_workbook(str(tracker_path))
            if "Coverage" in wb.sheetnames:
                ws = wb["Coverage"]
                start_row = ws.max_row + 1
            else:
                ws = wb.create_sheet("Coverage")
                start_row = 1
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Coverage"
            start_row = 1

        # Define headers if first time
        if start_row == 1:
            headers = [
                "Date Added",
                "Client",
                "Source",
                "Publication",
                "Headline",
                "URL",
                "Media Type",
                "Tier",
                "UMV",
                "Impressions",
                "Message Pull-Through",
                "Coverage Period",
            ]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col)
                cell.value = header
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Set column widths
            ws.column_dimensions["A"].width = 12
            ws.column_dimensions["B"].width = 15
            ws.column_dimensions["C"].width = 20
            ws.column_dimensions["D"].width = 20
            ws.column_dimensions["E"].width = 30
            ws.column_dimensions["F"].width = 35
            ws.column_dimensions["G"].width = 12
            ws.column_dimensions["H"].width = 10
            ws.column_dimensions["I"].width = 12
            ws.column_dimensions["J"].width = 15
            ws.column_dimensions["K"].width = 15
            ws.column_dimensions["L"].width = 15

        # Add records
        for record in records:
            ws.cell(row=start_row, column=1).value = utcnow().strftime("%Y-%m-%d")
            ws.cell(row=start_row, column=2).value = client_name or record.get("client", "")
            ws.cell(row=start_row, column=3).value = record.get("source", "")
            ws.cell(row=start_row, column=4).value = record.get("publication", "")
            ws.cell(row=start_row, column=5).value = record.get("headline", "")
            ws.cell(row=start_row, column=6).value = record.get("url", "")
            ws.cell(row=start_row, column=7).value = record.get("media_type", "")
            ws.cell(row=start_row, column=8).value = record.get("tier", "")
            ws.cell(row=start_row, column=9).value = record.get("umv", "")
            ws.cell(row=start_row, column=10).value = record.get("impressions", "")
            ws.cell(row=start_row, column=11).value = record.get("message_pullthrough", "")
            ws.cell(row=start_row, column=12).value = "24h"

            start_row += 1

        # Save workbook
        wb.save(str(tracker_path))
        log.info(f"✓ Tracker updated → {tracker_path}")
        return tracker_path

    except Exception as e:
        log.error(f"Failed to create/update tracker: {e}")
        return None


def load_tracker(
    client_filter: Optional[str] = None,
) -> Optional[List[Dict]]:
    """
    Load and return tracker data from Excel file.

    Args:
        client_filter: Optional client name to filter records

    Returns:
        List of records from tracker, or None if failed
    """
    if not HAS_EXCEL:
        log.error("openpyxl/pandas not installed")
        return None

    tracker_path = TRACKERS_DIR / "tracker.xlsx"

    if not tracker_path.exists():
        log.warning(f"Tracker not found at {tracker_path}")
        return None

    try:
        df = pd.read_excel(str(tracker_path), sheet_name="Coverage")

        if client_filter:
            df = df[df["Client"] == client_filter]

        return df.to_dict("records")
    except Exception as e:
        log.error(f"Failed to load tracker: {e}")
        return None
