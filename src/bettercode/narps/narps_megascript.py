## This is a megascript to run the NARPS preprocessing workflow
## This will serve as the basis for refactoring into a more modular workflow later.

import os
import dotenv
from pathlib import Path
import tarfile
import urllib.request
import shutil
from bettercode.narps.bids_utils import (
    parse_bids_filename,
    find_bids_files,
    modify_bids_filename,
)
from nilearn.maskers import NiftiMasker
import nilearn.image
import nibabel as nib
import numpy as np
import json
import templateflow.api as tflow
from nilearn.image import resample_to_img
import pandas as pd
from scipy.stats import norm, t

dotenv.load_dotenv()

## 1. Download data
# - the organized data are available from https://zenodo.org/record/3528329/files/narps_origdata_1.0.tgz

assert (
    'NARPS_DATADIR' in os.environ
), 'Please set NARPS_DATADIR in your environment variables or .env file'
basedir = Path(os.environ['NARPS_DATADIR'])
if not basedir.exists():
    basedir.mkdir(parents=True, exist_ok=True)

narps_data_url = (
    'https://zenodo.org/record/3528329/files/narps_origdata_1.0.tgz'
)
narps_data_archive = basedir / 'narps_origdata_1.0.tgz'

overwrite_data = False

if not narps_data_archive.exists() or overwrite_data:

    print(f'Downloading NARPS data from {narps_data_url}...')
    urllib.request.urlretrieve(narps_data_url, narps_data_archive)
    print('Download complete.')

origdir = basedir / 'orig'
if not origdir.exists() or overwrite_data:
    print('Extracting data...')
    with tarfile.open(narps_data_archive, 'r:gz') as tar:
        tar.extractall(path=basedir)
    print('Extraction complete.')

logdir = basedir / 'logs'
if not logdir.exists():
    logdir.mkdir(parents=True, exist_ok=True)


## 2. convert orig data to a BIDS-like organization

overwrite = False
datadir = basedir / 'data-teams'
if datadir.exists() and overwrite:
    shutil.rmtree(datadir)

if not datadir.exists():
    datadir.mkdir(parents=True, exist_ok=True)

# Get info about teams - we will only process data for hypothesis 1 here
# team dirs are in orig, starting with numeric team IDs

teamdirs = sorted(
    [d for d in origdir.iterdir() if d.is_dir() and d.name[0].isdigit()]
)
print(f'Found {len(teamdirs)} team directories.')
team_dict = {d.name: {'orig': d} for d in teamdirs}

# we will only process hypothesis 1 for this analysis for the sake of speed
target_hypothesis = 1

team_id_to_number = {}

for team_id, paths in team_dict.items():
    # only use the team number
    team_id_short = team_id.split('_')[0]
    team_id_to_number[team_id.split('_')[1]] = team_id_short
    team_orig_dir = paths['orig']
    # include "thresh" to prevent some additional files from being detected
    for type in ['thresh', 'unthresh']:
        for img_file in team_orig_dir.glob(f'*_{type}.nii.gz'):
            hyp, imgtype = (
                img_file.name.split('.')[0].replace('hypo', '').split('_')
            )
            try:
                int(hyp)
            except ValueError:
                print(
                    f'Unexpected hypothesis number format in file {img_file}, skipping.'
                )
                continue
            if int(hyp) != target_hypothesis:
                continue
            dest_file = (
                datadir
                / f'team-{team_id_short}_hyp-{hyp}_type-{imgtype}_space-native_desc-orig_stat.nii.gz'
            )
            if not dest_file.exists():
                print(f'Copying {img_file} to {dest_file}')
                shutil.copy(img_file.resolve(), dest_file)
            assert parse_bids_filename(dest_file)['team'] == team_id_short
            assert parse_bids_filename(dest_file)['hyp'] == hyp
            assert parse_bids_filename(dest_file)['type'] == imgtype

## 3. QC to identify bad data and move them to excluded data dir
# look for:
#  - different image dimensions or affine between thresh and unthresh images for a given team/hyp
# - missing thresholded images
# - need for rectification (i.e. mostly negative values in unthresh image within the mask defined by the thresh image)
#  - invalid in-mask values (i.e. both positive and negative values in unthresh image within the mask defined by the thresh image) - don't exclude, just note in log

datadir_excluded = basedir / 'data-teams-excluded'
if not datadir_excluded.exists():
    datadir_excluded.mkdir(parents=True, exist_ok=True)

qc_results = {}
error_thresh = 0.1  # proportion of invalid in-mask values to flag problem

print('Running QC on original images...')
unthresh_images = find_bids_files(datadir, type='unthresh', desc='orig')
print(f'Found {len(unthresh_images)} unthresh original images to QC.')

for unthresh_img_path in unthresh_images:
    components = parse_bids_filename(unthresh_img_path)
    hyp_num = int(components['hyp'])
    team_id = components['team']
    result = {
        'hyp': hyp_num,
        'team_id': team_id,
        'infile': str(unthresh_img_path),
    }
    thresh_img_path = modify_bids_filename(unthresh_img_path, type='thresh')
    if not Path(thresh_img_path).exists():
        print(
            f'Thresholded image not found for hyp {hyp_num}, team {team_id}, moving to excluded data.'
        )
        shutil.move(
            unthresh_img_path, datadir_excluded / unthresh_img_path.name
        )
        result['exclusion'] = 'thresholded image not found'
        qc_results[str(unthresh_img_path)] = result
        continue

    # Load images
    unthresh_img = nib.load(str(unthresh_img_path))
    thresh_img = nib.load(str(thresh_img_path))

    # check image dimensions and affine
    if unthresh_img.shape != thresh_img.shape or not np.allclose(
        unthresh_img.affine, thresh_img.affine
    ):
        print(
            f"Image shape or affine mismatch for hyp {components['hyp']}, team {components['team']}, moving to excluded data."
        )
        shutil.move(
            unthresh_img_path, datadir_excluded / unthresh_img_path.name
        )
        shutil.move(
            thresh_img_path, datadir_excluded / Path(thresh_img_path).name
        )
        result['exclusion'] = 'image shape or affine mismatch'
        qc_results[str(unthresh_img_path)] = result
        continue

    thresh_data = thresh_img.get_fdata().flatten()
    thresh_data = np.nan_to_num(thresh_data)
    n_thresh_vox = np.sum(thresh_data > 0)
    # check for min_p_direction > error_thresh
    result['n_thresh_vox'] = int(n_thresh_vox)

    # decide whether to rectify based on in-mask values
    # and info from researcher survey

    if n_thresh_vox > 0:
        masker = NiftiMasker(mask_img=thresh_img)
        masker.fit()
        unthresh_data_masked = masker.transform(str(unthresh_img_path))

        min_val = float(np.min(unthresh_data_masked.flatten()))
        max_val = float(np.max(unthresh_data_masked.flatten()))
        p_pos_unthresh = float(np.mean(unthresh_data_masked.flatten() > 0))
        p_neg_unthresh = float(np.mean(unthresh_data_masked.flatten() < 0))
        result['min_unthresh'] = min_val
        result['max_unthresh'] = max_val
        result['p_pos_unthresh'] = p_pos_unthresh
        result['p_neg_unthresh'] = p_neg_unthresh

        if p_neg_unthresh > (1 - error_thresh):
            # mostly negative values, rectify
            result['autorectify'] = True
        else:
            result['autorectify'] = False

        # Check for problems - note these in QC but don't exclude
        min_p_direction = min(p_pos_unthresh, p_neg_unthresh)
        if min_p_direction > error_thresh:
            result['problem'] = 'invalid in-mask values'
            print(
                f'hyp {hyp_num}, team {team_id} - invalid in-mask values (neg: {p_neg_unthresh:.3f}, pos: {p_pos_unthresh:.3f})'
            )

    qc_results[str(unthresh_img_path)] = result

with open(logdir / 'qc_log.json', 'w') as f:
    json.dump(qc_results, f, indent=4)


## 4 - Get binarized thresholded maps
# some thresholded masks have continuous values, so we will binarize
# them at a small threshold (1e-4)

print('Creating binarized images...')
thresh_images_to_binarize = find_bids_files(
    datadir, type='thresh', desc='orig'
)
print(
    f'Found {len(thresh_images_to_binarize)} thresh binarized images to process.'
)

results = {}
overwrite = False
thresh = 1e-4
for thresh_img_path in thresh_images_to_binarize:
    outfile = Path(
        modify_bids_filename(thresh_img_path, desc='binarized', suffix='mask')
    )
    if outfile.exists() and not overwrite:
        continue

    thresh_img = nib.load(str(thresh_img_path))
    thresh_data = thresh_img.get_fdata()
    thresh_data = np.nan_to_num(thresh_data)
    binarized_data = (np.abs(thresh_data) > thresh).astype(np.float32)
    binarized_img = nib.Nifti1Image(
        binarized_data, thresh_img.affine, thresh_img.header
    )
    binarized_img.to_filename(str(outfile))
    results[str(outfile)] = {
        'infile': str(thresh_img_path),
        'n_nonzero_voxels': int(np.sum(binarized_data)),
    }

with open(logdir / 'binarization_log.json', 'w') as f:
    json.dump(results, f, indent=4)


# 5 - Create rectified images
# some unthresh images need to be rectified (i.e. multiplied by -1)
# so that they match the hypothesis
# we infer this based on the match between thresh and unthresh images

print('Creating rectified images...')
results = {}
overwrite = False

for unthresh_img_path, values in qc_results.items():
    if not Path(unthresh_img_path).exists():
        continue

    output_path = Path(
        modify_bids_filename(unthresh_img_path, desc='rectified')
    )

    if output_path.exists() and not overwrite:
        print(f'Rectified image already exists: {output_path}, skipping.')
        continue

    unthresh_img = nib.load(str(unthresh_img_path))
    unthresh_data = unthresh_img.get_fdata()

    if values.get('autorectify', False):
        # mostly negative values, rectify
        print(f'Rectifying unthresh image for hyp {hyp_num}, team {team_id}')
        rectified_data = -1 * unthresh_data
        qc_results[unthresh_img_path]['rectified'] = True
    else:
        rectified_data = unthresh_data
        qc_results[unthresh_img_path]['rectified'] = False

    rectified_img = nib.Nifti1Image(
        rectified_data, unthresh_img.affine, unthresh_img.header
    )
    rectified_img.to_filename(str(output_path))

    results[str(output_path)] = result

with open(logdir / 'rectification_log.json', 'w') as f:
    json.dump(qc_results, f, indent=4)


## 6:  Get resampled images

## first get MNI152NLin2009cAsym template from templateflow
mni_template = tflow.get(
    'MNI152NLin2009cAsym', resolution=2, suffix='T1w', desc=None
)

print('Resampling images to MNI space...')
results = {}
overwrite = False
all_images_to_resample = find_bids_files(
    datadir, type='thresh', space='native', desc='binarized'
) + find_bids_files(datadir, type='unthresh', space='native', desc='rectified')

print(f'Found {len(all_images_to_resample)} images to resample.')

for img_path in all_images_to_resample:
    components = parse_bids_filename(img_path)
    output_path = Path(
        modify_bids_filename(img_path, space='MNI152NLin2009cAsym')
    )
    results[str(output_path)] = {
        'infile': str(img_path),
    }
    if output_path.exists() and not overwrite:
        continue

    img = nib.load(str(img_path))
    # use linear interpolation for binarized maps, then threshold at 0.5
    # this avoids empty voxels that can occur with NN interpolation
    # resample to MNI space
    if components['desc'] == 'binarized':
        interpolation = 'linear'
    else:
        interpolation = 'continuous'

    resampled_img = resample_to_img(
        img,
        mni_template,
        interpolation=interpolation,
        force_resample=True,
        copy_header=True,
    )

    if components['desc'] == 'binarized':
        interpolation = 'linear'
        # re-binarize
        resampled_data = resampled_img.get_fdata()
        binarized_data = (resampled_data > 0.5).astype(np.float32)
        resampled_img = nib.Nifti1Image(
            binarized_data, resampled_img.affine, resampled_img.header
        )

    resampled_img.to_filename(str(output_path))

with open(logdir / 'resampling_log.json', 'w') as f:
    json.dump(results, f, indent=4)

## 7: convert concatenated unthresh image to z scores
# some teams provided t instead of z scores


def TtoZ(data, df=54):
    """
    takes a nibabel file object and converts from z to t
    using Hughett's transform
    adapted from:
    https://github.com/vsoch/TtoZ/blob/master/TtoZ/scripts.py
    - default to 54 which is full sample per condition for narps
    """

    # Select just the nonzero voxels
    nonzero_vox = data != 0
    nonzero = data[nonzero_vox]

    # We will store our results here
    Z = np.zeros(len(nonzero))

    # Select values less than or == 0, and greater than zero
    c = np.zeros(len(nonzero))
    k1 = nonzero <= c
    k2 = nonzero > c

    # Subset the data into two sets
    t1 = nonzero[k1]
    t2 = nonzero[k2]

    # Calculate p values for <=0
    p_values_t1 = t.cdf(t1, df=df)
    z_values_t1 = norm.ppf(p_values_t1)

    # Calculate p values for > 0
    p_values_t2 = t.cdf(-t2, df=df)
    z_values_t2 = -norm.ppf(p_values_t2)
    Z[k1] = z_values_t1
    Z[k2] = z_values_t2

    # Write new image to file
    new_nii = np.zeros(data.shape)
    new_nii[nonzero_vox] = Z

    return new_nii


print('Converting unthresh images to z-scores...')

# first load the spreadsheet to get the stats types
stats_types_df = pd.read_csv(
    origdir / 'narps_neurovault_images_details_responses_corrected.csv'
)   # .set_index('team_id')
stats_types_df.columns = [
    'Timestamp',
    'team_id',
    'software',
    'unthresh_type',
    'thresh_type',
    'template',
    'h5',
    'h6',
    'h9',
    'comments',
]
stats_types_df['team_number'] = [
    team_id_to_number.get(tid, None) for tid in stats_types_df['team_id']
]

stat_type_by_team = {}
for _, row in stats_types_df.iterrows():
    team_number = row['team_number']
    if 't value' in row['unthresh_type'].strip().lower():
        stat_type_by_team[team_number] = 't'
    else:
        # default to z if unsure - i.e. no conversion
        stat_type_by_team[team_number] = 'z'

for team, stattype in stat_type_by_team.items():
    team_unthresh_images = find_bids_files(
        datadir,
        team=team,
        type='unthresh',
        space='MNI152NLin2009cAsym',
        desc='rectified',
    )
    if len(team_unthresh_images) == 0:
        continue
    if len(team_unthresh_images) > 1:
        print(
            f'Warning: multiple unthresh images found for team {team}, using first one.'
        )
    unthresh_img_path = team_unthresh_images[0]
    output_path = Path(modify_bids_filename(unthresh_img_path, suffix='zstat'))
    if output_path.exists() and not overwrite:
        continue
    unthresh_img = nib.load(str(unthresh_img_path))
    unthresh_data = unthresh_img.get_fdata()
    converted = False
    if stattype == 't':
        unthresh_data = TtoZ(unthresh_data, df=54)
        converted = True
    zstat_img = nib.Nifti1Image(
        unthresh_data, unthresh_img.affine, unthresh_img.header
    )
    zstat_img.to_filename(str(output_path))
    results[str(output_path)] = {
        'infile': str(unthresh_img_path),
        'original_stat_type': stattype,
    }

with open(logdir / 't_to_z_log.json', 'w') as f:
    json.dump(results, f, indent=4)

## 8: Create concatenated versions of all images

concat_dir = basedir / 'data-concat'
if not concat_dir.exists():
    concat_dir.mkdir(parents=True, exist_ok=True)

results = {}
for hyp in [target_hypothesis]:
    print(f'Creating concatenated images for hypothesis {hyp}...')

    resampled_images = {
        'unthresh': find_bids_files(
            datadir,
            type='unthresh',
            space='MNI152NLin2009cAsym',
            hyp=str(hyp),
            suffix='zstat',
        ),
        'thresh': [],
    }
    team_ids = []
    for img_path in resampled_images['unthresh']:
        components = parse_bids_filename(img_path)
        team_ids.append(components['team'])
        thresh_img_path = modify_bids_filename(
            img_path, type='thresh', desc='binarized', suffix='mask'
        )
        assert Path(
            thresh_img_path
        ).exists(), f'Binarized thresholded image not found for {img_path}'
        resampled_images['thresh'].append(thresh_img_path)
    assert len(resampled_images['thresh']) == len(
        resampled_images['unthresh']
    ), 'Mismatch in number of unthresh and thresh images'
    print(
        f'Found {len(team_ids)} unthresh resampled images to concatenate for hypothesis {hyp}.'
    )

    suffix_dict = {'unthresh': 'zstat', 'thresh': 'mask'}
    for imgtype in ['unthresh', 'thresh']:
        img_list = []
        for img_path in resampled_images[imgtype]:
            img = nib.load(str(img_path))
            img_list.append(img)
            img_paths = [p.as_posix() for p in resampled_images[imgtype]]
        # concatenate along 4th dimension
        concat_img = nilearn.image.concat_imgs(img_list)

        output_path = (
            concat_dir
            / f'hyp-{hyp}_type-{imgtype}_space-MNI152NLin2009cAsym_desc-concat_{suffix_dict[imgtype]}.nii.gz'
        )
        concat_img.to_filename(str(output_path))
        print(
            f'Saved concatenated {imgtype} image for hypothesis {hyp} to {output_path}'
        )
        results[str(output_path)] = {'infiles': img_paths}

with open(logdir / 'concatenation_log.json', 'w') as f:
    json.dump(results, f, indent=4)
