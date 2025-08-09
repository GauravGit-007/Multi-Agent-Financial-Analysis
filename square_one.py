import os
import glob

def reset_project():
    """
    Deletes all generated CSV and XLSX files in the current folder.
    This will NOT touch Python scripts, the .venv folder, or requirements files.
    """
    patterns = ["*.csv", "*.xlsx"]

    deleted_files = []

    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                deleted_files.append(file)
            except Exception as e:
                print(f"⚠️ Could not delete {file}: {e}")

    if deleted_files:
        print("🗑 Deleted files:")
        for f in deleted_files:
            print(f"  - {f}")
    else:
        print("✅ No CSV/XLSX files found to delete.")

    print("\nProject folder reset to a clean state.")

if __name__ == "__main__":
    reset_project()
