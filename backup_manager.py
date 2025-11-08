"""Backup manager for creating and restoring bundle file backups."""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple


class BackupManager:
    """Manages backup operations for bundle files."""
    
    def __init__(self, bundle_dir: Path):
        """
        Initialize backup manager.
        
        Args:
            bundle_dir: Path to the bundle directory (e.g., fm_Data/StreamingAssets/aa/StandaloneWindows64)
        """
        self.bundle_dir = Path(bundle_dir)
        self.backup_dir = self.bundle_dir / "backup"
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, bundle_path: Path, timestamp: Optional[str] = None, original: bool = False) -> Tuple[Path, bool]:
        """
        Create a backup of a bundle file.
        
        Args:
            bundle_path: Path to the bundle file to backup
            timestamp: Optional timestamp string (defaults to current time, ignored if original=True)
            original: If True, create an "original" backup with fixed name (only if it doesn't exist)
            
        Returns:
            Tuple of (Path to the backup file, bool indicating if backup was newly created)
        """
        if original:
            # Use fixed name for original backups
            backup_name = f"{bundle_path.name}.original"
            backup_path = self.backup_dir / backup_name
            
            # Only create if it doesn't already exist
            if backup_path.exists():
                return backup_path, False
        else:
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{bundle_path.name}.{timestamp}"
            backup_path = self.backup_dir / backup_name
        
        if bundle_path.exists():
            shutil.copy2(bundle_path, backup_path)
            return backup_path, True
        else:
            raise FileNotFoundError(f"Bundle file not found: {bundle_path}")
    
    def create_backups(self, bundle_paths: List[Path], timestamp: Optional[str] = None, original: bool = False) -> Tuple[List[Path], bool]:
        """
        Create backups for multiple bundle files.
        
        Args:
            bundle_paths: List of paths to bundle files
            timestamp: Optional timestamp string (shared across all backups, ignored if original=True)
            original: If True, create "original" backups with fixed names (only if they don't exist)
            
        Returns:
            Tuple of (List of paths to backup files, bool indicating if any new backups were created)
        """
        backup_paths = []
        any_created = False
        for bundle_path in bundle_paths:
            backup_path, created = self.create_backup(bundle_path, timestamp, original=original)
            backup_paths.append(backup_path)
            if created:
                any_created = True
        
        return backup_paths, any_created
    
    def get_original_backup(self, bundle_name: str) -> Optional[Path]:
        """
        Get the original backup for a bundle (if it exists).
        
        Args:
            bundle_name: Name of the bundle file
            
        Returns:
            Path to original backup or None if not found
        """
        original_backup = self.backup_dir / f"{bundle_name}.original"
        if original_backup.exists():
            return original_backup
        return None
    
    def list_backups(self, bundle_name: Optional[str] = None) -> List[Path]:
        """
        List available backups.
        
        Args:
            bundle_name: Optional bundle name to filter by
            
        Returns:
            List of backup file paths, sorted by modification time (newest first)
        """
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file():
                if bundle_name is None or backup_file.name.startswith(bundle_name):
                    backups.append(backup_file)
        
        # Sort by modification time, newest first
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return backups
    
    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """
        Restore a backup file to its original location.
        
        Args:
            backup_path: Path to the backup file
            target_path: Path where the backup should be restored
            
        Returns:
            True if successful, False otherwise
        """
        if not backup_path.exists():
            return False
        
        try:
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"Failed to restore backup: {e}")
            return False
    
    def get_latest_backup(self, bundle_name: str) -> Optional[Path]:
        """
        Get the most recent backup for a bundle.
        
        Args:
            bundle_name: Name of the bundle file
            
        Returns:
            Path to latest backup or None if no backups found
        """
        backups = self.list_backups(bundle_name)
        if backups:
            return backups[0]
        return None

