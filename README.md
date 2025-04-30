# File Collector

A simple Python utility for collecting multiple files into a single text file and expanding them back to individual files.

## Features

- **Collect Mode**: Combines multiple files into a single text file with a standardized format
- **Expand Mode**: Extracts files from a collected file, recreating the original file structure
- **Automatic Dating**: Default output files include the current date
- **Smart Expansion**: Can automatically use the most recent collected file
- **Backup Management**: Clean up or restore backup files created during expansion
- **Timestamping**: Option to add epoch timestamps to output filenames

## Installation

No installation required. Simply download `file_collector.py` and ensure you have Python 3.x installed.

```bash
chmod +x file_collector.py  # Make executable (optional)
```

## Usage

### Collect Mode

Combine multiple files into a single output file:

```bash
# Basic usage (creates collected_files_YYYY-MM-DD.txt)
python file_collector.py file1.txt file2.txt path/to/file3.txt

# Specify output file
python file_collector.py -o output.txt file1.txt file2.txt

# Explicit collect mode
python file_collector.py --collect -o output.txt file1.txt file2.txt

# Add epoch timestamp to filename (creates collected_files_YYYY-MM-DD_1234567890.txt)
python file_collector.py --add-epoch file1.txt file2.txt

# Custom filename with epoch timestamp (creates output_1234567890.txt)
python file_collector.py --add-epoch -o output.txt file1.txt file2.txt
```

### Expand Mode

Extract files from a collected file:

```bash
# Use the most recent collected file
python file_collector.py --expand

# Specify input file
python file_collector.py --expand --input collected_files.txt
```

### Backup Management

Manage backup files created during expansion:

```bash
# Restore files to state before expansion (using epoch timestamp)
python file_collector.py --restore 1234567890

# Clean all backup files
python file_collector.py --clean

# Clean backup files for specific epoch timestamp
python file_collector.py --clean-epoch 1234567890
```

## Options

- `--collect`, `-c`: Collect mode (default if no mode specified)
- `--expand`, `-e`: Expand mode
- `--output`, `-o`: Specify output file for collect mode
- `--input`, `-i`: Specify input file for expand mode
- `--add-epoch`, `-E`: Add epoch timestamp to output filename
- `--restore`, `-r`: Restore files to state before expansion (requires epoch timestamp)
- `--clean`, `-C`: Clean all backup files
- `--clean-epoch`: Clean backup files for specific epoch timestamp
- `files`: List of files to process (required for collect mode)

## File Format

The collected file format uses a simple structure:

```
----------
file1.txt
Contents of file1...
----------
path/to/file2.txt
Contents of file2...
```

## Requirements

- Python 3.x
