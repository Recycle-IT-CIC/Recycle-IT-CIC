"""
Configuration and constants for the E-Waste Tracking System
Recycle-IT! CIC - LBQ Job Tracking
"""

from datetime import datetime
from pathlib import Path

# Project Information
PROJECT_NAME = "E-Waste Tracking & Compliance System"
VERSION = "1.0.0"
ORGANISATION = "Recycle-IT! CIC"
ORGANISATION_ADDRESS = "Bolton, UK"
ORGANISATION_EMAIL = "recycle.it.cic@gmail.com"

# Client Information
CLIENT_NAME = "Learning by Questions (LBQ)"
CLIENT_VIA = "Logical BI Limited"
JOB_TYPE = "Free Secure Destruction Service"

# Compliance Standards
COMPLIANCE_STANDARDS = [
    "ISO 9001:2015 Quality Management",
    "WEEE Regulations 2013",
    "UK GDPR 2018"
]

# Item Type Definitions
ITEM_TYPES = {
    "CABINET": {
        "name": "Charging Cabinet",
        "prefix": "CAB",
        "expected_quantity": 85,
        "requires_label_removal": True,
        "requires_photo": True,
        "requires_wipe": False,
        "description": "LBQ branded charging cabinet (remove all labels/branding before recycling)"
    },
    "TABLET_10_NEW": {
        "name": "10\" Tablet (New/Boxed)",
        "prefix": "T10N",
        "expected_quantity": 380,
        "requires_label_removal": False,
        "requires_photo": True,
        "requires_wipe": False,
        "description": "New boxed 10-inch tablet - requires destruction with photo evidence"
    },
    "TABLET_8_NEW": {
        "name": "8\" Tablet (New/Boxed)",
        "prefix": "T8N",
        "expected_quantity": 400,
        "requires_label_removal": False,
        "requires_photo": True,
        "requires_wipe": False,
        "description": "New boxed 8-inch tablet - requires destruction with photo evidence"
    },
    "TABLET_MIXED_USED": {
        "name": "Mixed 8\"/10\" Tablet (Used Returns)",
        "prefix": "TMU",
        "expected_quantity": 1000,
        "requires_label_removal": False,
        "requires_photo": True,
        "requires_wipe": True,
        "description": "Used returned tablet - requires secure wipe THEN destruction with photo evidence"
    },
    "REMOTE_KIT": {
        "name": "Handheld Remote Device Kit",
        "prefix": "REM",
        "expected_quantity": 900,
        "requires_label_removal": False,
        "requires_photo": True,
        "requires_wipe": False,
        "description": "Handheld remote device kit - requires destruction with photo evidence"
    },
    "COMPUTER_EQUIPMENT": {
        "name": "Office Computer Equipment",
        "prefix": "COMP",
        "expected_quantity": 0,  # Variable quantity
        "requires_label_removal": False,
        "requires_photo": True,
        "requires_wipe": True,
        "description": "Office computer equipment including hard drives - requires secure destruction with certificates"
    }
}

# Item Condition Options
ITEM_CONDITIONS = [
    "New/Sealed",
    "Used - Good",
    "Used - Fair",
    "Used - Poor",
    "Damaged",
    "For Parts"
]

# Destruction Methods
DESTRUCTION_METHODS = [
    "Physical Shredding",
    "Crushing",
    "Degaussing + Physical Destruction",
    "Secure Disassembly + Recycling"
]

# Data Sanitisation Methods
DATA_WIPE_METHODS = [
    "DoD 5220.22-M (3-pass)",
    "NIST 800-88 (Secure Erase)",
    "Blancco Certified Wipe",
    "Physical Destruction (No Wipe Required)"
]

# Directory Paths
# Determine base directory intelligently
_config_path = Path(__file__).resolve()
if _config_path.parent.name == "src":
    # We're in src/ subfolder, go up two levels
    BASE_DIR = _config_path.parent.parent
else:
    # We're in root folder, go up one level
    BASE_DIR = _config_path.parent

INTAKE_LOGS_DIR = BASE_DIR / "intake_logs"
PHOTO_EVIDENCE_DIR = BASE_DIR / "photo_evidence"
CERTIFICATES_DIR = BASE_DIR / "certificates"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for directory in [INTAKE_LOGS_DIR, PHOTO_EVIDENCE_DIR, CERTIFICATES_DIR, REPORTS_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Warning: Cannot create directory {directory}. Please check permissions.")
        print(f"Current BASE_DIR: {BASE_DIR}")
        raise

# Date Formats
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
FILE_DATE_FORMAT = "%Y%m%d_%H%M%S"

# CSV Headers
INTAKE_CSV_HEADERS = [
    "Asset ID",
    "Item Type",
    "Serial Number",
    "Condition",
    "Intake Date",
    "Requires Label Removal",
    "Label Removal Completed",
    "Requires Data Wipe",
    "Data Wipe Method",
    "Data Wipe Date",
    "Data Wipe Technician",
    "Destruction Date",
    "Destruction Method",
    "Destruction Technician",
    "Photo Evidence Path",
    "Certificate Issued",
    "Notes"
]

def get_current_date():
    """Return current date in UK format"""
    return datetime.now().strftime(DATE_FORMAT)

def get_current_datetime():
    """Return current datetime in UK format"""
    return datetime.now().strftime(DATETIME_FORMAT)

def get_file_timestamp():
    """Return timestamp suitable for filenames"""
    return datetime.now().strftime(FILE_DATE_FORMAT)
