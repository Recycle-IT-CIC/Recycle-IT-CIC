# E-Waste Tracking & Compliance System

**Version 1.0.0**
**Recycle-IT! CIC - LBQ Job Management**

A comprehensive job tracking and compliance system for processing e-waste batches with full ISO 9001, WEEE, and GDPR compliance.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [System Workflow](#system-workflow)
- [User Guide](#user-guide)
- [Project Structure](#project-structure)
- [Compliance Standards](#compliance-standards)
- [Troubleshooting](#troubleshooting)

---

## Overview

This system was built to track and document the processing of a large e-waste batch from **Learning by Questions (LBQ)** via **Logical BI Limited**. It provides:

- **Asset tracking** with unique barcode/asset IDs
- **Photo evidence management** with organised folder structure
- **PDF certificate generation** for destruction compliance
- **Final compliance reporting** suitable for client records
- **Full audit trail** for ISO 9001, WEEE, and GDPR requirements

### Job Scope: LBQ E-Waste Batch

| Item Type | Quantity | Special Requirements |
|-----------|----------|---------------------|
| Charging Cabinets | 85 | Remove all LBQ branding/labels |
| 10" Tablets (New) | 380 | Photo evidence of destruction |
| 8" Tablets (New) | 400 | Photo evidence of destruction |
| Mixed Tablets (Used) | 1,000 | Secure wipe THEN destruction |
| Remote Device Kits | 900 | Photo evidence of destruction |
| Computer Equipment | Variable | Secure destruction certificates |

---

## Features

### 1. Intake Logging System
- Generates unique asset IDs for every item (e.g., `CAB-20250107-0001`)
- Tracks serial numbers, condition, and category
- Batch import for processing large quantities
- Exports to CSV for record-keeping

### 2. Photo Evidence Management
- Creates organised folder structure by item type
- Links photos to specific asset IDs
- Generates timestamped filenames automatically
- Supports proof sheet generation

### 3. Certificate Generator
- Individual destruction certificates (PDF)
- Batch summary certificates
- Includes Recycle-IT! branding
- References WEEE/GDPR/ISO 9001 compliance
- Technician signature fields

### 4. Final Report Generator
- Comprehensive compliance reports
- Summary by item category
- Photo evidence references
- Certificate tracking
- Professional PDF format for client delivery

### 5. CLI Menu System
- Simple interface for non-technical volunteers
- Step-by-step workflows
- Confirmation prompts for safety
- Progress indicators for batch operations
- Built-in help system

---

## Installation

### Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package manager)

### Setup Steps

1. **Navigate to the project directory:**
   ```bash
   cd ewaste_tracker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install reportlab
   ```

3. **Verify installation:**
   ```bash
   python main.py
   ```

   You should see the main menu appear.

---

## Quick Start

### First Time Setup

1. **Launch the system:**
   ```bash
   python main.py
   ```

2. **Setup photo folders (Option 6):**
   - Creates organised folder structure
   - Sets up directories for each item type
   - Creates stage folders (before/during/after)

3. **Start logging items (Options 1-2):**
   - Use Option 1 for single items
   - Use Option 2 for batch logging

### Daily Workflow

```
Morning:
1. Log items as they arrive (Options 1-2)
2. Take photos during processing

During Processing:
3. Record data wipes for tablets/computers (Option 4)
4. Record destruction completion (Option 5)

End of Day:
5. Generate certificates (Options 9-10)
6. Review intake summary (Option 3)

Job Completion:
7. Generate final compliance report (Option 11)
```

---

## System Workflow

### Complete Processing Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INTAKE PHASE                                             │
├─────────────────────────────────────────────────────────────┤
│ • Log items as they arrive                                  │
│ • System generates unique Asset IDs                         │
│ • Record serial numbers and condition                       │
│ • Data saved to CSV in intake_logs/                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. PROCESSING PHASE                                         │
├─────────────────────────────────────────────────────────────┤
│ • For tablets/computers: Perform secure data wipe           │
│ • For cabinets: Remove LBQ branding/labels                  │
│ • Take BEFORE photos                                        │
│ • Perform physical destruction                              │
│ • Take DURING and AFTER photos                              │
│ • Record completion in system                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DOCUMENTATION PHASE                                      │
├─────────────────────────────────────────────────────────────┤
│ • Generate destruction certificates                         │
│ • Link photo evidence to asset IDs                          │
│ • Create batch certificates for efficiency                  │
│ • PDFs saved to certificates/                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. REPORTING PHASE                                          │
├─────────────────────────────────────────────────────────────┤
│ • Generate final compliance report                          │
│ • Includes all statistics and references                    │
│ • Professional PDF for client delivery                      │
│ • Report saved to reports/                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## User Guide

### Option 1: Log Single Item (Intake)

Use this when processing items one at a time.

**Steps:**
1. Select item type from list (e.g., `CABINET`, `TABLET_10_NEW`)
2. Enter serial number (optional)
3. Select condition (1-6)
4. Add notes (optional)
5. Confirm to save

**Example:**
```
Item Type: CABINET
Serial Number: CAB12345
Condition: Used - Good
Notes: Blue cabinet, LBQ logo on front

→ Creates Asset ID: CAB-20250107-0001
```

### Option 2: Log Batch Items (Intake)

Use this for processing multiple identical items quickly.

**Steps:**
1. Select item type
2. Enter quantity to log
3. Select condition for all items
4. Optionally provide base serial number
5. Add notes (optional)
6. Confirm to create batch

**Example:**
```
Item Type: TABLET_10_NEW
Quantity: 50
Condition: New/Sealed
Base Serial: LBQ-T10

→ Creates 50 assets: T10N-20250107-0001 through T10N-20250107-0050
```

### Option 3: View Intake Summary

Shows current statistics:
- Total items logged
- Breakdown by item type
- Breakdown by condition
- Pending tasks (data wipes, destructions, etc.)
- Certificates issued

### Option 4: Record Data Wipe

For tablets and computers that require secure data sanitisation.

**Steps:**
1. System shows items requiring data wipe
2. Enter Asset ID to update
3. Select data wipe method (DoD, NIST, Blancco, etc.)
4. Enter technician name
5. System records wipe completion with timestamp

### Option 5: Record Destruction

Record when physical destruction is complete.

**Steps:**
1. Enter Asset ID (or type `BATCH` for multiple)
2. For batch: Select item type or `ALL`
3. Select destruction method
4. Enter technician name
5. System records destruction with timestamp

**Batch Mode Example:**
```
Asset ID: BATCH
Item Type: Charging Cabinet
Destruction Method: Physical Shredding
Technician: John Smith

→ Updates all cabinets at once
```

### Option 6: Setup Photo Folders

Creates organised folder structure for photo evidence.

**Structure Created:**
```
photo_evidence/
  LBQ_Job_YYYYMMDD_HHMMSS/
    ├── before_destruction/
    ├── during_destruction/
    ├── after_destruction/
    ├── proof_sheets/
    ├── Charging Cabinet/
    ├── 10 Tablet (New-Boxed)/
    ├── 8 Tablet (New-Boxed)/
    ├── Mixed 8_10 Tablet (Used Returns)/
    ├── Handheld Remote Device Kit/
    └── Office Computer Equipment/
```

### Option 7: View Photo Guide

Displays comprehensive guide for:
- Folder structure
- File naming conventions
- Stage definitions
- Best practices

**File Naming Convention:**
```
ASSETID_STAGE_SEQUENCE_TIMESTAMP.jpg

Examples:
CAB-20250107-0001_before_01_20250107_143022.jpg
T10N-20250107-0050_destruction_01_20250107_150315.jpg
TMU-20250107-0123_after_01_20250107_152045.jpg
```

### Option 8: Photo Inventory

Scans photo folders and provides:
- Total photo count
- Breakdown by item type
- Breakdown by stage
- List of job folders

### Option 9: Generate Individual Certificate

Creates a single PDF certificate for one asset.

**Requirements:**
- Item must be destroyed
- Certificate not already issued

**Certificate Includes:**
- Asset ID and details
- Destruction method and date
- Data wipe information (if applicable)
- Technician certification
- Compliance references
- Photo evidence references

### Option 10: Generate Batch Certificate

Creates a single PDF covering multiple assets.

**Filtering Options:**
- All destroyed items
- Specific item type
- Date range

**Certificate Includes:**
- Summary statistics
- List of all asset IDs
- Batch destruction information
- Compliance references

### Option 11: Generate Final Report

Creates comprehensive compliance report for client.

**Report Contains:**
- Executive summary
- Item breakdown with expected vs actual
- Compliance methodology
- Destruction methods used
- Photo evidence summary
- Certificate listing
- Full audit trail

---

## Project Structure

```
ewaste_tracker/
│
├── main.py                     # Main CLI application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/                        # Source code modules
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── asset_tracker.py       # Asset tracking and intake logging
│   ├── photo_manager.py       # Photo evidence management
│   ├── certificate_generator.py  # PDF certificate generation
│   └── report_generator.py    # Final compliance reports
│
├── intake_logs/               # CSV intake logs (auto-created)
│   └── intake_log_TIMESTAMP.csv
│
├── photo_evidence/            # Photo storage (auto-created)
│   └── LBQ_Job_TIMESTAMP/
│       ├── [Item type folders]/
│       └── [Stage folders]/
│
├── certificates/              # Generated certificates (auto-created)
│   ├── CERT-*.pdf
│   └── CERT-BATCH-*.pdf
│
└── reports/                   # Final reports (auto-created)
    └── LBQ_Final_Report_*.pdf
```

---

## Compliance Standards

### ISO 9001:2015 - Quality Management

This system ensures:
- Documented procedures for all processes
- Traceability of all items through unique asset IDs
- Comprehensive record-keeping
- Technician accountability
- Process verification through photo evidence

### WEEE Regulations 2013

Compliance through:
- Proper categorisation of electronic waste
- Documented destruction methods
- Segregation for recycling
- Hazardous component handling records
- Chain of custody documentation

### UK GDPR 2018

Data protection via:
- Secure data sanitisation methods
- Certified wipe procedures (DoD, NIST, Blancco)
- Physical destruction of storage devices
- Complete data destruction verification
- Audit trail for all data-bearing devices

---

## Troubleshooting

### PDF Generation Errors

**Error:** `reportlab library is required for PDF generation`

**Solution:**
```bash
pip install reportlab
```

### Missing Directories

**Error:** Files not being saved

**Solution:**
Directories are auto-created. If issues persist:
```bash
cd ewaste_tracker
mkdir -p intake_logs photo_evidence certificates reports
```

### CSV Encoding Issues

**Error:** Special characters not displaying correctly

**Solution:**
Open CSV files with UTF-8 encoding:
- Excel: Data > Get Data > From Text/CSV > File Origin: UTF-8
- LibreOffice: Open with character set UTF-8

### Photo Import

Photos must be manually placed in the correct folders with proper naming:
```bash
# Copy photos to correct folder
cp camera_photos/* photo_evidence/LBQ_Job_*/[ItemType]/

# Rename using asset IDs
# Example: mv IMG_1234.jpg CAB-20250107-0001_destruction_01_20250107_143022.jpg
```

### Finding Recent Files

All files use timestamps. To find most recent:

```bash
# Latest intake log
ls -lt intake_logs/ | head -n 2

# Latest certificate
ls -lt certificates/ | head -n 2

# Latest report
ls -lt reports/ | head -n 2
```

---

## Tips for Volunteers

### Best Practices

1. **Log items immediately** when they arrive
2. **Use batch mode** for identical items (saves time)
3. **Take photos in stages** (before, during, after)
4. **Include asset ID** in every photo filename
5. **Generate certificates daily** to stay current
6. **Create backups** of intake logs regularly

### Time-Saving Tips

- Use batch destruction recording for groups
- Generate batch certificates instead of individual
- Setup photo folders at start of job
- Keep paper checklist alongside digital system

### Common Workflows

**Processing 100 identical tablets:**
1. Option 2: Log all 100 at once
2. Option 4: Batch record data wipes
3. Take photos (can batch by groups)
4. Option 5: Batch record destruction
5. Option 10: Generate single batch certificate

**End of day routine:**
1. Option 3: Review summary
2. Option 8: Check photo inventory
3. Option 9/10: Generate certificates
4. Backup intake log CSV

---

## Support

For technical issues or questions:

**Organisation:** Recycle-IT! CIC
**Email:** recycle.it.cic@gmail.com
**Location:** Bolton, UK

---

## Version History

**v1.0.0** - Initial release
- Complete intake logging system
- Photo evidence management
- PDF certificate generation
- Final compliance reporting
- CLI menu interface
- ISO 9001, WEEE, GDPR compliance

---

## License

Copyright © 2025 Recycle-IT! CIC
For internal use only - LBQ Job Management

---

**Built with ❤️ for digital inclusion and responsible e-waste management**
