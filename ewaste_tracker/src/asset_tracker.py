"""
Asset Tracking and Intake Logging System
Handles creation and management of asset records
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from .config import (
        ITEM_TYPES, ITEM_CONDITIONS, INTAKE_CSV_HEADERS,
        INTAKE_LOGS_DIR, get_current_date, get_current_datetime,
        get_file_timestamp
    )
except ImportError:
    from config import (
        ITEM_TYPES, ITEM_CONDITIONS, INTAKE_CSV_HEADERS,
        INTAKE_LOGS_DIR, get_current_date, get_current_datetime,
        get_file_timestamp
    )


class AssetTracker:
    """Manages asset intake and tracking"""

    def __init__(self):
        self.intake_log_path = INTAKE_LOGS_DIR / f"intake_log_{get_file_timestamp()}.csv"
        self.asset_counter = {}  # Track count per item type
        self._initialize_counter()

    def _initialize_counter(self):
        """Initialize asset counters for each item type"""
        for item_type in ITEM_TYPES.keys():
            self.asset_counter[item_type] = 0

    def generate_asset_id(self, item_type: str) -> str:
        """
        Generate unique asset ID for an item
        Format: PREFIX-YYYYMMDD-NNNN
        Example: CAB-20250107-0001
        """
        if item_type not in ITEM_TYPES:
            raise ValueError(f"Invalid item type: {item_type}")

        prefix = ITEM_TYPES[item_type]["prefix"]
        date_str = datetime.now().strftime("%Y%m%d")

        self.asset_counter[item_type] += 1
        count = self.asset_counter[item_type]

        return f"{prefix}-{date_str}-{count:04d}"

    def create_asset_record(self,
                           item_type: str,
                           serial_number: str = "",
                           condition: str = "Unknown",
                           notes: str = "") -> Dict:
        """Create a new asset record"""

        if item_type not in ITEM_TYPES:
            raise ValueError(f"Invalid item type: {item_type}")

        if condition not in ITEM_CONDITIONS:
            print(f"Warning: '{condition}' is not a standard condition. Using anyway.")

        item_config = ITEM_TYPES[item_type]
        asset_id = self.generate_asset_id(item_type)

        record = {
            "Asset ID": asset_id,
            "Item Type": item_config["name"],
            "Serial Number": serial_number,
            "Condition": condition,
            "Intake Date": get_current_date(),
            "Requires Label Removal": "Yes" if item_config["requires_label_removal"] else "No",
            "Label Removal Completed": "No",
            "Requires Data Wipe": "Yes" if item_config["requires_wipe"] else "No",
            "Data Wipe Method": "",
            "Data Wipe Date": "",
            "Data Wipe Technician": "",
            "Destruction Date": "",
            "Destruction Method": "",
            "Destruction Technician": "",
            "Photo Evidence Path": "",
            "Certificate Issued": "No",
            "Notes": notes
        }

        return record

    def batch_create_assets(self,
                           item_type: str,
                           quantity: int,
                           condition: str = "Unknown",
                           base_serial: str = "",
                           notes: str = "") -> List[Dict]:
        """Create multiple asset records at once"""

        records = []
        print(f"\nCreating {quantity} asset records for {ITEM_TYPES[item_type]['name']}...")

        for i in range(quantity):
            serial = f"{base_serial}-{i+1:04d}" if base_serial else ""
            record = self.create_asset_record(item_type, serial, condition, notes)
            records.append(record)

            # Progress indicator
            if (i + 1) % 10 == 0 or (i + 1) == quantity:
                print(f"  Created {i + 1}/{quantity} records...")

        print(f"✓ Successfully created {quantity} asset records")
        return records

    def save_to_csv(self, records: List[Dict], append: bool = True):
        """Save asset records to CSV"""

        mode = 'a' if append and self.intake_log_path.exists() else 'w'
        file_exists = self.intake_log_path.exists()

        with open(self.intake_log_path, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=INTAKE_CSV_HEADERS)

            # Write header if new file or overwriting
            if mode == 'w' or not file_exists:
                writer.writeheader()

            writer.writerows(records)

        print(f"\n✓ Records saved to: {self.intake_log_path}")

    def load_intake_log(self, log_path: Optional[Path] = None) -> List[Dict]:
        """Load intake log from CSV"""

        if log_path is None:
            # Find most recent intake log
            log_files = sorted(INTAKE_LOGS_DIR.glob("intake_log_*.csv"), reverse=True)
            if not log_files:
                print("No intake logs found.")
                return []
            log_path = log_files[0]

        records = []
        with open(log_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            records = list(reader)

        print(f"✓ Loaded {len(records)} records from {log_path.name}")
        return records

    def update_record(self, records: List[Dict], asset_id: str, updates: Dict) -> bool:
        """Update a specific asset record"""

        for record in records:
            if record["Asset ID"] == asset_id:
                record.update(updates)
                return True
        return False

    def get_summary_stats(self, records: List[Dict]) -> Dict:
        """Generate summary statistics from records"""

        stats = {
            "total_items": len(records),
            "by_type": {},
            "by_condition": {},
            "label_removal_pending": 0,
            "data_wipe_pending": 0,
            "destruction_pending": 0,
            "certificates_issued": 0
        }

        for record in records:
            # Count by type
            item_type = record["Item Type"]
            stats["by_type"][item_type] = stats["by_type"].get(item_type, 0) + 1

            # Count by condition
            condition = record["Condition"]
            stats["by_condition"][condition] = stats["by_condition"].get(condition, 0) + 1

            # Count pending tasks
            if record["Requires Label Removal"] == "Yes" and record["Label Removal Completed"] == "No":
                stats["label_removal_pending"] += 1

            if record["Requires Data Wipe"] == "Yes" and not record["Data Wipe Date"]:
                stats["data_wipe_pending"] += 1

            if not record["Destruction Date"]:
                stats["destruction_pending"] += 1

            if record["Certificate Issued"] == "Yes":
                stats["certificates_issued"] += 1

        return stats

    def find_assets_by_type(self, records: List[Dict], item_type_name: str) -> List[Dict]:
        """Find all assets of a specific type"""
        return [r for r in records if r["Item Type"] == item_type_name]

    def find_asset_by_id(self, records: List[Dict], asset_id: str) -> Optional[Dict]:
        """Find a specific asset by ID"""
        for record in records:
            if record["Asset ID"] == asset_id:
                return record
        return None


def display_item_types():
    """Display available item types"""
    print("\n" + "=" * 70)
    print("AVAILABLE ITEM TYPES")
    print("=" * 70)

    for code, config in ITEM_TYPES.items():
        print(f"\n[{code}]")
        print(f"  Name: {config['name']}")
        print(f"  Prefix: {config['prefix']}")
        print(f"  Expected Qty: {config['expected_quantity']}")
        print(f"  Requirements: ", end="")
        reqs = []
        if config['requires_label_removal']:
            reqs.append("Label Removal")
        if config['requires_wipe']:
            reqs.append("Data Wipe")
        if config['requires_photo']:
            reqs.append("Photo Evidence")
        print(", ".join(reqs) if reqs else "Destruction Only")
        print(f"  Description: {config['description']}")
    print("\n" + "=" * 70)


def display_conditions():
    """Display available condition options"""
    print("\nAVAILABLE CONDITIONS:")
    for i, condition in enumerate(ITEM_CONDITIONS, 1):
        print(f"  {i}. {condition}")
