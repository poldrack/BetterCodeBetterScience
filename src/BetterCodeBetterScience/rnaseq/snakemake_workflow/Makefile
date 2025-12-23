include ../../../../.env
export

# Generate rule dependency graph
rulegraph:
	snakemake --rulegraph --config datadir=$(DATADIR)/immune_aging/workflow/ --cores 2 | dot -Tpng > rulegraph.png

# Run the full workflow
run:
	snakemake --cores 8 --config datadir=$(DATADIR)/immune_aging/workflow/

# Generate HTML report (run after workflow completes)
report:
	snakemake --report $(DATADIR)/immune_aging/workflow/wf_snakemake/report.html --config datadir=$(DATADIR)/immune_aging/workflow/

# Generate ZIP report (for larger reports with many figures)
report-zip:
	snakemake --report $(DATADIR)/immune_aging/workflow/wf_snakemake/report.zip --config datadir=$(DATADIR)/immune_aging/workflow/

# Dry run - show what would be executed
dry-run:
	snakemake -n --config datadir=$(DATADIR)/immune_aging/workflow/

# Clean all outputs
clean:
	rm -rf $(DATADIR)/immune_aging/workflow/wf_snakemake/

.PHONY: rulegraph run report report-zip dry-run clean
