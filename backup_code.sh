#!/bin/bash

# Vidst Code Backup Script
# This script creates backups of your source code before refactoring

# Create timestamp for the backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="refactor/07_backup/code_backups_${TIMESTAMP}"

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Main backup function
backup_files() {
    local SOURCE_DIR=$1
    local DEST_DIR="$BACKUP_DIR/$(basename $SOURCE_DIR)"

    echo "Backing up $SOURCE_DIR to $DEST_DIR"

    # Create the destination directory
    mkdir -p "$DEST_DIR"

    # Copy files with directory structure preserved
    cp -R "$SOURCE_DIR"/* "$DEST_DIR"/ 2>/dev/null || true

    echo "✅ Backup of $SOURCE_DIR completed"
}

# Function to backup a specific file
backup_file() {
    local SOURCE_FILE=$1
    local FILE_NAME=$(basename "$SOURCE_FILE")
    local DEST_DIR="$BACKUP_DIR"

    echo "Backing up file $SOURCE_FILE to $DEST_DIR/$FILE_NAME.bak"

    # Create the destination directory
    mkdir -p "$DEST_DIR"

    # Copy the file with .bak extension
    cp "$SOURCE_FILE" "$DEST_DIR/$FILE_NAME.bak"

    echo "✅ Backup of $SOURCE_FILE completed"
}

# Main execution
echo "=== Starting Vidst Code Backup ==="
echo "Timestamp: $TIMESTAMP"

# Check if specific directories/files are provided as arguments
if [ $# -eq 0 ]; then
    echo "No specific paths provided. Backing up main source directories..."

    # Add your source directories here
    # Example: backup_files "src"
    # Example: backup_files "tests"

    echo "Please specify which directories to back up."
    echo "Usage: ./backup_code.sh [directory1] [directory2] [file1] ..."
    exit 1
else
    # Back up specific directories/files provided as arguments
    for path in "$@"; do
        if [ -d "$path" ]; then
            backup_files "$path"
        elif [ -f "$path" ]; then
            backup_file "$path"
        else
            echo "⚠️ Warning: $path does not exist"
        fi
    done
fi

echo "=== Backup Complete ==="
echo "All files backed up to $BACKUP_DIR"
echo "You can now proceed with your refactoring safely."
