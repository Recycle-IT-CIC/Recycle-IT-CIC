#!/usr/bin/env python3
"""
Test script for E-Waste Tracking System
Verifies all components work correctly
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from config import PROJECT_NAME, VERSION, ITEM_TYPES
        print(f"  ✓ Config loaded: {PROJECT_NAME} v{VERSION}")

        from asset_tracker import AssetTracker
        print("  ✓ AssetTracker imported")

        from photo_manager import PhotoManager
        print("  ✓ PhotoManager imported")

        try:
            from certificate_generator import CertificateGenerator
            from report_generator import ReportGenerator
            print("  ✓ PDF generators imported (reportlab available)")
            return True
        except ImportError:
            print("  ⚠ PDF generators not available (reportlab not installed)")
            return False

    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_asset_tracker():
    """Test asset tracking functionality"""
    print("\nTesting AssetTracker...")
    try:
        from asset_tracker import AssetTracker

        tracker = AssetTracker()

        # Test single asset creation
        record = tracker.create_asset_record(
            "CABINET",
            serial_number="TEST-001",
            condition="Used - Good",
            notes="Test cabinet"
        )

        assert record["Asset ID"].startswith("CAB-")
        assert record["Item Type"] == "Charging Cabinet"
        print(f"  ✓ Created test asset: {record['Asset ID']}")

        # Test batch creation
        records = tracker.batch_create_assets(
            "TABLET_10_NEW",
            quantity=5,
            condition="New/Sealed",
            base_serial="TEST-T10"
        )

        assert len(records) == 5
        print(f"  ✓ Created batch of 5 assets")

        # Test save to CSV
        tracker.save_to_csv(records, append=False)
        print(f"  ✓ Saved to CSV: {tracker.intake_log_path.name}")

        # Test load from CSV
        loaded = tracker.load_intake_log(tracker.intake_log_path)
        assert len(loaded) == 5
        print(f"  ✓ Loaded {len(loaded)} records from CSV")

        # Test summary stats
        stats = tracker.get_summary_stats(loaded)
        assert stats["total_items"] == 5
        print(f"  ✓ Statistics calculated: {stats['total_items']} items")

        return True

    except Exception as e:
        print(f"  ❌ AssetTracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_photo_manager():
    """Test photo management functionality"""
    print("\nTesting PhotoManager...")
    try:
        from photo_manager import PhotoManager

        photo_mgr = PhotoManager()

        # Test folder structure creation
        folders = photo_mgr.create_folder_structure("TEST_Job")
        assert len(folders) > 0
        print(f"  ✓ Created {len(folders)} item type folders")

        # Test filename generation
        filename = photo_mgr.generate_photo_filename("CAB-20250107-0001", "destruction", 1)
        assert "CAB-20250107-0001" in filename
        assert "destruction" in filename
        print(f"  ✓ Generated filename: {filename}")

        # Test photo inventory
        inventory = photo_mgr.create_photo_inventory()
        print(f"  ✓ Photo inventory created")

        return True

    except Exception as e:
        print(f"  ❌ PhotoManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_certificate_generator():
    """Test certificate generation"""
    print("\nTesting CertificateGenerator...")
    try:
        from certificate_generator import CertificateGenerator
        from asset_tracker import AssetTracker
        from config import get_current_date

        tracker = AssetTracker()
        cert_gen = CertificateGenerator()

        # Create test record
        record = tracker.create_asset_record(
            "TABLET_10_NEW",
            serial_number="CERT-TEST-001",
            condition="New/Sealed",
            notes="Test for certificate"
        )

        # Add destruction info
        record["Destruction Date"] = get_current_date()
        record["Destruction Method"] = "Physical Shredding"
        record["Destruction Technician"] = "Test User"

        # Generate certificate
        cert_path = cert_gen.generate_individual_certificate(record, "TEST-CERT-001")
        assert cert_path.exists()
        print(f"  ✓ Individual certificate generated: {cert_path.name}")

        # Test batch certificate
        records = [record] * 3  # Simulate 3 items
        batch_path = cert_gen.generate_batch_certificate(records, "TEST_Batch")
        assert batch_path.exists()
        print(f"  ✓ Batch certificate generated: {batch_path.name}")

        return True

    except ImportError:
        print("  ⚠ Skipped (reportlab not installed)")
        return True
    except Exception as e:
        print(f"  ❌ CertificateGenerator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generator():
    """Test report generation"""
    print("\nTesting ReportGenerator...")
    try:
        from report_generator import ReportGenerator
        from asset_tracker import AssetTracker
        from photo_manager import PhotoManager
        from config import get_current_date

        tracker = AssetTracker()
        report_gen = ReportGenerator()
        photo_mgr = PhotoManager()

        # Create test records
        records = []
        for i in range(10):
            record = tracker.create_asset_record(
                "TABLET_10_NEW",
                serial_number=f"RPT-TEST-{i:03d}",
                condition="New/Sealed"
            )
            record["Destruction Date"] = get_current_date()
            record["Destruction Method"] = "Physical Shredding"
            record["Destruction Technician"] = "Test User"
            records.append(record)

        # Generate report
        photo_inventory = photo_mgr.create_photo_inventory()
        report_path = report_gen.generate_final_report(
            records,
            photo_inventory,
            [],
            "TEST_Report"
        )

        assert report_path.exists()
        print(f"  ✓ Final report generated: {report_path.name}")

        return True

    except ImportError:
        print("  ⚠ Skipped (reportlab not installed)")
        return True
    except Exception as e:
        print(f"  ❌ ReportGenerator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directory_structure():
    """Test that all required directories exist"""
    print("\nTesting directory structure...")
    try:
        from config import INTAKE_LOGS_DIR, PHOTO_EVIDENCE_DIR, CERTIFICATES_DIR, REPORTS_DIR

        dirs = {
            "intake_logs": INTAKE_LOGS_DIR,
            "photo_evidence": PHOTO_EVIDENCE_DIR,
            "certificates": CERTIFICATES_DIR,
            "reports": REPORTS_DIR
        }

        for name, path in dirs.items():
            assert path.exists(), f"{name} directory not found"
            print(f"  ✓ {name}/ exists")

        return True

    except Exception as e:
        print(f"  ❌ Directory test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("E-WASTE TRACKING SYSTEM - TEST SUITE")
    print("=" * 70)

    results = {
        "imports": test_imports(),
        "directories": test_directory_structure(),
        "asset_tracker": test_asset_tracker(),
        "photo_manager": test_photo_manager(),
        "certificate_generator": test_certificate_generator(),
        "report_generator": test_report_generator()
    }

    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())

    print("=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
