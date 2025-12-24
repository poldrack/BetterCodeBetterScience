run:
	-rm .snakemake
	snakemake --cores 1 --config output_dir=~/data_unsynced/BCBS/simple_workflow/wf_snakemake

report:
	snakemake --report report.html --config output_dir=~/data_unsynced/BCBS/simple_workflow/wf_snakemake

graph:
	snakemake --rulegraph --config output_dir=./output --cores 2 | dot -Tpng -Gdpi=300  > output/rulegraph.png
