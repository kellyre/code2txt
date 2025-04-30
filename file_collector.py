#!/usr/bin/env python3
import argparse
import os
import sys
import glob
from datetime import datetime
import time

def collect_files(files, output_file=None, add_epoch=False):
    """Collect content from multiple files into a single output file."""
    if output_file is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_file = f"collected_files_{date_str}.txt"
    
    # Add epoch time to filename if requested
    if add_epoch:
        epoch_time = int(time.time())
        # Split filename and extension
        base, ext = os.path.splitext(output_file)
        output_file = f"{base}_{epoch_time}{ext}"
    
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as in_f:
                    out_f.write('-' * 10 + '\n')
                    out_f.write(f"{file_path}\n")
                    out_f.write(in_f.read())
                    # Add a newline if the file doesn't end with one
                    if in_f.tell() > 0:
                        in_f.seek(in_f.tell() - 1, 0)
                        if in_f.read(1) != '\n':
                            out_f.write('\n')
            except Exception as e:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)
    
    print(f"Files collected into {output_file}")

def find_latest_collected_file():
    """Find the most recent collected_files_<date>.txt file."""
    files = glob.glob("collected_files_*.txt")
    if not files:
        return None
    return max(files, key=os.path.getctime)

def expand_file(input_file):
    """Expand a collected file into individual files."""
    # Get current epoch time once at the start
    epoch_time = int(time.time())
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = content.split('-' * 10 + '\n')
    
    # Skip the first empty section if it exists
    if sections and not sections[0].strip():
        sections = sections[1:]
    
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.splitlines()
        if not lines:
            continue
        
        file_path = lines[0]
        file_content = '\n'.join(lines[1:])
        
        # Create directories if needed
        dir_name = os.path.dirname(file_path)
        if dir_name:  # Only create directories if there's a directory path
            os.makedirs(dir_name, exist_ok=True)
        
        # Handle existing or new files
        base_name = os.path.basename(file_path)
        if os.path.exists(file_path):
            # If file exists, rename it with timestamp prefix
            backup_name = f"orig_{epoch_time}_{base_name}"
            
            if dir_name:
                backup_path = os.path.join(dir_name, backup_name)
            else:
                backup_path = backup_name
                
            os.rename(file_path, backup_path)
            print(f"Renamed existing file to: {backup_path}")
        else:
            # If file didn't exist, create an empty placeholder file
            delete_name = f"orig_delete_{epoch_time}_{base_name}"
            
            if dir_name:
                delete_path = os.path.join(dir_name, delete_name)
            else:
                delete_path = delete_name
                
            with open(delete_path, 'w', encoding='utf-8') as f:
                pass  # Create empty file
            print(f"Created placeholder: {delete_path}")
        
        # Create the new file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Created file: {file_path}")

def find_latest_epoch_time():
    """Find the most recent epoch time used in backup files."""
    orig_files = glob.glob("orig_*_*")
    delete_files = glob.glob("orig_delete_*_*")
    all_files = orig_files + delete_files
    
    if not all_files:
        return None
    
    # Extract epoch times from filenames
    epoch_times = []
    for file in all_files:
        parts = file.split('_')
        if len(parts) >= 3 and parts[0] == 'orig' and parts[1].isdigit():
            epoch_times.append(int(parts[1]))
    
    return max(epoch_times) if epoch_times else None

def restore_files(epoch_time):
    """Restore files to their state before an expand operation."""
    # Check if this is the latest epoch time
    latest_epoch = find_latest_epoch_time()
    if latest_epoch and epoch_time != latest_epoch:
        print(f"Warning: {epoch_time} is not the most recent epoch time ({latest_epoch}).")
        response = input("Do you want to proceed anyway? (y/N): ").strip().lower()
        if not response or response[0] != 'y':
            print("Restore operation cancelled.")
            return
    
    # Find all backup files with the specified epoch time
    orig_pattern = f"orig_{epoch_time}_*"
    delete_pattern = f"orig_delete_{epoch_time}_*"
    
    orig_files = glob.glob(orig_pattern)
    delete_files = glob.glob(delete_pattern)
    
    # Process original files (rename back to original)
    for backup_file in orig_files:
        # Extract original filename
        parts = backup_file.split('_', 2)
        if len(parts) < 3:
            print(f"Skipping invalid backup file: {backup_file}")
            continue
        
        original_file = parts[2]
        
        # Check if the original file exists
        if os.path.exists(original_file):
            try:
                os.remove(original_file)
                print(f"Deleted: {original_file}")
            except Exception as e:
                print(f"Error deleting {original_file}: {e}")
                continue
        
        # Rename backup to original
        try:
            os.rename(backup_file, original_file)
            print(f"Restored: {original_file}")
        except Exception as e:
            print(f"Error restoring {original_file}: {e}")
    
    # Process delete markers (delete the created file)
    for delete_file in delete_files:
        # Extract original filename
        parts = delete_file.split('_', 3)
        if len(parts) < 4:
            print(f"Skipping invalid delete marker: {delete_file}")
            continue
        
        original_file = parts[3]
        
        # Delete the created file if it exists
        if os.path.exists(original_file):
            try:
                os.remove(original_file)
                print(f"Deleted: {original_file}")
            except Exception as e:
                print(f"Error deleting {original_file}: {e}")
        
        # Delete the marker file
        try:
            os.remove(delete_file)
            print(f"Removed marker: {delete_file}")
        except Exception as e:
            print(f"Error removing marker {delete_file}: {e}")
    
    if not orig_files and not delete_files:
        print(f"No backup files found for epoch time {epoch_time}")
    else:
        print(f"Restore completed: processed {len(orig_files)} original files and {len(delete_files)} delete markers")

def clean_backup_files(epoch_time=None):
    """Clean backup and placeholder files.
    
    Args:
        epoch_time: If provided, only clean files with this epoch time.
                   If None, clean all backup files.
    """
    if epoch_time is not None:
        # Clean specific epoch time
        orig_pattern = f"orig_{epoch_time}_*"
        delete_pattern = f"orig_delete_{epoch_time}_*"
    else:
        # Clean all backup files (with 10-digit epoch times)
        orig_pattern = "orig_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*"
        delete_pattern = "orig_delete_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*"
    
    orig_files = glob.glob(orig_pattern)
    delete_files = glob.glob(delete_pattern)
    
    # Remove original backup files
    for file in orig_files:
        try:
            os.remove(file)
            print(f"Removed backup: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")
    
    # Remove delete marker files
    for file in delete_files:
        try:
            os.remove(file)
            print(f"Removed marker: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")
    
    total_removed = len(orig_files) + len(delete_files)
    if total_removed == 0:
        if epoch_time:
            print(f"No backup files found for epoch time {epoch_time}")
        else:
            print("No backup files found")
    else:
        print(f"Cleanup completed: removed {len(orig_files)} backup files and {len(delete_files)} marker files")

def main():
    parser = argparse.ArgumentParser(description='Collect or expand files.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--collect', '-c', action='store_true', help='Collect files into a single output file')
    group.add_argument('--expand', '-e', action='store_true', help='Expand a collected file into individual files')
    group.add_argument('--restore', '-r', type=int, help='Restore files to their state before an expand operation (requires epoch time)')
    group.add_argument('--clean', '-C', action='store_true', help='Clean all backup files')
    group.add_argument('--clean-epoch', type=int, help='Clean backup files for a specific epoch time')
    parser.add_argument('--output', '-o', help='Output file for collect mode')
    parser.add_argument('--input', '-i', help='Input file for expand mode')
    parser.add_argument('--add-epoch', '-E', action='store_true', help='Add epoch time to output filename in collect mode')
    parser.add_argument('files', nargs='*', help='Files to process (required for collect mode)')
    
    args = parser.parse_args()
    
    if args.restore is not None:
        restore_files(args.restore)
    elif args.clean:
        clean_backup_files()
    elif args.clean_epoch is not None:
        clean_backup_files(args.clean_epoch)
    elif args.expand:
        input_file = args.input
        if not input_file:
            input_file = find_latest_collected_file()
            if not input_file:
                parser.error("No collected files found and no input file specified")
            print(f"Using latest collected file: {input_file}")
        expand_file(input_file)
    else:  # Default is collect mode
        if not args.files:
            parser.error("Collect mode requires at least one file to process")
        collect_files(args.files, args.output, args.add_epoch)

if __name__ == "__main__":
    main()
