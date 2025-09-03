# Extract appendices data
data/appendix_1.txt: scripts/monograph_text_extraction/clean_appendix.py resources/appendix_1.txt
	mkdir -p data
	python $^ --quantitative $@

data/appendix_2.txt: scripts/monograph_text_extraction/clean_appendix.py resources/appendix_2.txt
	mkdir -p data
	python $^ $@

appendices: data/appendix_1.txt data/appendix_2.txt

# Extract treatments and sentences for ceratolobus group
data/treatments.txt: scripts/monograph_text_extraction/extract_treatments.py resources/calamus_monograph.pdf resources/ceratolobus_target_species.txt
	mkdir -p data
	python $^ $@

data/sentences.txt: scripts/monograph_text_extraction/extract_treatments.py resources/calamus_monograph.pdf resources/ceratolobus_target_species.txt
	mkdir -p data
	python $^ --sentences $@

treatments: data/treatments.txt

sentences: data/sentences.txt

monograph_data: appendices treatments sentences

# Ceratolobus description generation
ceratolobus_outputs/formatted_supp_data.csv ceratolobus_outputs/supp_data_multi.csv: resources/Ceratolobus.xlsx
	mkdir -p ceratolobus_outputs
	python -m scripts.description_generation.format_supplementary_data $< ceratolobus_outputs/supp_data_multi.csv ceratolobus_outputs/formatted_supp_data.csv

ceratolobus_outputs/app1_descriptions.csv: data/appendix_1.txt ceratolobus_outputs/formatted_supp_data.csv
	mkdir -p ceratolobus_outputs
	python -m scripts.description_generation.app1_descriptions $^ ceratolobus_outputs/app1_descriptions.csv

ceratolobus_outputs/app2_descriptions.csv: data/appendix_2.txt ceratolobus_outputs/formatted_supp_data.csv ceratolobus_outputs/supp_data_multi.csv
	mkdir -p ceratolobus_outputs
	python -m scripts.description_generation.app2_descriptions $^ ceratolobus_outputs/app2_descriptions.csv

# Generates full species descriptions
ceratolobus_outputs/final_combined_descriptions.csv: ceratolobus_outputs/app1_descriptions.csv ceratolobus_outputs/app2_descriptions.csv
	mkdir -p ceratolobus_outputs
	python -m scripts.description_generation.combine_descriptions $^ ceratolobus_outputs/final_combined_descriptions.csv

# Use the subject_sentences option to include the subject of each sentence in the final output
ceratolobus_outputs/subject_descriptions.csv: ceratolobus_outputs/app1_descriptions.csv ceratolobus_outputs/app2_descriptions.csv
	mkdir -p ceratolobus_outputs
	python -m scripts.description_generation.combine_descriptions $^ ceratolobus_outputs/subject_descriptions.csv --subject_sentences

ceratolobus_descriptions: ceratolobus_outputs/final_combined_descriptions.csv

# To extract quantitative data from the monograph
ceratolobus_outputs/quantitative_traits.csv: data/sentences.txt data/appendix_1.txt
	mkdir -p ceratolobus_outputs
	python -m scripts.trait_extraction.app1_extraction $^ ceratolobus_outputs/quantitative_traits.csv

all: data/appendix_1.txt data/appendix_2.txt data/treatments.txt data/sentences.txt ceratolobus_outputs/formatted_supp_data.csv ceratolobus_outputs/supp_data_multi.csv ceratolobus_outputs/app1_descriptions.csv ceratolobus_outputs/app2_descriptions.csv ceratolobus_descriptions ceratolobus_outputs/quantitative_traits.csv

clean:
	rm -rf data ceratolobus_outputs

# I want Ceratolobus to be the default target (make make ceratolobus)
# Daemonorops and extras can be run separately (optionally)
# Make all will run everything

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