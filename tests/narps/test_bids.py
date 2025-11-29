"""Tests for BIDS utility functions."""

import pytest
from pathlib import Path
import tempfile
import shutil

from BetterCodeBetterScience.narps.bids_utils import (
    parse_bids_filename,
    find_bids_files,
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
