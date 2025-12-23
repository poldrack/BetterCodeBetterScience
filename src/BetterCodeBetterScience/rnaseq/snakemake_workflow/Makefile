include ../../../../.env
export 

rulegraph:
	snakemake --rulegraph --config datadir=$(DATADIR)/immune_aging/workflow/ --cores 2 | dot -Tpng > rulegraph.png
