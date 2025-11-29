
import os
from typing import Dict, Optional, Union
from pathlib import Path

import numpy as np
import nibabel as nib


def compare_thresh_unthresh_values(
    thresh_image_path: Union[str, Path],
    unthresh_image_path: Union[str, Path],
    hyp_num: int,
    team_id: Optional[str] = None,
    collection_id: Optional[str] = None,
    error_thresh: float = 0.05,
    verbose: bool = True,
    logger=None,
) -> Dict:
    """
    Examine unthresholded values within thresholded map voxels
    to check direction of maps and determine if rectification is needed.

    If more than error_thresh percent of voxels are in opposite direction,
    then flag a problem. We allow a few to bleed over due to interpolation.

    Parameters
    ----------
    thresh_image_path : str or Path
        Path to thresholded image
    unthresh_image_path : str or Path
        Path to unthresholded image
    hyp_num : int
        Hypothesis number
    team_id : str, optional
        Team identifier
    collection_id : str, optional
        Collection identifier
    error_thresh : float
        Threshold for flagging problems (proportion of voxels in wrong direction)
    verbose : bool
        Whether to print diagnostic messages

    Returns
    -------
    dict
        Dictionary containing diagnostic information:
        - autorectify: bool, whether image should be rectified
        - problem: bool, whether there's a problem with the image
        - n_thresh_vox: int, number of thresholded voxels
        - min_unthresh: float, minimum unthresholded value within mask
        - max_unthresh: float, maximum unthresholded value within mask
        - p_pos_unthresh: float, proportion of positive unthresholded values
        - p_neg_unthresh: float, proportion of negative unthresholded values
    """
    result = {
        "hyp": hyp_num,
        "team_id": team_id,
        "collection_id": collection_id,
        "autorectify": False,
        "problem": False,
        "n_thresh_vox": 0,
        "min_unthresh": np.nan,
        "max_unthresh": np.nan,
        "p_pos_unthresh": np.nan,
        "p_neg_unthresh": np.nan,
    }

    # Check if files exist
    if not os.path.exists(thresh_image_path):
        if verbose and logger:
            logger.warning("Threshold image not found: %s", thresh_image_path)
        return result

    if not os.path.exists(unthresh_image_path):
        if verbose and logger:
            logger.warning("Unthreshold image not found: %s", unthresh_image_path)
        return result

    # Load images
    thresh_img = nib.load(thresh_image_path)
    thresh_data = thresh_img.get_fdata().flatten()
    thresh_data = np.nan_to_num(thresh_data)

    unthresh_img = nib.load(unthresh_image_path)
    unthresh_data = unthresh_img.get_fdata().flatten()
    unthresh_data = np.nan_to_num(unthresh_data)

    # Check shape compatibility
    if thresh_data.shape != unthresh_data.shape:
        if verbose and logger:
            logger.error("thresh/unthresh size mismatch for hyp %d", hyp_num)
        result["problem"] = True
        return result

    # Count thresholded voxels
    n_thresh_vox = np.sum(thresh_data > 0)
    result["n_thresh_vox"] = int(n_thresh_vox)

    if n_thresh_vox == 0:
        if verbose and logger:
            logger.warning("hyp %d - empty mask", hyp_num)
        return result

    # Analyze values within the mask
    inmask_unthresh_data = unthresh_data[thresh_data > 0]

    min_val = float(np.min(inmask_unthresh_data))
    max_val = float(np.max(inmask_unthresh_data))
    p_pos_unthresh = float(np.mean(inmask_unthresh_data > 0))
    p_neg_unthresh = float(np.mean(inmask_unthresh_data < 0))

    result["min_unthresh"] = min_val
    result["max_unthresh"] = max_val
    result["p_pos_unthresh"] = p_pos_unthresh
    result["p_neg_unthresh"] = p_neg_unthresh

    # Check if rectification is needed
    if max_val < 0:  # All values are negative
        result["autorectify"] = True
        if verbose and logger:
            logger.info("Autorectify needed: hyp %d", hyp_num)

    # Check for problems
    min_p_direction = min(p_pos_unthresh, p_neg_unthresh)
    if min_p_direction > error_thresh:
        if verbose and logger:
            logger.warning(
                "hyp %d invalid in-mask values (neg: %.3f, pos: %.3f)",
                hyp_num, p_neg_unthresh, p_pos_unthresh
            )
        result["problem"] = True

    return result
