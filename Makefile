# Extract appendices data
data/appendix_1.txt: scripts/monograph_text_extraction/clean_appendix.py resources/appendix_1.txt
	mkdir -p data
	python $^ --quantitative $@

data/appendix_2.txt: scripts/monograph_text_extraction/clean_appendix.py resources/appendix_2.txt
	mkdir -p data
	python $^ $@

appendices: data/appendix_1.txt data/appendix_2.txt

# Extract treatments and sentences for ceratolobus group
data/%_treatments.txt: scripts/monograph_text_extraction/extract_treatments.py resources/calamus_monograph.pdf resources/%_target_species.txt
	mkdir -p data
	python $^ $@

data/%_sentences.txt: scripts/monograph_text_extraction/extract_treatments.py resources/calamus_monograph.pdf resources/%_target_species.txt
	mkdir -p data
	python $^ --sentences $@

treatments: data/treatments.txt

sentences: data/sentences.txt

monograph_data: appendices treatments sentences

# Description generation
ceratolobus_outputs/formatted_supp_data.csv ceratolobus_outputs/supp_data_multi.csv: resources/ceratolobus.xlsx
	mkdir -p ceratolobus_outputs
	python -m scripts.description_generation.format_supplementary_data $< ceratolobus_outputs/supp_data_multi.csv ceratolobus_outputs/formatted_supp_data.csv

daemonorops_outputs/formatted_supp_data.csv daemonorops_outputs/supp_data_multi.csv: resources/daemonorops.xlsx
	mkdir -p daemonorops_outputs
	python -m scripts.description_generation.format_supplementary_data $< daemonorops_outputs/supp_data_multi.csv daemonorops_outputs/formatted_supp_data.csv

extra_outputs/formatted_supp_data.csv extra_outputs/supp_data_multi.csv: resources/extras.xlsx
	mkdir -p extra_outputs
	python -m scripts.description_generation.format_supplementary_data $< extra_outputs/supp_data_multi.csv extra_outputs/formatted_supp_data.csv

%_outputs/app1_descriptions.csv: data/appendix_1.txt %_outputs/formatted_supp_data.csv
	mkdir -p $*_outputs
	python -m scripts.description_generation.app1_descriptions $^ $*_outputs/app1_descriptions.csv

%_outputs/app2_descriptions.csv: data/appendix_2.txt %_outputs/formatted_supp_data.csv %_outputs/supp_data_multi.csv
	mkdir -p $*_outputs
	python -m scripts.description_generation.app2_descriptions $^ $*_outputs/app2_descriptions.csv

# Generates full species descriptions
%_outputs/final_combined_descriptions.csv: %_outputs/app1_descriptions.csv %_outputs/app2_descriptions.csv
	mkdir -p $*_outputs
	python -m scripts.description_generation.combine_descriptions $^ $*_outputs/final_combined_descriptions.csv

# Use the subject_sentences option to include the subject of each sentence in the final output
%_outputs/subject_descriptions.csv: %_outputs/app1_descriptions.csv %_outputs/app2_descriptions.csv
	mkdir -p $*_outputs
	python -m scripts.description_generation.combine_descriptions $^ $*_outputs/subject_descriptions.csv --subject_sentences

ceratolobus_descriptions: ceratolobus_outputs/final_combined_descriptions.csv
daemonorops_descriptions: daemonorops_outputs/final_combined_descriptions.csv
extra_descriptions: extra_outputs/final_combined_descriptions.csv

# To extract quantitative data from the monograph
%_outputs/quantitative_traits.csv: data/%_sentences.txt data/appendix_1.txt
	mkdir -p $*_outputs
	python -m scripts.trait_extraction.app1_extraction $^ $*_outputs/quantitative_traits.csv

clean:
	rm -rf data ceratolobus_outputs daemonorops_outputs extra_outputs

# I want Ceratolobus to be the default target (make make ceratolobus)
# Daemonorops and extras can be run separately (optionally)
# Make all will run everything

APPENDIX_FILES = data/appendix_1.txt data/appendix_2.txt
SENTENCES_FILES = data/ceratolobus_sentences.txt data/daemonorops_sentences.txt data/extra_sentences.txt
TREATMENTS_FILES = data/ceratolobus_treatments.txt data/daemonorops_treatments.txt data/extra_treatments.txt
MONOGRAPH_FILES = $(APPENDIX_FILES) $(SENTENCES_FILES) $(TREATMENTS_FILES)

CERATALOBUS_FILES = ceratolobus_outputs/formatted_supp_data.csv ceratolobus_outputs/supp_data_multi.csv ceratolobus_outputs/app1_descriptions.csv ceratolobus_outputs/app2_descriptions.csv ceratolobus_descriptions ceratolobus_outputs/quantitative_traits.csv 
DAEMONOROPS_FILES = daemonorops_outputs/formatted_supp_data.csv daemonorops_outputs/supp_data_multi.csv daemonorops_outputs/app1_descriptions.csv daemonorops_outputs/app2_descriptions.csv daemonorops_descriptions daemonorops_outputs/quantitative_traits.csv
EXTRA_FILES = extra_outputs/formatted_supp_data.csv extra_outputs/supp_data_multi.csv extra_outputs/app1_descriptions.csv extra_outputs/app2_descriptions.csv extra_descriptions extra_outputs/quantitative_traits.csv

all: $(CERATALOBUS_FILES) $(DAEMONOROPS_FILES) $(EXTRA_FILES)
ceratolobus: $(CERATALOBUS_FILES)
daemonorops: $(DAEMONOROPS_FILES)	
extra: $(EXTRA_FILES)

DESCRIPTION_FILES = ceratolobus_outputs/final_combined_descriptions.csv daemonorops_outputs/final_combined_descriptions.csv extra_outputs/final_combined_descriptions.csv
QUANTITATIVE_FILES = ceratolobus_outputs/quantitative_traits.csv daemonorops_outputs/quantitative_traits.csv extra_outputs/quantitative_traits.csv

metrics_outputs/bert_combined_subject.csv: data/ceratolobus_sentences.txt data/daemonorops_sentences.txt data/extra_sentences.txt trial20-06/cerat_desc_combined.csv trial20-06/daem_desc_combined.csv trial20-06/extra_desc_combined.csv 
	mkdir -p metrics_outputs
	python -m scripts.results.calc_metric_results $^ $@ --metric=bert --level=subject

metrics_outputs/rouge_combined_subject.csv: data/ceratolobus_sentences.txt data/daemonorops_sentences.txt data/extra_sentences.txt trial20-06/cerat_desc_combined.csv trial20-06/daem_desc_combined.csv trial20-06/extra_desc_combined.csv 
	mkdir -p metrics_outputs
	python -m scripts.results.calc_metric_results $^ $@ --metric=rouge --level=subject

metrics_outputs/bert_combined_group.csv: data/ceratolobus_treatments.txt data/daemonorops_treatments.txt data/extra_treatments.txt trial20-06/cerat_desc_combined_treatment.csv trial20-06/daem_desc_combined_treatment.csv trial20-06/extra_desc_combined_treatment.csv 
	mkdir -p metrics_outputs
	python -m scripts.results.calc_metric_results $^ $@ --metric=bert --level=group

metrics_outputs/rouge_combined_group.csv: data/ceratolobus_treatments.txt data/daemonorops_treatments.txt data/extra_treatments.txt trial20-06/cerat_desc_combined_treatment.csv trial20-06/daem_desc_combined_treatment.csv trial20-06/extra_desc_combined_treatment.csv 
	mkdir -p metrics_outputs
	python -m scripts.results.calc_metric_results $^ $@ --metric=rouge --level=group

metrics: metrics_outputs/bert_combined_subject.csv metrics_outputs/rouge_combined_subject.csv metrics_outputs/bert_combined_group.csv metrics_outputs/rouge_combined_group.csv

plots_outputs/bert_plot_subject.png: metrics_outputs/bert_combined_subject.csv
	mkdir -p plots_outputs
	python -m scripts.results.plot_metric_results $^ $@ --metric=bert --level=subject

plots_outputs/rouge_plot_subject.png: metrics_outputs/rouge_combined_subject.csv
	mkdir -p plots_outputs
	python -m scripts.results.plot_metric_results $^ $@ --metric=rouge --level=subject

plots_outputs/bert_plot_group.png: metrics_outputs/bert_combined_group.csv
	mkdir -p plots_outputs
	python -m scripts.results.plot_metric_results $^ $@ --metric=bert --level=group

plots_outputs/rouge_plot_group.png: metrics_outputs/rouge_combined_group.csv
	mkdir -p plots_outputs
	python -m scripts.results.plot_metric_results $^ $@ --metric=rouge --level=group

plots: plots_outputs/bert_plot_subject.png plots_outputs/rouge_plot_subject.png plots_outputs/bert_plot_group.png plots_outputs/rouge_plot_group.png

results: metrics plots