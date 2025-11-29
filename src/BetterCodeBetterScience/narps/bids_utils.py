from typing import Dict, List, Union
from pathlib import Path


def parse_bids_filename(filename) -> Dict[str, str]:
    """
    Parse a BIDS-like filename into its components.

    Parameters
    ----------
    filename : str or Path
        BIDS-like filename (string or Path object)

    Returns
    -------
    dict
        Dictionary with components of the filename, including 'path' key
    """
    if isinstance(filename, str):
        filepath = Path(filename)
    else:
        filepath = filename
    
    base = filepath.name
    parts = base.split('_')
    # take the last element which is the suffix
    suffix = parts[-1].split('.')[0]
    parts = parts[:-1]  # remove suffix part
    components = {'path': str(filepath), 'suffix': suffix}
    for part in parts:
        if '-' in part:
            key, value = part.split('-', 1)
            components[key] = value
    return components


# take in a set of bids tags (defined as kwargs) and find all files matching them
def find_bids_files(basedir: Union[str, Path], **bids_tags) -> List[Path]:
    """
    Find all files in a BIDS-like directory that match specified tags.

    Parameters
    ----------
    basedir : str or Path
        Base directory to search
    **bids_tags : dict
        Key-value pairs of BIDS tags to match

    Returns
    -------
    list of Path
        List of Path objects for files matching the specified tags
    """
    if isinstance(basedir, str):
        basedir = Path(basedir)
    
    matched_files = []
    for filepath in basedir.rglob('*'):
        if filepath.is_file():
            components = parse_bids_filename(filepath)
            if all(components.get(k) == v for k, v in bids_tags.items()):
                matched_files.append(filepath)
    return matched_files


def modify_bids_filename(filename: Union[str, Path], **bids_tags) -> Union[str, Path]:
    """
    Modify a BIDS-like filename by replacing specified tag values.

    Parameters
    ----------
    filename : str or Path
        Original BIDS-like filename (string or Path object)
    **bids_tags : dict
        Key-value pairs of BIDS tags to modify

    Returns
    -------
    str or Path
        Modified filename with updated tag values, returned in the same type
        as the input (str or Path). Full directory path is preserved.

    Examples
    --------
    >>> modify_bids_filename("sub-123_desc-test_type-1_stat.nii.gz", desc="real")
    'sub-123_desc-real_type-1_stat.nii.gz'
    
    >>> modify_bids_filename("sub-01_task-rest_bold.nii", task="memory", run="02")
    'sub-01_task-memory_run-02_bold.nii'
    """
    # Track input type
    input_is_string = isinstance(filename, str)
    
    if input_is_string:
        filepath = Path(filename)
    else:
        filepath = filename
    
    # Get directory and original filename
    parent_dir = filepath.parent
    original_name = filepath.name
    
    # Get the file extension(s)
    if '.' in original_name:
        # Handle both .nii.gz and .nii cases
        ext_parts = original_name.split('.')
        extension = '.' + '.'.join(ext_parts[1:])
    else:
        extension = ''
    
    # Parse original filename to extract key-value pairs in order
    base = original_name
    if '.' in base:
        base = base.split('.')[0]  # Remove extension
    
    parts = base.split('_')
    suffix = parts[-1]  # Last part is the suffix
    kv_parts = parts[:-1]  # Everything before suffix
    
    # Build ordered list of (key, value) tuples, preserving original order
    ordered_pairs = []
    existing_keys = set()
    
    for part in kv_parts:
        if '-' in part:
            key, value = part.split('-', 1)
            # Update value if modification requested
            if key in bids_tags:
                value = bids_tags[key]
            ordered_pairs.append((key, value))
            existing_keys.add(key)
    
    # Add any new keys from bids_tags that weren't in original
    for key, value in bids_tags.items():
        if key not in existing_keys:
            ordered_pairs.append((key, value))
    
    # Reconstruct filename maintaining order
    new_parts = [f"{key}-{value}" for key, value in ordered_pairs]
    new_filename = '_'.join(new_parts) + f"_{suffix}{extension}"
    
    # Reconstruct full path
    new_filepath = parent_dir / new_filename
    
    # Return in same type as input
    if input_is_string:
        return str(new_filepath)
    else:
        return new_filepath


def bids_summary(
    basedir: Union[str, Path],
    extension: str = ".nii.gz",
    verbose: bool = True
) -> Dict[str, Dict[str, int]]:
    """
    Summarize BIDS files in a directory by counting images for each type within each desc.

    Parameters
    ----------
    basedir : str or Path
        Base directory containing BIDS files
    extension : str, optional
        File extension to filter (default: ".nii.gz")
    verbose : bool, optional
        Whether to print summary to screen (default: True)

    Returns
    -------
    dict
        Nested dictionary with structure:
        {desc_value: {type_value: count, ...}, ...}
        If desc is not present, uses 'no_desc' as key.
        If type is not present, uses 'no_type' as key.

    Examples
    --------
    >>> summary = bids_summary("/data/narps", extension=".nii.gz", verbose=True)
    Summary of BIDS files in /data/narps (*.nii.gz):
    desc-orig:
      type-thresh: 10 files
      type-unthresh: 10 files
    desc-rect:
      type-thresh: 5 files
    """
    if isinstance(basedir, str):
        basedir = Path(basedir)
    
    # Find all files with the specified extension
    if extension.startswith('.'):
        pattern = f"*{extension}"
    else:
        pattern = f"*.{extension}"
    
    all_files = list(basedir.rglob(pattern))
    
    # Count by desc and type
    summary_dict = {}
    
    for filepath in all_files:
        components = parse_bids_filename(filepath)
        
        # Get desc and type, with defaults if missing
        desc_value = components.get('desc', 'no_desc')
        type_value = components.get('type', 'no_type')
        
        # Initialize nested dict if needed
        if desc_value not in summary_dict:
            summary_dict[desc_value] = {}
        
        if type_value not in summary_dict[desc_value]:
            summary_dict[desc_value][type_value] = 0
        
        summary_dict[desc_value][type_value] += 1
    
    # Print summary if verbose
    if verbose:
        print(f"Summary of BIDS files in {basedir} (*{extension}):")
        if not summary_dict:
            print("  No files found")
        else:
            for desc, type_counts in sorted(summary_dict.items()):
                print(f"  desc-{desc}:")
                for type_val, count in sorted(type_counts.items()):
                    print(f"    type-{type_val}: {count} files")
    
    return summary_dict

