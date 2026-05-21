"""
Submission script for ray tracing exercise.

Usage:
    uv run submit.py
    uv run submit.py --student2 "firstname-lastname" --id2 "123456789"
"""

import argparse
import zipfile
import os
import sys

STUDENT1_NAME = "noam-adda"
STUDENT1_ID = "209087634"

# Files/dirs to include in the zip
INCLUDE_FILES = [
    "hw3.py",
    "helper_classes.py",
    "Ray Tracing Assignment.ipynb",
]
INCLUDE_DIRS = [
    "scenes",
]

# Patterns to exclude
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", ".ipynb_checkpoints"}
EXCLUDE_EXTENSIONS = {".pyc"}
EXCLUDE_FILES = {".DS_Store", ".python-version"}


def should_exclude(path):
    parts = path.replace("\\", "/").split("/")
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    basename = os.path.basename(path)
    if basename in EXCLUDE_FILES:
        return True
    if os.path.splitext(basename)[1] in EXCLUDE_EXTENSIONS:
        return True
    return False


def build_zip_name(name1, id1, name2=None, id2=None):
    base = f"ex03_{name1}-{id1}"
    if name2 and id2:
        base += f"_{name2}-{id2}"
    return base + ".zip"


def main():
    parser = argparse.ArgumentParser(description="Create submission zip.")
    parser.add_argument("--student2", default=None, help="Second student name (firstname-lastname)")
    parser.add_argument("--id2", default=None, help="Second student ID")
    args = parser.parse_args()

    if (args.student2 is None) != (args.id2 is None):
        print("Error: provide both --student2 and --id2, or neither.")
        sys.exit(1)

    zip_name = build_zip_name(STUDENT1_NAME, STUDENT1_ID, args.student2, args.id2)
    root = os.path.dirname(os.path.abspath(__file__))

    added = []
    skipped = []

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename in INCLUDE_FILES:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                zf.write(filepath, filename)
                added.append(filename)
            else:
                print(f"  WARNING: {filename} not found, skipping.")

        for dirname in INCLUDE_DIRS:
            dirpath = os.path.join(root, dirname)
            if not os.path.isdir(dirpath):
                print(f"  WARNING: directory '{dirname}/' not found, skipping.")
                continue
            for dirroot, dirs, files in os.walk(dirpath):
                # Prune excluded dirs in-place
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    abs_path = os.path.join(dirroot, file)
                    rel_path = os.path.relpath(abs_path, root)
                    if should_exclude(rel_path):
                        skipped.append(rel_path)
                        continue
                    zf.write(abs_path, rel_path)
                    added.append(rel_path)

    print(f"\nCreated: {zip_name}")
    print(f"  {len(added)} files added")
    if skipped:
        print(f"  {len(skipped)} files skipped (cache/system files)")


if __name__ == "__main__":
    main()
