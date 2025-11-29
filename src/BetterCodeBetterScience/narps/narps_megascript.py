## This is a megascript to run the NARPS preprocessing workflow
## This will serve as the basis for refactoring into a more modular workflow later.

import os
import dotenv
from pathlib import Path
import tarfile
import urllib.request
from typing import Dict, List, Union
import shutil
from BetterCodeBetterScience.narps.bids_utils import (
    parse_bids_filename,
    find_bids_files,
    modify_bids_filename
)
from nilearn.maskers import NiftiMasker
import nibabel as nib
import numpy as np

dotenv.load_dotenv()




## Download data
# - the organized data are available from https://zenodo.org/record/3528329/files/narps_origdata_1.0.tgz

assert 'NARPS_DATADIR' in os.environ, "Please set NARPS_DATADIR in your environment variables or .env file"
basedir = Path(os.environ['NARPS_DATADIR'])
if not basedir.exists():
    basedir.mkdir(parents=True, exist_ok=True)

narps_data_url = "https://zenodo.org/record/3528329/files/narps_origdata_1.0.tgz"
narps_data_archive = basedir / "narps_origdata_1.0.tgz"

overwrite_data = False

if not narps_data_archive.exists() or overwrite_data:

    print(f"Downloading NARPS data from {narps_data_url}...")
    urllib.request.urlretrieve(narps_data_url, narps_data_archive)
    print("Download complete.")

origdir = basedir / "orig"
if not origdir.exists() or overwrite_data:
    print("Extracting data...")
    with tarfile.open(narps_data_archive, "r:gz") as tar:
        tar.extractall(path=basedir)
    print("Extraction complete.")


## Get info about teams and hypotheses
## team dirs are in orig, starting with numeric team IDs

teamdirs = sorted([d for d in origdir.iterdir() if d.is_dir() and d.name[0].isdigit()])
print(f"Found {len(teamdirs)} team directories.")
team_dict = {d.name: {'orig': d} for d in teamdirs}

# convert orig data to a BIDS-like organization

overwrite = False
datadir = basedir / "data"
if datadir.exists() and overwrite:
    shutil.rmtree(datadir)

if not datadir.exists():
    datadir.mkdir(parents=True, exist_ok=True)

for team_id, paths in team_dict.items():
    # only use the team number
    team_id_short = team_id.split('_')[0]
    team_orig_dir = paths['orig']
    # include "thresh" to prevent some additional files from being detected
    for type in ['thresh', 'unthresh']:
        for img_file in team_orig_dir.glob(f"*_{type}.nii.gz"):
            hyp, imgtype = img_file.name.split('.')[0].replace('hypo','').split('_')
            dest_file = datadir / f"team-{team_id_short}_hyp-{hyp}_type-{imgtype}_desc-orig_stat.nii.gz"
            if not dest_file.exists():
                print(f"Copying {img_file} to {dest_file}")
                shutil.copy(img_file.resolve(), dest_file)
            assert parse_bids_filename(dest_file)['team'] == team_id_short
            assert parse_bids_filename(dest_file)['hyp'] == hyp
            assert parse_bids_filename(dest_file)['type'] == imgtype

# - Create rectified images - narps.create_rectified_images()
#     - input: original image (thresh and unthresh versions)
#     - output: rectified images for reverse contrasts
#     - NOTE: see logic within get_binarized_thresh_masks 

print("Creating rectified images...")
unthresh_images_to_rectify = find_bids_files(
    datadir, type='unthresh', desc='orig')

for unthresh_img_path in unthresh_images_to_rectify:
    components = parse_bids_filename(unthresh_img_path)
    hyp_num = int(components['hyp'])
    team_id = components['team']
    result = {
        "hyp": hyp_num,
        "team_id": team_id,
    }
    thresh_img_path = modify_bids_filename(
        unthresh_img_path,
        type='thresh'
    )
    if not Path(thresh_img_path).exists():
        print(f"Thresholded image not found for hyp {hyp_num}, team {team_id}, skipping rectification.")
        result["problem"] = 'thresholded image not found'
        continue

    output_path = Path(modify_bids_filename(
        unthresh_img_path,
        desc='rectified'
    ))
    result["output_path"] = str(output_path)
    if output_path.exists() and not overwrite:
        print(f"Rectified image already exists: {output_path}, skipping.")
        continue

    # recitification involves looking at the values of the unthresh
    # image within the mask defined by the thresholded image
    unthresh_img = nib.load(str(unthresh_img_path))
    thresh_img = nib.load(str(thresh_img_path))

    # check image dimensions
    if unthresh_img.shape != thresh_img.shape:
        print(f"Image shape mismatch for hyp {components['hyp']}, team {components['team']}, skipping rectification.")
        result["problem"] = 'image shape mismatch'
        continue
    thresh_data = thresh_img.get_fdata().flatten()
    thresh_data = np.nan_to_num(thresh_data)
    n_thresh_vox = np.sum(thresh_data > 0)
    result["n_thresh_vox"] = int(n_thresh_vox)
    if n_thresh_vox == 0:
        print(f"Empty mask for hyp {components['hyp']}, team {components['team']}, skipping rectification.")
        continue

    masker = NiftiMasker(mask_img=thresh_img)
    masker.fit()
    unthresh_data = masker.transform(str(unthresh_img_path)).flatten()

ljksadf


# - Get binarized thresholded maps (narps.get_binarized_thresh_masks())
#     - input: thresholded original image
#     - output: binarized version


# - Get resampled images (narps.get_resampled_images())
#     - input: all image types (thresh, bin, unthresh)
#     - output: resampled image in MNI space


# - Create concatenated versions of all images - narps.create_concat_imag
#     - input: individual 3d images
#     - output: combined 4d images for each image type


# - Check image values - narps.check_image_values()
#     - input: thresholded images
#     - output: data frame with number of NA and nonzero voxels 


# - Create mean thresholded images - narps.create_mean_thresholded_images()
#     - input: contact thresh image
#     - output: mean thresholded image


# - Convert to zscores - narps.convert_to_zscores()
#     - input: unthresh rectified images
#     - output: zscore images


# - Create concatenated utnhresh zstat images - narps.create_concat_images(datatype='zstat', imgtypes=['unthresh'],
#                                create_voxel_map=True)
#         input: zstat images
#         output: concatenated 4d zstat image
#         NOTE: maynbe consider using the concatenated unthresh image to compute zstats


## Analyses

# - Compute image stats - narps.compute_image_stats()
#     input: unthresholded concatenated files
#     output: range and std images

# - Estimate smoothness - narps.estimate_smoothness() - relies upon FSL smoothest
#     input: individual 3d team zstat images
#     output: dataframe containing smoothness estimates for each team


# ### Map analysis functions

# NOTE: the following three are largely duplicative
# - Create overlap maps - AnalyzeMaps.mk_overlap_maps
#     input: mean thresholded images
#     output: pdf and png files with rendering of map on anatomy
# - Create range maps - AnalyzeMaps.mk_range_maps
#     input: range images
#     output: pdf/png files with rendering of range map on anatomy
# - Create std maps - AnalyzeMaps.mk_std_maps
#     input: std images
#     output: pdf/png files with rendering of std map on anatomy

# - Unthresholded correlation analysis - test_unthresh_correlation_analysis
# - Create correlation maps for unthresholded images - AnalyzeMaps.mk_correlation_maps_unthresh
#     input: concatenated unthresholded images
#     output: 
#         - median pattern correlation (?)
#         - df containing correlation matrix between datasets for each hypothesis
#         - png/pdf images of clustermap based on correlation matrix
#         - cluster membership (saved as json)
#         - reordered correlation matrix based on ward clustering
#         - dendrograms for each hypothesis
#     NOTE: this one has WAY too much going on - good candidate for refactoring example!
# - Analyze clusters - AnalyzeMaps.analyze_clusters
#     input: dendrograms and membership dict 
#     output:
#         - mean unthresholded map for each cluster/hypothesis
#         - various stats output to logfile
#         -pdf/png files with rendered thresholded map for each cluster
#         - cluster metadata saved to csv
#         - cluster similarity (rand scores) saved to csv
#         - consistency of cluster membership across hypotheses
# - Plot distance from mean - AnalyzeMaps.plot_distance_from_mean(narps)
#     input: median pattern correlation
#     output:
#         - pdf with bar plot of correlations across teams
#         - pdf of bar plot excluding teams above .2 correlation (i.e. only bad teams)
# - Get similarity of thresholded images - AnalyzeMaps.get_thresh_similarity(narps)
#     input: concatenated thresholded data
#     output:
#         - df with percent agreement
#         - pdf/png with cluster map of percent agreement
#         - mean jaccard for nonzero voxels
# - Get thresholded z-stat maps - utils.get_thresholded_Z_maps(narps)
#     input: unthresholded z maps and thresholded binarized maps
#     output: thresholded Z maps
#     NOTE: currently done on individual maps, probably should do on concatenated
# - Get diagnostics on thresholded maps - ThreshVoxelStatistics.get_zstat_diagnostics(narps)
#     input: thresholded and unthresholded maps
#     output: diagnostic data comparing thresh and unthresh for each team
# - Get stats on thresholded maps - ThreshVoxelStatistics.get_thresh_voxel_stats(narps.basedir)
#     input: individual diagnostic data frames
#     output:
#         - df with all diagnostic data combined
#         - df with statistics on thresholded maps
# - Get similarity summary - GetMeanSimilarity.get_similarity_summary()
#     input:  correlation data frames, cluster membership json
#     output:
#         - png with histogram of correlations
#         - pngs with hisrogram of correlations for each cluster
#         - data frame with correlation results by hyp/group


# ### Consensus analysis functions

# - run t-tests - ConsensusAnalysis.run_ttests
#     input: unthresholded zstat images
#     output:
#         - t, pval, and fdr image for each hypothesis
#         - tau image for each hypothesis
# - make figures - ConsensusAnalysis.mk_figures()
#     input: t and fdr images
#     output: 
#         - pdf with rendered consensus images
#         - pdf with rendered tau maps
#         - pdf with rendered tau histograms

# - Compute cluster similarity for Tom et al. and mean activation - ClusterImageCorrelation.cluster_image_correlation
#     input: cluster images and target image (mean or tom et al)
#     output: 
#         - correlation maps for each cluster vs target for each hyp
#         - df with cluster correlations for each hyp

# - Make combined cluster figures - MakeCombinedClusterFigures.make_combined_cluster_figures
#     input: pngs for corr map and cluster means
#     output: png with combined cluster images
# - Make supp figure 1 - MakeSupplementaryFigure1.mk_supp_figure1
#     input: metadata
#     output: 
#         - csv tables with merged metadata, decision data, and confidence data
#         - png image with confidence data and modeling info

