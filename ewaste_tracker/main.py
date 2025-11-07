#!/usr/bin/env python3
"""
E-Waste Tracking and Compliance System - Main CLI Interface
Recycle-IT! CIC - LBQ Job Management

Main menu system for volunteers to manage the entire e-waste tracking workflow
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import (
    PROJECT_NAME, VERSION, ORGANISATION, CLIENT_NAME,
    ITEM_TYPES, ITEM_CONDITIONS, DESTRUCTION_METHODS, DATA_WIPE_METHODS
)
from asset_tracker import AssetTracker, display_item_types, display_conditions
from photo_manager import PhotoManager
from certificate_generator import CertificateGenerator
from report_generator import ReportGenerator


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    """Print application header"""
    print("=" * 80)
    print(f"{PROJECT_NAME} v{VERSION}".center(80))
    print(f"{ORGANISATION} - {CLIENT_NAME}".center(80))
    print("=" * 80)
    print()


def print_menu(title, options):
    """Print a menu with options"""
    print(f"\n{title}")
    print("-" * 60)
    for key, description in options.items():
        print(f"  [{key}] {description}")
    print("-" * 60)


def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    value = input(prompt).strip()
    return value if value else default


def confirm_action(message):
    """Ask user to confirm an action"""
    response = input(f"{message} (y/n): ").strip().lower()
    return response in ['y', 'yes']


# ============================================================================
# INTAKE LOGGING WORKFLOWS
# ============================================================================

def intake_single_item(tracker):
    """Log a single item intake"""
    print("\n" + "=" * 60)
    print("SINGLE ITEM INTAKE")
    print("=" * 60)

    display_item_types()

    item_type = get_input("Enter item type code (e.g., CABINET, TABLET_10_NEW)").upper()

    if item_type not in ITEM_TYPES:
        print(f"❌ Invalid item type: {item_type}")
        return

    print(f"\nSelected: {ITEM_TYPES[item_type]['name']}")
    print(f"Description: {ITEM_TYPES[item_type]['description']}")

    serial_number = get_input("Serial Number (optional)", "")
    print("\nCondition options:")
    display_conditions()
    condition_idx = get_input("Select condition (1-6)", "1")

    try:
        condition = ITEM_CONDITIONS[int(condition_idx) - 1]
    except (ValueError, IndexError):
        condition = "Unknown"

    notes = get_input("Notes (optional)", "")

    # Create record
    record = tracker.create_asset_record(item_type, serial_number, condition, notes)

    print("\n✓ Asset record created:")
    print(f"  Asset ID: {record['Asset ID']}")
    print(f"  Item Type: {record['Item Type']}")
    print(f"  Condition: {record['Condition']}")

    if confirm_action("\nSave this record to intake log?"):
        tracker.save_to_csv([record])
        print("✓ Record saved successfully")
    else:
        print("Record discarded")


def intake_batch_items(tracker):
    """Log multiple items in batch"""
    print("\n" + "=" * 60)
    print("BATCH ITEM INTAKE")
    print("=" * 60)

    display_item_types()

    item_type = get_input("Enter item type code").upper()

    if item_type not in ITEM_TYPES:
        print(f"❌ Invalid item type: {item_type}")
        return

    print(f"\nSelected: {ITEM_TYPES[item_type]['name']}")
    print(f"Expected quantity: {ITEM_TYPES[item_type]['expected_quantity']}")

    quantity = get_input("How many items to log", ITEM_TYPES[item_type]['expected_quantity'])

    try:
        quantity = int(quantity)
    except ValueError:
        print("❌ Invalid quantity")
        return

    print("\nCondition options:")
    display_conditions()
    condition_idx = get_input("Select condition for all items (1-6)", "1")

    try:
        condition = ITEM_CONDITIONS[int(condition_idx) - 1]
    except (ValueError, IndexError):
        condition = "Unknown"

    base_serial = get_input("Base serial number (will add -0001, -0002, etc.) [optional]", "")
    notes = get_input("Notes for all items (optional)", "")

    print(f"\n⚠ You are about to create {quantity} records for {ITEM_TYPES[item_type]['name']}")

    if not confirm_action("Continue?"):
        print("Batch intake cancelled")
        return

    # Create batch records
    records = tracker.batch_create_assets(item_type, quantity, condition, base_serial, notes)

    if confirm_action(f"\n✓ {len(records)} records created. Save to intake log?"):
        tracker.save_to_csv(records)
        print("✓ Records saved successfully")
    else:
        print("Records discarded")


def view_intake_summary(tracker):
    """View summary of intake log"""
    print("\n" + "=" * 60)
    print("INTAKE LOG SUMMARY")
    print("=" * 60)

    records = tracker.load_intake_log()

    if not records:
        print("No records found in intake log")
        return

    stats = tracker.get_summary_stats(records)

    print(f"\nTotal Items: {stats['total_items']}")
    print(f"Certificates Issued: {stats['certificates_issued']}")

    print("\n--- By Item Type ---")
    for item_type, count in sorted(stats['by_type'].items()):
        print(f"  {item_type}: {count}")

    print("\n--- By Condition ---")
    for condition, count in sorted(stats['by_condition'].items()):
        print(f"  {condition}: {count}")

    print("\n--- Pending Tasks ---")
    print(f"  Label Removal: {stats['label_removal_pending']}")
    print(f"  Data Wipe: {stats['data_wipe_pending']}")
    print(f"  Destruction: {stats['destruction_pending']}")

    input("\nPress Enter to continue...")


# ============================================================================
# DESTRUCTION & DATA WIPE WORKFLOWS
# ============================================================================

def record_data_wipe(tracker):
    """Record data wipe completion"""
    print("\n" + "=" * 60)
    print("RECORD DATA WIPE")
    print("=" * 60)

    records = tracker.load_intake_log()

    if not records:
        print("No records found")
        return

    # Show items requiring data wipe
    pending = [r for r in records if r['Requires Data Wipe'] == 'Yes' and not r['Data Wipe Date']]

    if not pending:
        print("✓ No items pending data wipe")
        return

    print(f"\n{len(pending)} items require data wipe:")
    for i, record in enumerate(pending[:10], 1):
        print(f"  {i}. {record['Asset ID']} - {record['Item Type']}")

    if len(pending) > 10:
        print(f"  ... and {len(pending) - 10} more")

    asset_id = get_input("\nEnter Asset ID to update").upper()

    record = tracker.find_asset_by_id(records, asset_id)

    if not record:
        print(f"❌ Asset ID not found: {asset_id}")
        return

    print(f"\nAsset: {record['Asset ID']} - {record['Item Type']}")

    print("\nData Wipe Methods:")
    for i, method in enumerate(DATA_WIPE_METHODS, 1):
        print(f"  {i}. {method}")

    method_idx = get_input("Select wipe method (1-4)", "1")

    try:
        wipe_method = DATA_WIPE_METHODS[int(method_idx) - 1]
    except (ValueError, IndexError):
        wipe_method = DATA_WIPE_METHODS[0]

    from config import get_current_date
    technician = get_input("Technician name")

    # Update record
    updates = {
        "Data Wipe Method": wipe_method,
        "Data Wipe Date": get_current_date(),
        "Data Wipe Technician": technician
    }

    tracker.update_record(records, asset_id, updates)

    # Save updated log
    from config import INTAKE_LOGS_DIR
    log_path = tracker.intake_log_path
    tracker.save_to_csv(records, append=False)

    print(f"✓ Data wipe recorded for {asset_id}")


def record_destruction(tracker):
    """Record destruction completion"""
    print("\n" + "=" * 60)
    print("RECORD DESTRUCTION")
    print("=" * 60)

    records = tracker.load_intake_log()

    if not records:
        print("No records found")
        return

    # Show items pending destruction
    pending = [r for r in records if not r['Destruction Date']]

    if not pending:
        print("✓ All items have been destroyed")
        return

    print(f"\n{len(pending)} items pending destruction:")
    for i, record in enumerate(pending[:10], 1):
        print(f"  {i}. {record['Asset ID']} - {record['Item Type']}")

    if len(pending) > 10:
        print(f"  ... and {len(pending) - 10} more")

    asset_id = get_input("\nEnter Asset ID to update (or 'BATCH' for multiple)").upper()

    if asset_id == 'BATCH':
        # Batch destruction recording
        item_type_name = get_input("Enter item type name to update (or 'ALL' for all)")

        if item_type_name.upper() == 'ALL':
            to_update = pending
        else:
            to_update = [r for r in pending if r['Item Type'] == item_type_name]

        if not to_update:
            print("No matching items found")
            return

        print(f"\n⚠ You are about to mark {len(to_update)} items as destroyed")

        if not confirm_action("Continue?"):
            print("Batch update cancelled")
            return

        print("\nDestruction Methods:")
        for i, method in enumerate(DESTRUCTION_METHODS, 1):
            print(f"  {i}. {method}")

        method_idx = get_input("Select destruction method (1-4)", "1")

        try:
            dest_method = DESTRUCTION_METHODS[int(method_idx) - 1]
        except (ValueError, IndexError):
            dest_method = DESTRUCTION_METHODS[0]

        from config import get_current_date
        technician = get_input("Technician name")

        updates = {
            "Destruction Method": dest_method,
            "Destruction Date": get_current_date(),
            "Destruction Technician": technician
        }

        # Update all matching records
        for record in to_update:
            tracker.update_record(records, record['Asset ID'], updates)

        tracker.save_to_csv(records, append=False)
        print(f"✓ {len(to_update)} items marked as destroyed")

    else:
        # Single item update
        record = tracker.find_asset_by_id(records, asset_id)

        if not record:
            print(f"❌ Asset ID not found: {asset_id}")
            return

        print(f"\nAsset: {record['Asset ID']} - {record['Item Type']}")

        print("\nDestruction Methods:")
        for i, method in enumerate(DESTRUCTION_METHODS, 1):
            print(f"  {i}. {method}")

        method_idx = get_input("Select destruction method (1-4)", "1")

        try:
            dest_method = DESTRUCTION_METHODS[int(method_idx) - 1]
        except (ValueError, IndexError):
            dest_method = DESTRUCTION_METHODS[0]

        from config import get_current_date
        technician = get_input("Technician name")

        updates = {
            "Destruction Method": dest_method,
            "Destruction Date": get_current_date(),
            "Destruction Technician": technician
        }

        tracker.update_record(records, asset_id, updates)
        tracker.save_to_csv(records, append=False)

        print(f"✓ Destruction recorded for {asset_id}")


# ============================================================================
# PHOTO EVIDENCE WORKFLOWS
# ============================================================================

def setup_photo_folders(photo_mgr):
    """Create photo evidence folder structure"""
    print("\n" + "=" * 60)
    print("SETUP PHOTO FOLDERS")
    print("=" * 60)

    job_name = get_input("Job name", "LBQ_Job")

    folders = photo_mgr.create_folder_structure(job_name)

    print("\n✓ Folder structure ready for photo collection")
    input("\nPress Enter to continue...")


def view_photo_guide(photo_mgr):
    """Display photo organisation guide"""
    photo_mgr.display_photo_structure_guide()
    input("\nPress Enter to continue...")


def photo_inventory(photo_mgr):
    """Show photo inventory"""
    print("\n" + "=" * 60)
    print("PHOTO INVENTORY")
    print("=" * 60)

    inventory = photo_mgr.create_photo_inventory()

    if not inventory or inventory.get('total_photos', 0) == 0:
        print("No photos found in evidence folders")
        return

    print(f"\nJob Folder: {Path(inventory['job_folder']).name}")
    print(f"Total Photos: {inventory['total_photos']}")

    if inventory.get('by_item_type'):
        print("\n--- By Item Type ---")
        for item_type, count in sorted(inventory['by_item_type'].items()):
            print(f"  {item_type}: {count} photos")

    if inventory.get('by_stage'):
        print("\n--- By Stage ---")
        for stage, count in sorted(inventory['by_stage'].items()):
            print(f"  {stage}: {count} photos")

    input("\nPress Enter to continue...")


# ============================================================================
# CERTIFICATE WORKFLOWS
# ============================================================================

def generate_individual_cert(tracker, cert_gen):
    """Generate certificate for single asset"""
    print("\n" + "=" * 60)
    print("GENERATE INDIVIDUAL CERTIFICATE")
    print("=" * 60)

    records = tracker.load_intake_log()

    if not records:
        print("No records found")
        return

    # Show destroyed items without certificates
    eligible = [r for r in records if r['Destruction Date'] and r['Certificate Issued'] != 'Yes']

    if not eligible:
        print("No items eligible for certificates")
        print("(Items must be destroyed and not already have certificates)")
        return

    print(f"\n{len(eligible)} items eligible for certificates:")
    for i, record in enumerate(eligible[:10], 1):
        print(f"  {i}. {record['Asset ID']} - {record['Item Type']}")

    if len(eligible) > 10:
        print(f"  ... and {len(eligible) - 10} more")

    asset_id = get_input("\nEnter Asset ID").upper()

    record = tracker.find_asset_by_id(records, asset_id)

    if not record:
        print(f"❌ Asset ID not found: {asset_id}")
        return

    if not record['Destruction Date']:
        print(f"❌ Item not yet destroyed: {asset_id}")
        return

    print(f"\nGenerating certificate for: {record['Asset ID']} - {record['Item Type']}")

    try:
        cert_path = cert_gen.generate_individual_certificate(record)

        # Mark as issued
        tracker.update_record(records, asset_id, {"Certificate Issued": "Yes"})
        tracker.save_to_csv(records, append=False)

        print(f"\n✓ Certificate saved to: {cert_path}")
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")

    input("\nPress Enter to continue...")


def generate_batch_cert(tracker, cert_gen):
    """Generate batch certificate"""
    print("\n" + "=" * 60)
    print("GENERATE BATCH CERTIFICATE")
    print("=" * 60)

    records = tracker.load_intake_log()

    if not records:
        print("No records found")
        return

    # Show destroyed items
    destroyed = [r for r in records if r['Destruction Date']]

    if not destroyed:
        print("No destroyed items found")
        return

    print(f"\n{len(destroyed)} destroyed items found")

    # Filter options
    print("\nFilter by:")
    print("  [1] All destroyed items")
    print("  [2] Specific item type")
    print("  [3] Date range")

    choice = get_input("Select filter (1-3)", "1")

    if choice == "2":
        item_type_name = get_input("Enter item type name")
        items = [r for r in destroyed if r['Item Type'] == item_type_name]
    elif choice == "3":
        date_from = get_input("From date (DD/MM/YYYY)")
        date_to = get_input("To date (DD/MM/YYYY)")
        # Simple date filtering - in production would parse dates properly
        items = destroyed
    else:
        items = destroyed

    if not items:
        print("No items match filter")
        return

    print(f"\n⚠ Generating batch certificate for {len(items)} items")

    batch_name = get_input("Batch name", "LBQ_Batch")

    if confirm_action("Generate certificate?"):
        try:
            cert_path = cert_gen.generate_batch_certificate(items, batch_name)

            # Mark all as issued
            for record in items:
                tracker.update_record(records, record['Asset ID'], {"Certificate Issued": "Yes"})

            tracker.save_to_csv(records, append=False)

            print(f"\n✓ Batch certificate saved to: {cert_path}")
        except Exception as e:
            print(f"❌ Error generating certificate: {e}")

    input("\nPress Enter to continue...")


# ============================================================================
# REPORT WORKFLOWS
# ============================================================================

def generate_final_report(tracker, photo_mgr, cert_gen, report_gen):
    """Generate final compliance report"""
    print("\n" + "=" * 60)
    print("GENERATE FINAL COMPLIANCE REPORT")
    print("=" * 60)

    records = tracker.load_intake_log()

    if not records:
        print("No records found")
        return

    stats = tracker.get_summary_stats(records)

    print(f"\nTotal Items: {stats['total_items']}")
    print(f"Destroyed: {stats['total_items'] - stats['destruction_pending']}")
    print(f"Certificates Issued: {stats['certificates_issued']}")

    # Get photo inventory
    print("\nScanning photo evidence...")
    photo_inventory = photo_mgr.create_photo_inventory()

    # Get certificate list
    cert_list = cert_gen.list_certificates()

    print(f"Photos found: {photo_inventory.get('total_photos', 0)}")
    print(f"Certificates found: {len(cert_list)}")

    report_name = get_input("\nReport name", "LBQ_Final_Report")

    if confirm_action("\nGenerate final compliance report?"):
        try:
            report_path = report_gen.generate_final_report(
                records,
                photo_inventory,
                cert_list,
                report_name
            )
            print(f"\n✓ Report saved to: {report_path}")
        except Exception as e:
            print(f"❌ Error generating report: {e}")

    input("\nPress Enter to continue...")


# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """Main application menu"""

    # Initialize modules
    tracker = AssetTracker()
    photo_mgr = PhotoManager()

    try:
        cert_gen = CertificateGenerator()
        report_gen = ReportGenerator()
        pdf_available = True
    except ImportError:
        cert_gen = None
        report_gen = None
        pdf_available = False

    while True:
        clear_screen()
        print_header()

        menu_options = {
            "1": "Log Single Item (Intake)",
            "2": "Log Batch Items (Intake)",
            "3": "View Intake Summary",
            "4": "Record Data Wipe",
            "5": "Record Destruction",
            "6": "Setup Photo Folders",
            "7": "View Photo Guide",
            "8": "Photo Inventory",
            "9": "Generate Individual Certificate",
            "10": "Generate Batch Certificate",
            "11": "Generate Final Report",
            "H": "Help & Information",
            "Q": "Quit"
        }

        print_menu("MAIN MENU", menu_options)

        if not pdf_available:
            print("\n⚠ WARNING: reportlab not installed - PDF features disabled")
            print("  Install with: pip install reportlab")

        choice = get_input("\nSelect option").upper()

        try:
            if choice == "1":
                intake_single_item(tracker)
            elif choice == "2":
                intake_batch_items(tracker)
            elif choice == "3":
                view_intake_summary(tracker)
            elif choice == "4":
                record_data_wipe(tracker)
            elif choice == "5":
                record_destruction(tracker)
            elif choice == "6":
                setup_photo_folders(photo_mgr)
            elif choice == "7":
                view_photo_guide(photo_mgr)
            elif choice == "8":
                photo_inventory(photo_mgr)
            elif choice == "9":
                if pdf_available:
                    generate_individual_cert(tracker, cert_gen)
                else:
                    print("❌ PDF features require reportlab")
                    input("Press Enter to continue...")
            elif choice == "10":
                if pdf_available:
                    generate_batch_cert(tracker, cert_gen)
                else:
                    print("❌ PDF features require reportlab")
                    input("Press Enter to continue...")
            elif choice == "11":
                if pdf_available:
                    generate_final_report(tracker, photo_mgr, cert_gen, report_gen)
                else:
                    print("❌ PDF features require reportlab")
                    input("Press Enter to continue...")
            elif choice == "H":
                show_help()
            elif choice == "Q":
                if confirm_action("Are you sure you want to quit?"):
                    print("\nThank you for using the E-Waste Tracking System!")
                    break
            else:
                print("❌ Invalid option")
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")


def show_help():
    """Display help information"""
    clear_screen()
    print("=" * 80)
    print("HELP & INFORMATION")
    print("=" * 80)

    help_text = """
WORKFLOW OVERVIEW:

1. INTAKE (Options 1-2)
   - Log all items as they arrive
   - Generate unique Asset IDs for tracking
   - Record serial numbers and condition
   - Can log items individually or in batches

2. PROCESSING (Options 4-5)
   - Record data wipe for tablets and computers
   - Record destruction completion
   - Link photos to assets
   - Update technician information

3. EVIDENCE (Options 6-8)
   - Setup organised photo folders
   - Take photos during destruction
   - Name files using asset IDs
   - Verify photo inventory

4. DOCUMENTATION (Options 9-11)
   - Generate individual certificates per item
   - Generate batch certificates for groups
   - Create final compliance report for client

TIPS FOR VOLUNTEERS:

- Always log items at intake first
- Take photos BEFORE, DURING, and AFTER destruction
- Use the asset ID in photo filenames
- Generate certificates after destruction is complete
- Create final report when entire job is done

COMPLIANCE:

This system ensures compliance with:
- ISO 9001:2015 (Quality Management)
- WEEE Regulations 2013 (E-Waste)
- UK GDPR 2018 (Data Protection)

All records are timestamped and traceable for audit purposes.
    """

    print(help_text)
    input("\nPress Enter to return to main menu...")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
