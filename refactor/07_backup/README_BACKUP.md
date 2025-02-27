# Vidst Code Backup System

This directory contains backup utilities and backed-up code for the Vidst refactoring project.

## Important Backups

- **[PRE_REFACTOR_BACKUP](./PRE_REFACTOR_BACKUP)** - Complete backup of the codebase before refactoring began

## Available Backup Tools

The following backup tools have been created to help manage code during the refactoring process:

### 1. Shell Backup Script (`backup_code.sh`)

A shell script for creating complete backups of directories and files. This is typically used before major refactoring operations.

**Usage:**

```bash
# Back up specific directories
./backup_code.sh src tests

# Back up specific files
./backup_code.sh src/main.py config.json

# Back up a mix of files and directories
./backup_code.sh src/utils.py tests
```

**Features:**

- Creates timestamped backups
- Preserves directory structure
- Handles both files and directories
- Creates backups in `refactor/07_backup/code_backups_TIMESTAMP/`

### 2. Python Backup Helper (`backup_helper.py`)

A more flexible Python utility for targeted backups, with additional features for pattern matching and custom backup locations.

**Usage as a Command Line Tool:**

```bash
# Back up a single file
python refactor/07_backup/backup_helper.py file path/to/file.py

# Back up an entire directory
python refactor/07_backup/backup_helper.py dir path/to/directory

# Back up files matching a pattern
python refactor/07_backup/backup_helper.py pattern "src/**/*.py"

# Specify a custom backup location
python refactor/07_backup/backup_helper.py file path/to/file.py --backup-dir custom/backup/dir
```

**Usage as a Python Module:**

```python
from refactor.07_backup.backup_helper import backup_file, backup_directory, backup_by_pattern

# Back up a single file
backup_path = backup_file("path/to/file.py")
print(f"Backed up to: {backup_path}")

# Back up a directory
backup_path = backup_directory("path/to/directory")
print(f"Backed up to: {backup_path}")

# Back up files matching a pattern
backup_paths = backup_by_pattern("src/**/*.py")
print(f"Backed up {len(backup_paths)} files")
```

## Backup Directory Structure

The backup system organizes backups as follows:

- `code_backups_TIMESTAMP/` - Full backups created by the shell script
- `file_backups/` - Individual file backups
- `directory_backups/` - Directory backups

## Best Practices

1. **Always back up before major changes**
   - Create a full backup before beginning significant refactoring
   - Use descriptive commit messages after successful changes

2. **Use the right tool for the job**
   - For single files: `backup_helper.py file path/to/file.py`
   - For entire components: `backup_code.sh src/component`
   - For patterns: `backup_helper.py pattern "src/**/*.py"`

3. **Backup Retention**
   - Keep backups until the refactored code is stable and tested
   - Consider removing old backups once code is merged and deployed

4. **Integration with Git**
   - These backups complement (not replace) version control
   - Use Git for standard versioning and these tools for additional safety

## Troubleshooting

If you encounter issues with the backup tools:

1. **Permission Denied**
   - Ensure scripts are executable: `chmod +x backup_code.sh`
   - Ensure you have write permissions to backup directories

2. **No Files Backed Up**
   - Check that your file paths are correct
   - For pattern matching, ensure quotes are used: `"src/**/*.py"`

3. **Custom Backup Locations**
   - When using custom backup locations, ensure the parent directory exists
