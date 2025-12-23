# Simple Correlation Workflow using Make
#
# This Makefile demonstrates a simple data analysis pipeline using Make.
# Each target represents a step in the workflow, with dependencies ensuring
# correct execution order.
#
# Usage:
#   make OUTPUT_DIR=/path/to/output all
#   make OUTPUT_DIR=/path/to/output clean
#   make OUTPUT_DIR=/path/to/output help

# Configuration
OUTPUT_DIR ?= ./output
DATA_DIR := $(OUTPUT_DIR)/data
RESULTS_DIR := $(OUTPUT_DIR)/results
FIGURES_DIR := $(OUTPUT_DIR)/figures
LOGS_DIR := $(OUTPUT_DIR)/logs

# Data URLs
MV_URL := https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/meaningful_variables_clean.csv
DEMO_URL := https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv

# Python command
PYTHON := python

# Default target
.PHONY: all
all: $(FIGURES_DIR)/correlation_heatmap.png

# Help target
.PHONY: help
help:
	@echo "Simple Correlation Workflow"
	@echo ""
	@echo "Usage: make OUTPUT_DIR=/path/to/output <target>"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Run full workflow (default)"
	@echo "  clean    - Remove all generated files"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Individual steps:"
	@echo "  download_mv    - Download meaningful variables data"
	@echo "  download_demo  - Download demographics data"
	@echo "  filter_mv      - Filter meaningful variables to numerical"
	@echo "  filter_demo    - Filter demographics to numerical"
	@echo "  join           - Join the two datasets"
	@echo "  correlation    - Compute correlation matrix"
	@echo "  heatmap        - Generate clustered heatmap"

# Create directories
$(DATA_DIR) $(RESULTS_DIR) $(FIGURES_DIR) $(LOGS_DIR):
	mkdir -p $@

# Step 1a: Download meaningful variables
.PHONY: download_mv
download_mv: $(DATA_DIR)/meaningful_variables.csv

$(DATA_DIR)/meaningful_variables.csv: | $(DATA_DIR) $(LOGS_DIR)
	$(PYTHON) scripts/download_data.py "$(MV_URL)" "$@" > $(LOGS_DIR)/download_mv.log 2>&1

# Step 1b: Download demographics
.PHONY: download_demo
download_demo: $(DATA_DIR)/demographics.csv

$(DATA_DIR)/demographics.csv: | $(DATA_DIR) $(LOGS_DIR)
	$(PYTHON) scripts/download_data.py "$(DEMO_URL)" "$@" > $(LOGS_DIR)/download_demo.log 2>&1

# Step 2a: Filter meaningful variables
.PHONY: filter_mv
filter_mv: $(DATA_DIR)/meaningful_variables_numerical.csv

$(DATA_DIR)/meaningful_variables_numerical.csv: $(DATA_DIR)/meaningful_variables.csv | $(LOGS_DIR)
	$(PYTHON) scripts/filter_data.py "$<" "$@" > $(LOGS_DIR)/filter_mv.log 2>&1

# Step 2b: Filter demographics
.PHONY: filter_demo
filter_demo: $(DATA_DIR)/demographics_numerical.csv

$(DATA_DIR)/demographics_numerical.csv: $(DATA_DIR)/demographics.csv | $(LOGS_DIR)
	$(PYTHON) scripts/filter_data.py "$<" "$@" > $(LOGS_DIR)/filter_demo.log 2>&1

# Step 3: Join datasets
.PHONY: join
join: $(DATA_DIR)/joined_data.csv

$(DATA_DIR)/joined_data.csv: $(DATA_DIR)/meaningful_variables_numerical.csv $(DATA_DIR)/demographics_numerical.csv | $(LOGS_DIR)
	$(PYTHON) scripts/join_data.py "$<" "$(word 2,$^)" "$@" > $(LOGS_DIR)/join.log 2>&1

# Step 4: Compute correlation
.PHONY: correlation
correlation: $(RESULTS_DIR)/correlation_matrix.csv

$(RESULTS_DIR)/correlation_matrix.csv: $(DATA_DIR)/joined_data.csv | $(RESULTS_DIR) $(LOGS_DIR)
	$(PYTHON) scripts/compute_correlation.py "$<" "$@" > $(LOGS_DIR)/correlation.log 2>&1

# Step 5: Generate heatmap
.PHONY: heatmap
heatmap: $(FIGURES_DIR)/correlation_heatmap.png

$(FIGURES_DIR)/correlation_heatmap.png: $(RESULTS_DIR)/correlation_matrix.csv | $(FIGURES_DIR) $(LOGS_DIR)
	$(PYTHON) scripts/generate_heatmap.py "$<" "$@" > $(LOGS_DIR)/heatmap.log 2>&1

# Clean target
.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)
