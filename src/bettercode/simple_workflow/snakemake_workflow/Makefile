OUTPUT_DIR := /Users/poldrack/data_unsynced/BCBS/simple_workflow/wf_snakemake

.PHONY: run report graph

clean:
	-rm .snakemake
	-rm -rf $(OUTPUT_DIR)/*

run:
	snakemake --cores 1 --config output_dir=$(OUTPUT_DIR)

lint:
	snakemake --lint --cores 1 --config output_dir=$(OUTPUT_DIR)

dryrun:
	snakemake --dry-run --cores 1 --config output_dir=$(OUTPUT_DIR)

report:
	snakemake --report $(OUTPUT_DIR)/report.html --config output_dir=$(OUTPUT_DIR)

graph:
	snakemake --rulegraph --config output_dir=$(OUTPUT_DIR) --cores 2 | dot -Tpng -Gdpi=300  > output/rulegraph.png

export-env:
	-mkdir envs
	micromamba env export -n bettercode > envs/bettercode.yml
