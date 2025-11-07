"""
Photo Evidence Management System
Organises and links photographic evidence to asset records
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional

try:
    from .config import PHOTO_EVIDENCE_DIR, ITEM_TYPES, get_file_timestamp
except ImportError:
    from config import PHOTO_EVIDENCE_DIR, ITEM_TYPES, get_file_timestamp


class PhotoManager:
    """Manages photo evidence organisation and linking"""

    def __init__(self):
        self.base_dir = PHOTO_EVIDENCE_DIR

    def create_folder_structure(self, job_name: str = "LBQ_Job") -> Dict[str, Path]:
        """
        Create organised folder structure for photo evidence
        Returns dict mapping item types to their photo directories
        """
        timestamp = get_file_timestamp()
        job_dir = self.base_dir / f"{job_name}_{timestamp}"

        folders = {}

        print(f"\nCreating photo evidence folder structure in:")
        print(f"  {job_dir}")

        for item_code, config in ITEM_TYPES.items():
            if config["requires_photo"]:
                folder_name = config["name"].replace("/", "_").replace("\"", "")
                item_folder = job_dir / folder_name
                item_folder.mkdir(parents=True, exist_ok=True)
                folders[item_code] = item_folder
                print(f"  ✓ {folder_name}/")

        # Create additional folders for different stages
        stages = ["before_destruction", "during_destruction", "after_destruction", "proof_sheets"]
        for stage in stages:
            stage_folder = job_dir / stage
            stage_folder.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {stage}/")

        print(f"\n✓ Photo evidence folders created successfully")
        return folders

    def generate_photo_filename(self, asset_id: str, stage: str = "destruction", sequence: int = 1) -> str:
        """
        Generate standardised photo filename
        Format: ASSETID_STAGE_SEQ_TIMESTAMP.jpg
        Example: CAB-20250107-0001_destruction_01_20250107_143022.jpg
        """
        timestamp = get_file_timestamp()
        return f"{asset_id}_{stage}_{sequence:02d}_{timestamp}.jpg"

    def link_photo_to_asset(self, asset_id: str, photo_path: str) -> str:
        """
        Create a relative path link between photo and asset
        Returns the relative path string for storage in CSV
        """
        photo_path_obj = Path(photo_path)

        if not photo_path_obj.exists():
            print(f"Warning: Photo file does not exist: {photo_path}")

        # Store relative path from project root
        try:
            relative_path = photo_path_obj.relative_to(self.base_dir.parent)
            return str(relative_path)
        except ValueError:
            # If path is not relative to base, store absolute
            return str(photo_path_obj)

    def copy_photo_to_evidence(self,
                               source_path: str,
                               asset_id: str,
                               item_type: str,
                               stage: str = "destruction",
                               sequence: int = 1) -> Optional[Path]:
        """
        Copy a photo from camera/device to evidence folder with proper naming
        """
        source = Path(source_path)

        if not source.exists():
            print(f"Error: Source photo not found: {source_path}")
            return None

        # Find the appropriate folder
        job_folders = list(self.base_dir.glob("LBQ_Job_*"))
        if not job_folders:
            print("Error: No job folders found. Create folder structure first.")
            return None

        # Use most recent job folder
        job_folder = sorted(job_folders, reverse=True)[0]

        # Determine destination based on item type
        item_config = ITEM_TYPES.get(item_type)
        if not item_config:
            print(f"Error: Invalid item type: {item_type}")
            return None

        folder_name = item_config["name"].replace("/", "_").replace("\"", "")
        dest_folder = job_folder / folder_name

        if not dest_folder.exists():
            dest_folder.mkdir(parents=True, exist_ok=True)

        # Generate filename and copy
        filename = self.generate_photo_filename(asset_id, stage, sequence)
        dest_path = dest_folder / filename

        try:
            shutil.copy2(source, dest_path)
            print(f"✓ Photo copied: {filename}")
            return dest_path
        except Exception as e:
            print(f"Error copying photo: {e}")
            return None

    def create_photo_inventory(self, job_folder: Optional[str] = None) -> Dict:
        """
        Create an inventory of all photos in a job folder
        Returns dict with statistics and file lists
        """
        if job_folder:
            folder = Path(job_folder)
        else:
            # Use most recent job folder
            job_folders = sorted(self.base_dir.glob("LBQ_Job_*"), reverse=True)
            if not job_folders:
                print("No job folders found.")
                return {}
            folder = job_folders[0]

        inventory = {
            "job_folder": str(folder),
            "total_photos": 0,
            "by_item_type": {},
            "by_stage": {},
            "file_list": []
        }

        # Scan for all image files
        for img_ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            for img_file in folder.rglob(img_ext):
                inventory["total_photos"] += 1
                inventory["file_list"].append(str(img_file.relative_to(folder)))

                # Categorise by parent folder (item type)
                parent_name = img_file.parent.name
                inventory["by_item_type"][parent_name] = inventory["by_item_type"].get(parent_name, 0) + 1

                # Try to extract stage from filename
                if "_" in img_file.stem:
                    parts = img_file.stem.split("_")
                    if len(parts) > 1:
                        stage = parts[1]
                        inventory["by_stage"][stage] = inventory["by_stage"].get(stage, 0) + 1

        return inventory

    def generate_photo_proof_sheet_data(self, asset_records: List[Dict]) -> List[Dict]:
        """
        Generate data for creating proof sheets (grid of photos with asset IDs)
        Returns list of assets with their photo paths
        """
        proof_data = []

        for record in asset_records:
            if record["Photo Evidence Path"]:
                proof_data.append({
                    "asset_id": record["Asset ID"],
                    "item_type": record["Item Type"],
                    "photo_path": record["Photo Evidence Path"],
                    "destruction_date": record["Destruction Date"]
                })

        return proof_data

    def list_job_folders(self) -> List[str]:
        """List all job folders"""
        folders = sorted(self.base_dir.glob("LBQ_Job_*"), reverse=True)
        return [f.name for f in folders]

    def get_photos_for_asset(self, asset_id: str, job_folder: Optional[str] = None) -> List[Path]:
        """Find all photos associated with an asset ID"""

        if job_folder:
            search_dir = self.base_dir / job_folder
        else:
            # Search most recent job folder
            job_folders = sorted(self.base_dir.glob("LBQ_Job_*"), reverse=True)
            if not job_folders:
                return []
            search_dir = job_folders[0]

        photos = []
        for img_ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            for img_file in search_dir.rglob(img_ext):
                if asset_id in img_file.name:
                    photos.append(img_file)

        return sorted(photos)

    def display_photo_structure_guide(self):
        """Display guide for photo organisation"""
        print("\n" + "=" * 70)
        print("PHOTO EVIDENCE ORGANISATION GUIDE")
        print("=" * 70)
        print("\nFolder Structure:")
        print("  photo_evidence/")
        print("    LBQ_Job_YYYYMMDD_HHMMSS/")
        print("      ├── before_destruction/")
        print("      ├── during_destruction/")
        print("      ├── after_destruction/")
        print("      ├── proof_sheets/")

        for item_code, config in ITEM_TYPES.items():
            if config["requires_photo"]:
                folder_name = config["name"].replace("/", "_").replace("\"", "")
                print(f"      ├── {folder_name}/")

        print("\nFile Naming Convention:")
        print("  ASSETID_STAGE_SEQUENCE_TIMESTAMP.jpg")
        print("  Example: CAB-20250107-0001_destruction_01_20250107_143022.jpg")
        print("\nStages:")
        print("  - before: Item before destruction")
        print("  - destruction: During destruction process")
        print("  - after: After destruction complete")
        print("  - label_removal: Label removal for cabinets")
        print("  - data_wipe: Data sanitisation screens")
        print("\n" + "=" * 70)
