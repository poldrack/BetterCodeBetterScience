### Data for examples

#### Data management

The database example requires downloading genome-wide association study (GWAS) data from https://www.ebi.ac.uk/gwas/docs/file-downloads.  The dataset can be downloaded and renamed the proper name using the following commands, starting from the project root directory:

```bash
cd data
wget https://www.ebi.ac.uk/gwas/api/search/downloads/associations/v1.0.2\?split\=false -O gwas_catalog_v1.0.2-associations.zip
mkdir gwas
cd gwas
unzip ../gwas_catalog_v1.0.2-associations.zip
```

According to the EBI site, the GWAS Catalog data is currently mapped to Genome Assembly GRCh38.p14 and dbSNP Build 156.





