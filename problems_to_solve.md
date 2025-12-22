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

2. **`layers["counts"]`** - Raw counts layer:
   - Created at end of Step 3 (QC) for HVG selection in step 4
   - Deleted after step 4 before step 5 checkpoint is saved
   - Step 7 (pseudobulking) loads step 3 checkpoint directly to get raw counts from `.X`

**Optimization implemented:**
- `layers["counts"]` is created in step 3 (needed for HVG selection in step 4)
- After step 4 (preprocessing), the counts layer is deleted before step 5 saves its checkpoint
- Step 7 (pseudobulking) loads the step 3 checkpoint to get raw counts from `.X`
- This eliminates redundant storage of raw counts in steps 5-6 checkpoints

**Storage savings:**
- Step 3 checkpoint stores both `.X` (raw counts) and `layers["counts"]` (needed for step 4)
- Steps 5-6 checkpoints store only `.X` (counts layer deleted after step 4)
- Combined with gzip compression, this reduces storage for steps 5-6 checkpoints

After Step 7, the pseudobulk AnnData is a separate object with only aggregated counts in `.X` (no layers needed). Steps 8-11 use pickle/parquet files, not h5ad.

**Selective checkpointing:**
- Added `checkpoint_steps` parameter to `run_stateless_workflow()` (default: `{2, 3, 5, 8, 9, 10, 11}`)
- Only specified steps save checkpoints; other steps run without saving
- Step 3 is always required (provides raw counts for pseudobulking)
- Steps 8-11 included by default as they produce small pickle/parquet files
- Added `skip_save` parameter to `run_with_checkpoint()` and `run_with_checkpoint_multi()`
