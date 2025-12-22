## Problems to be fixed

Open problems marked with [ ]
Fixed problems marked with [x]


[x] Please change the file naming scheme for the checkpoint files to use a BIDS schema, just like the downloaded data.
    - Implemented `bids_checkpoint_name()` and `parse_bids_checkpoint_name()` functions
    - Checkpoint files now use format: `dataset-{name}_step-{number}_desc-{description}.{extension}`
    - Updated `list_checkpoints()` and `clear_checkpoints_from_step()` to support both BIDS and legacy naming

[x] Please save the checkpoint h5ad files using compression='gzip'
    - Added `compression="gzip"` to `data.write()` in `save_checkpoint()` function

[x] The size of the checkpoint files is very large, I think in part due to their storage of the original counts within the .X variable in the dataset.  However, I'm not sure if and when that's actually necessary, versus simply reloading the original data or an earlier checkpoint to re-populate that variable. Please examine the usage of this .X variable and determine whether it would make more sense to remove it for the sake of space and then reload if needed from an earlier checkpoint.

### Analysis of .X variable usage:

The workflow uses two main data storage locations in AnnData:

1. **`.X`** - The main expression matrix:
   - Steps 2-3: Contains raw counts
   - Steps 4-6: Contains normalized, log-transformed expression data (after preprocessing)
   - Used for: QC metrics, normalization, HVG selection, PCA, neighbor graph, UMAP, clustering

2. **`layers["counts"]`** - Raw counts layer (no longer used):
   - Previously created at end of Step 3 (QC) - now removed
   - Step 7 (pseudobulking) now loads step 3 checkpoint directly to get raw counts from `.X`

**Optimization implemented:**
- Removed `layers["counts"]` creation from step 3 (QC)
- Step 7 (pseudobulking) now loads the step 3 checkpoint to get raw counts from `.X`
- This eliminates redundant storage of raw counts in `layers["counts"]` for steps 3-6 checkpoints

**Storage savings:**
- Steps 3-6 checkpoints now store only `.X` (not both `.X` and `layers["counts"]`)
- Combined with gzip compression, this roughly halves the expression data storage for these checkpoints

After Step 7, the pseudobulk AnnData is a separate object with only aggregated counts in `.X` (no layers needed). Steps 8-11 use pickle/parquet files, not h5ad.

**Selective checkpointing:**
- Added `checkpoint_steps` parameter to `run_stateless_workflow()` (default: `{2, 3, 5}`)
- Only specified steps save checkpoints; other steps run without saving
- Step 3 is always required (provides raw counts for pseudobulking)
- Added `skip_save` parameter to `run_with_checkpoint()` and `run_with_checkpoint_multi()`
