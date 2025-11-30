"""Tests for BIDS utility functions."""

import pytest
from pathlib import Path
import tempfile
import shutil

from BetterCodeBetterScience.narps.bids_utils import (
    parse_bids_filename,
    find_bids_files,
    modify_bids_filename,
    bids_summary,
)


# Tests for parse_bids_filename


def test_parse_bids_filename_basic_string():
    """Test parsing a basic BIDS filename from a string."""
    filename = "sub-01_task-rest_bold.nii.gz"
    result = parse_bids_filename(filename)
    
    assert result['sub'] == '01'
    assert result['task'] == 'rest'
    assert result['suffix'] == 'bold'
    assert 'path' in result
    assert result['path'] == filename


def test_parse_bids_filename_path_object():
    """Test parsing a BIDS filename from a Path object."""
    filepath = Path("/data/sub-02_ses-01_T1w.nii.gz")
    result = parse_bids_filename(filepath)
    
    assert result['sub'] == '02'
    assert result['ses'] == '01'
    assert result['suffix'] == 'T1w'
    assert result['path'] == str(filepath)


def test_parse_bids_filename_complex():
    """Test parsing a complex BIDS filename with multiple entities."""
    filename = "sub-01_ses-02_task-rest_acq-mb_run-01_bold.nii.gz"
    result = parse_bids_filename(filename)
    
    assert result['sub'] == '01'
    assert result['ses'] == '02'
    assert result['task'] == 'rest'
    assert result['acq'] == 'mb'
    assert result['run'] == '01'
    assert result['suffix'] == 'bold'


def test_parse_bids_filename_with_hyphen_in_value():
    """Test parsing when a value contains a hyphen."""
    filename = "sub-control-01_task-go-nogo_bold.nii"
    result = parse_bids_filename(filename)
    
    # Should split only on first hyphen
    assert result['sub'] == 'control-01'
    assert result['task'] == 'go-nogo'
    assert result['suffix'] == 'bold'


def test_parse_bids_filename_narps_format():
    """Test parsing NARPS-specific filename format."""
    filename = "sub-team01_hyp-1_type-thresh_desc-orig_stat.nii.gz"
    result = parse_bids_filename(filename)
    
    assert result['sub'] == 'team01'
    assert result['hyp'] == '1'
    assert result['type'] == 'thresh'
    assert result['desc'] == 'orig'
    assert result['suffix'] == 'stat'


def test_parse_bids_filename_with_full_path():
    """Test parsing with a full absolute path."""
    filepath = Path("/home/user/data/sub-03_T2w.nii.gz")
    result = parse_bids_filename(filepath)
    
    assert result['sub'] == '03'
    assert result['suffix'] == 'T2w'
    assert result['path'] == str(filepath)
    # Should only parse the filename, not the directory
    assert 'home' not in result
    assert 'user' not in result


def test_parse_bids_filename_minimal():
    """Test parsing a minimal BIDS filename."""
    filename = "sub-01_bold.nii"
    result = parse_bids_filename(filename)
    
    assert result['sub'] == '01'
    assert result['suffix'] == 'bold'
    assert len(result) == 3  # sub, suffix, path


def test_parse_bids_filename_no_extension():
    """Test parsing a filename without extension."""
    filename = "sub-01_task-rest_bold"
    result = parse_bids_filename(filename)
    
    assert result['sub'] == '01'
    assert result['task'] == 'rest'
    assert result['suffix'] == 'bold'


# Tests for find_bids_files


@pytest.fixture
def temp_bids_dir():
    """Create a temporary BIDS-like directory structure for testing."""
    tmpdir = tempfile.mkdtemp()
    basedir = Path(tmpdir)
    
    # Create test files
    files = [
        "sub-01_task-rest_bold.nii.gz",
        "sub-01_task-rest_T1w.nii.gz",
        "sub-01_task-memory_bold.nii.gz",
        "sub-02_task-rest_bold.nii.gz",
        "sub-02_task-memory_bold.nii.gz",
        "sub-03_ses-01_task-rest_bold.nii.gz",
        "sub-03_ses-02_task-rest_bold.nii.gz",
    ]
    
    for filename in files:
        filepath = basedir / filename
        filepath.touch()
    
    yield basedir
    
    # Cleanup
    shutil.rmtree(tmpdir)


def test_find_bids_files_single_tag(temp_bids_dir):
    """Test finding files with a single BIDS tag."""
    results = find_bids_files(temp_bids_dir, sub='01')
    
    assert len(results) == 3
    assert all('sub-01' in r.name for r in results)


def test_find_bids_files_multiple_tags(temp_bids_dir):
    """Test finding files with multiple BIDS tags."""
    results = find_bids_files(temp_bids_dir, sub='01', task='rest')
    
    assert len(results) == 2
    filenames = [r.name for r in results]
    assert "sub-01_task-rest_bold.nii.gz" in filenames
    assert "sub-01_task-rest_T1w.nii.gz" in filenames


def test_find_bids_files_with_suffix(temp_bids_dir):
    """Test finding files filtered by suffix."""
    results = find_bids_files(temp_bids_dir, suffix='bold')
    
    assert len(results) == 6
    assert all('bold' in r.name for r in results)


def test_find_bids_files_no_matches(temp_bids_dir):
    """Test finding files when no matches exist."""
    results = find_bids_files(temp_bids_dir, sub='99')
    
    assert len(results) == 0


def test_find_bids_files_all_tags_must_match(temp_bids_dir):
    """Test that all specified tags must match."""
    results = find_bids_files(temp_bids_dir, sub='01', task='rest', suffix='bold')
    
    assert len(results) == 1
    assert results[0].name == "sub-01_task-rest_bold.nii.gz"


def test_find_bids_files_with_session(temp_bids_dir):
    """Test finding files with session tag."""
    results = find_bids_files(temp_bids_dir, sub='03', ses='01')
    
    assert len(results) == 1
    assert results[0].name == "sub-03_ses-01_task-rest_bold.nii.gz"


def test_find_bids_files_string_basedir(temp_bids_dir):
    """Test that basedir can be a string."""
    results = find_bids_files(str(temp_bids_dir), sub='02')
    
    assert len(results) == 2
    assert all('sub-02' in r.name for r in results)


def test_find_bids_files_no_tags(temp_bids_dir):
    """Test finding files with no tag filters returns all files."""
    results = find_bids_files(temp_bids_dir)
    
    assert len(results) == 7


def test_find_bids_files_nonexistent_tag(temp_bids_dir):
    """Test filtering by a tag that doesn't exist in any files."""
    results = find_bids_files(temp_bids_dir, run='01')
    
    assert len(results) == 0


@pytest.fixture
def temp_narps_dir():
    """Create a temporary NARPS-like directory structure."""
    tmpdir = tempfile.mkdtemp()
    basedir = Path(tmpdir)
    
    # Create NARPS-style test files
    files = [
        "sub-team01_hyp-1_type-thresh_desc-orig_stat.nii.gz",
        "sub-team01_hyp-1_type-unthresh_desc-orig_stat.nii.gz",
        "sub-team01_hyp-2_type-thresh_desc-orig_stat.nii.gz",
        "sub-team02_hyp-1_type-thresh_desc-orig_stat.nii.gz",
        "sub-team02_hyp-1_type-thresh_desc-rect_stat.nii.gz",
    ]
    
    for filename in files:
        filepath = basedir / filename
        filepath.touch()
    
    yield basedir
    
    shutil.rmtree(tmpdir)


def test_find_bids_files_narps_format(temp_narps_dir):
    """Test finding NARPS-formatted files."""
    results = find_bids_files(temp_narps_dir, sub='team01', hyp='1')
    
    assert len(results) == 2


def test_find_bids_files_narps_by_type(temp_narps_dir):
    """Test finding NARPS files by type."""
    results = find_bids_files(temp_narps_dir, type='thresh')
    
    assert len(results) == 4


def test_find_bids_files_narps_by_desc(temp_narps_dir):
    """Test finding NARPS files by description."""
    results = find_bids_files(temp_narps_dir, desc='rect')
    
    assert len(results) == 1
    assert results[0].name == "sub-team02_hyp-1_type-thresh_desc-rect_stat.nii.gz"


def test_find_bids_files_narps_complex_filter(temp_narps_dir):
    """Test complex filtering on NARPS files."""
    results = find_bids_files(
        temp_narps_dir, 
        sub='team01', 
        hyp='1', 
        type='thresh',
        desc='orig'
    )
    
    assert len(results) == 1
    assert results[0].name == "sub-team01_hyp-1_type-thresh_desc-orig_stat.nii.gz"


# Tests for modify_bids_filename


def test_modify_bids_filename_single_tag():
    """Test modifying a single BIDS tag."""
    original = "sub-123_desc-test_type-1_stat.nii.gz"
    result = modify_bids_filename(original, desc="real")
    
    # Should preserve order and return same type
    assert result == "sub-123_desc-real_type-1_stat.nii.gz"
    assert isinstance(result, str)


def test_modify_bids_filename_multiple_tags():
    """Test modifying multiple BIDS tags at once."""
    original = "sub-01_task-rest_bold.nii"
    result = modify_bids_filename(original, task="memory", run="02")
    
    # Should add run and modify task, preserving original order
    assert result == "sub-01_task-memory_run-02_bold.nii"
    assert isinstance(result, str)


def test_modify_bids_filename_path_object():
    """Test that function works with Path objects."""
    original = Path("sub-01_ses-01_T1w.nii.gz")
    result = modify_bids_filename(original, ses="02")
    
    # Should return Path object when input is Path
    assert isinstance(result, Path)
    assert result.name == "sub-01_ses-02_T1w.nii.gz"


def test_modify_bids_filename_add_new_tag():
    """Test adding a tag that wasn't in the original filename."""
    original = "sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original, run="01", acq="mb")
    
    # New tags should be added at the end (after existing tags)
    assert result == "sub-01_task-rest_run-01_acq-mb_bold.nii.gz"
    assert isinstance(result, str)


def test_modify_bids_filename_preserve_extension():
    """Test that file extensions are preserved."""
    original = "sub-01_bold.nii.gz"
    result = modify_bids_filename(original, sub="02")
    
    assert result.endswith(".nii.gz")
    assert result == "sub-02_bold.nii.gz"


def test_modify_bids_filename_simple_extension():
    """Test with simple extension (not .nii.gz)."""
    original = "sub-01_task-rest_bold.nii"
    result = modify_bids_filename(original, task="memory")
    
    assert result.endswith(".nii")
    assert "task-memory" in result


def test_modify_bids_filename_no_extension():
    """Test with no file extension."""
    original = "sub-01_task-rest_bold"
    result = modify_bids_filename(original, task="memory")
    
    assert "task-memory" in result
    assert not result.endswith(".")


def test_modify_bids_filename_narps_format():
    """Test modifying NARPS-specific fields."""
    original = "sub-team01_hyp-1_type-thresh_desc-orig_stat.nii.gz"
    result = modify_bids_filename(original, desc="rect", type="unthresh")
    
    assert "desc-rect" in result
    assert "type-unthresh" in result
    assert "hyp-1" in result
    assert "sub-team01" in result


def test_modify_bids_filename_change_subject():
    """Test changing the subject ID."""
    original = "sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original, sub="99")
    
    # Should preserve order with modified subject
    assert result == "sub-99_task-rest_bold.nii.gz"


def test_modify_bids_filename_preserve_suffix():
    """Test that suffix is preserved when modifying other tags."""
    original = "sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original, task="memory")
    
    assert result.endswith("_bold.nii.gz")


def test_modify_bids_filename_change_suffix():
    """Test changing the suffix."""
    original = "sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original, suffix="T1w")
    
    # Suffix should be at the end, not as suffix-value
    assert result == "sub-01_task-rest_T1w.nii.gz"
    assert "suffix-" not in result


def test_modify_bids_filename_change_suffix_and_tags():
    """Test changing both suffix and other tags."""
    original = "sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original, task="memory", suffix="T1w")
    
    assert result == "sub-01_task-memory_T1w.nii.gz"
    assert "suffix-" not in result


def test_modify_bids_filename_complex_modification():
    """Test complex modification with many changes."""
    original = "sub-01_ses-01_task-rest_acq-mb_bold.nii.gz"
    result = modify_bids_filename(
        original,
        sub="02",
        ses="03",
        task="memory",
        run="01"
    )
    
    # Should preserve original order and append new tag
    assert result == "sub-02_ses-03_task-memory_acq-mb_run-01_bold.nii.gz"


def test_modify_bids_filename_hyphenated_value():
    """Test that hyphenated values are handled correctly."""
    original = "sub-control-01_task-go_bold.nii"
    result = modify_bids_filename(original, task="go-nogo")
    
    # Should preserve order with hyphenated values
    assert result == "sub-control-01_task-go-nogo_bold.nii"


def test_modify_bids_filename_empty_modification():
    """Test that calling with no modifications returns identical filename."""
    original = "sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original)
    
    # Should return exactly the same filename
    assert result == original


def test_modify_bids_filename_with_full_path():
    """Test modification preserves full directory path."""
    original = Path("/data/bids/sub-01_task-rest_bold.nii.gz")
    result = modify_bids_filename(original, task="memory")
    
    # Result should preserve the full directory path
    assert isinstance(result, Path)
    assert result == Path("/data/bids/sub-01_task-memory_bold.nii.gz")
    assert result.parent == Path("/data/bids")
    assert result.name == "sub-01_task-memory_bold.nii.gz"


def test_modify_bids_filename_string_with_path():
    """Test that string input with directory path preserves the path."""
    original = "/data/bids/sub-01_task-rest_bold.nii.gz"
    result = modify_bids_filename(original, task="memory")
    
    # Should return string and preserve directory path
    assert isinstance(result, str)
    assert result == "/data/bids/sub-01_task-memory_bold.nii.gz"


def test_modify_bids_filename_order_preservation():
    """Test that original key order is strictly preserved."""
    original = "sub-01_desc-orig_type-thresh_hyp-1_stat.nii.gz"
    result = modify_bids_filename(original, type="unthresh")
    
    # Order should be exactly: sub, desc, type, hyp
    assert result == "sub-01_desc-orig_type-unthresh_hyp-1_stat.nii.gz"


def test_modify_bids_filename_relative_path():
    """Test with relative path."""
    original = Path("data/sub-01_task-rest_bold.nii.gz")
    result = modify_bids_filename(original, task="memory")
    
    assert isinstance(result, Path)
    assert result == Path("data/sub-01_task-memory_bold.nii.gz")
    assert result.parent == Path("data")


# Tests for bids_summary


@pytest.fixture
def temp_summary_dir():
    """Create a temporary directory with various BIDS files for summary testing."""
    tmpdir = tempfile.mkdtemp()
    basedir = Path(tmpdir)
    
    # Create test files with different desc and type combinations
    files = [
        "sub-team01_desc-orig_type-thresh_hyp-1_stat.nii.gz",
        "sub-team01_desc-orig_type-thresh_hyp-2_stat.nii.gz",
        "sub-team01_desc-orig_type-unthresh_hyp-1_stat.nii.gz",
        "sub-team01_desc-orig_type-unthresh_hyp-2_stat.nii.gz",
        "sub-team02_desc-orig_type-thresh_hyp-1_stat.nii.gz",
        "sub-team02_desc-rect_type-thresh_hyp-1_stat.nii.gz",
        "sub-team02_desc-rect_type-unthresh_hyp-1_stat.nii.gz",
        "sub-team03_desc-rect_type-thresh_hyp-1_stat.nii.gz",
        # Files without desc or type
        "sub-team04_hyp-1_stat.nii.gz",
        "sub-team05_desc-orig_hyp-1_stat.nii.gz",
        # Different extension (should be excluded by default)
        "sub-team01_desc-orig_type-thresh_hyp-1_stat.nii",
    ]
    
    for filename in files:
        filepath = basedir / filename
        filepath.touch()
    
    yield basedir
    
    shutil.rmtree(tmpdir)


def test_bids_summary_basic(temp_summary_dir, capsys):
    """Test basic summary functionality."""
    result = bids_summary(temp_summary_dir, verbose=False)
    
    # Check the structure
    assert 'orig' in result
    assert 'rect' in result
    
    # Check counts for orig
    assert result['orig']['thresh'] == 3
    assert result['orig']['unthresh'] == 2
    
    # Check counts for rect
    assert result['rect']['thresh'] == 2
    assert result['rect']['unthresh'] == 1


def test_bids_summary_verbose_output(temp_summary_dir, capsys):
    """Test that verbose mode prints summary."""
    result = bids_summary(temp_summary_dir, verbose=True)
    
    captured = capsys.readouterr()
    assert "Summary of BIDS files" in captured.out
    assert "desc-orig:" in captured.out
    assert "desc-rect:" in captured.out
    assert "type-thresh:" in captured.out
    assert "type-unthresh:" in captured.out


def test_bids_summary_no_verbose(temp_summary_dir, capsys):
    """Test that verbose=False suppresses output."""
    result = bids_summary(temp_summary_dir, verbose=False)
    
    captured = capsys.readouterr()
    assert captured.out == ""


def test_bids_summary_different_extension(temp_summary_dir):
    """Test filtering by different extension."""
    result = bids_summary(temp_summary_dir, extension=".nii", verbose=False)
    
    # Should find only the .nii file
    assert 'orig' in result
    assert result['orig']['thresh'] == 1
    # Should not find .nii.gz files
    assert result['orig'].get('unthresh') is None


def test_bids_summary_no_desc(temp_summary_dir):
    """Test handling of files without desc tag."""
    result = bids_summary(temp_summary_dir, verbose=False)
    
    # Files without desc should be grouped under 'no_desc'
    assert 'no_desc' in result


def test_bids_summary_no_type(temp_summary_dir):
    """Test handling of files without type tag."""
    result = bids_summary(temp_summary_dir, verbose=False)
    
    # Check for files with desc but no type
    assert 'orig' in result
    assert 'no_type' in result['orig']
    assert result['orig']['no_type'] == 1


def test_bids_summary_empty_directory():
    """Test summary on empty directory."""
    tmpdir = tempfile.mkdtemp()
    try:
        result = bids_summary(tmpdir, verbose=False)
        assert result == {}
    finally:
        shutil.rmtree(tmpdir)


def test_bids_summary_string_path(temp_summary_dir):
    """Test that function accepts string paths."""
    result = bids_summary(str(temp_summary_dir), verbose=False)
    
    assert isinstance(result, dict)
    assert 'orig' in result


def test_bids_summary_extension_with_dot(temp_summary_dir):
    """Test that extension works with or without leading dot."""
    result1 = bids_summary(temp_summary_dir, extension=".nii.gz", verbose=False)
    result2 = bids_summary(temp_summary_dir, extension="nii.gz", verbose=False)
    
    # Both should produce same results
    assert result1 == result2


def test_bids_summary_nested_directories():
    """Test summary works with nested directory structures."""
    tmpdir = tempfile.mkdtemp()
    basedir = Path(tmpdir)
    
    try:
        # Create nested structure
        subdir1 = basedir / "sub-01"
        subdir2 = basedir / "sub-02" / "nested"
        subdir1.mkdir(parents=True)
        subdir2.mkdir(parents=True)
        
        (subdir1 / "sub-01_desc-orig_type-thresh_stat.nii.gz").touch()
        (subdir2 / "sub-02_desc-orig_type-thresh_stat.nii.gz").touch()
        
        result = bids_summary(basedir, verbose=False)
        
        # Should find files in nested directories
        assert result['orig']['thresh'] == 2
        
    finally:
        shutil.rmtree(tmpdir)


def test_bids_summary_return_structure(temp_summary_dir):
    """Test that return structure is correct type."""
    result = bids_summary(temp_summary_dir, verbose=False)
    
    assert isinstance(result, dict)
    for desc_key, type_dict in result.items():
        assert isinstance(desc_key, str)
        assert isinstance(type_dict, dict)
        for type_key, count in type_dict.items():
            assert isinstance(type_key, str)
            assert isinstance(count, int)
            assert count > 0

