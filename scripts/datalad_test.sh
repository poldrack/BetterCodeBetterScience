

datalad create -d . my_datalad_repo

datalad download-url -d . -O my_datalad_repo/data/ https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv

datalad download-url -d . -O my_datalad_repo/data/ https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/meaningful_variables_clean.csv

datalad unlock my_datalad_repo/data/demographics.csv

python src/BetterCodeBetterScience/modify_data.py my_datalad_repo/data/demographics.csv

datalad status

datalad save -d . -m "Modified demographics.csv" my_datalad_repo/data/demographics.csv

datalad status
