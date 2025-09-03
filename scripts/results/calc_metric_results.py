import argparse
import pandas as pd
from evaluate import load
import re
import string


def normalize_text(text):
    # Lowercase
    text = text.lower()
    # Replace semicolons and other punctuation with space (not just remove — to avoid word merging)
    text = re.sub(rf"[{re.escape(string.punctuation)}]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Function to retrieve rouge scores for each subject in each taxon_name
def compute_bert_for_files(sentences_file, llm_descriptions_file, bertscore):
    sentences_df = pd.read_csv(sentences_file)
    llm_descriptions_df = pd.read_csv(llm_descriptions_file)
    output_list = []

    unique_taxon_names = sentences_df['taxon_name'].unique()
    for taxon_name in unique_taxon_names:
        taxon_sentences = sentences_df[sentences_df['taxon_name'] == taxon_name]
        taxon_llm_descriptions = llm_descriptions_df[llm_descriptions_df['taxon_name'] == taxon_name]

        grouped_taxon_sentences = taxon_sentences.groupby('subject_gen')
        grouped_taxon_llm_descriptions = taxon_llm_descriptions.groupby('subject')

        for subject, subject_sentences in grouped_taxon_sentences:
            if subject in grouped_taxon_llm_descriptions.groups:
                subject_llm_descriptions = grouped_taxon_llm_descriptions.get_group(subject)

                for _, row in subject_llm_descriptions.iterrows():
                    reference_text = ' '.join(subject_sentences['sentence'].tolist())
                    normalized_prediction = normalize_text(row['species_description'])
                    normalized_reference = normalize_text(reference_text)
                    bert_score = bertscore.compute(
                        predictions=[normalized_prediction],
                        references=[normalized_reference],
                        lang = "en"
                    )
                    print(bert_score)
                    loop_dict = {
                        'taxon_name': taxon_name,
                        'subject': subject,
                        'llm_description': row['species_description'],
                        'reference_text': reference_text,
                        'precision': bert_score['precision'],
                        'recall': bert_score['recall'],
                        'f1': bert_score['f1']
                    }
                    output_list.append(loop_dict)
    return pd.DataFrame(output_list)


def process_bert_scores(df):
    # Remove 'llm_description' and 'reference_text' columns
    df = df.drop(columns=['llm_description', 'reference_text', 'precision', 'recall'])
    
    # Remove square brackets from 'f1' column and convert to float, coercing errors to NaN
    df['f1'] = pd.to_numeric(df['f1'].astype(str).str.strip('[]'), errors='coerce')

    # Drop rows where 'f1' could not be converted to a number
    df = df.dropna(subset=['f1'])

    # Group by 'group', then calculate mean and SEM for each group
    grouped_df = df.groupby('subject').agg({'f1': ['mean', 'sem']}).reset_index()

    # Flatten MultiIndex columns
    grouped_df.columns = ['subject', 'f1_mean', 'f1_sem']

    return grouped_df


output_list = []

def bert_full_description_level(cerat_mono, daem_mono, extra_mono, cerat_llm, daem_llm, extra_llm, bertscore):
    cerat_mono = pd.read_csv(cerat_mono)
    daem_mono = pd.read_csv(daem_mono)
    extra_mono = pd.read_csv(extra_mono)
    cerat_llm = pd.read_csv(cerat_llm)
    daem_llm = pd.read_csv(daem_llm)
    extra_llm = pd.read_csv(extra_llm)

    cerat_mono['group'] = 'ceratolobus'
    daem_mono['group'] = 'daemonorops'
    extra_mono['group'] = 'extras'
    cerat_llm['group'] = 'ceratolobus'
    daem_llm['group'] = 'daemonorops'
    extra_llm['group'] = 'extras'    
    all_df_llm = pd.concat([cerat_llm, daem_llm, extra_llm], ignore_index=True)
    all_df_mono = pd.concat([cerat_mono, daem_mono, extra_mono], ignore_index=True).rename(columns={'line_cleaned': 'species_description'})
    
    for taxon_name in all_df_llm['taxon_name'].unique():
        taxon_llm = all_df_llm[all_df_llm['taxon_name'] == taxon_name]
        taxon_mono = all_df_mono[all_df_mono['taxon_name'] == taxon_name]

        for _, row in taxon_llm.iterrows():
            reference_text = ' '.join(taxon_mono['species_description'].tolist())
            bert_score = bertscore.compute(
                            predictions=[row['species_description']],
                            references=[reference_text],
                            lang = "en"
                        )
            print(bert_score)
            loop_dict = {
                'group': row['group'],
                'taxon_name': taxon_name,
                'llm_description': row['species_description'],
                'reference_text': reference_text,
                'f1': bert_score['f1']
            }
            output_list.append(loop_dict)
    description_level_bert = pd.DataFrame(output_list)
    return description_level_bert


def process_description_level_bert(df):
    # Remove 'llm_description' and 'reference_text' columns
    df = df.drop(columns=['taxon_name', 'llm_description', 'reference_text'])

    # Remove square brackets from 'f1' column and convert to float, coercing errors to NaN
    df['f1'] = pd.to_numeric(df['f1'].astype(str).str.strip('[]'), errors='coerce')

    # Drop rows where 'f1' could not be converted to a number
    df = df.dropna(subset=['f1'])

    # Group by 'group', then calculate mean and SEM for each group
    grouped_df = df.groupby('group').agg({'f1': ['mean', 'sem']}).reset_index()

    # Flatten MultiIndex columns
    grouped_df.columns = ['group', 'f1_mean', 'f1_sem']

    return grouped_df


# Function to retrieve rouge scores for each subject in each taxon_name
def compute_rouge_for_files(sentences_file, llm_descriptions_file, rouge):
    sentences_df = pd.read_csv(sentences_file)
    llm_descriptions_df = pd.read_csv(llm_descriptions_file)
    output_list = []

    for taxon_name in sentences_df['taxon_name'].unique():
        taxon_sentences = sentences_df[sentences_df['taxon_name'] == taxon_name]
        taxon_llm_descriptions = llm_descriptions_df[llm_descriptions_df['taxon_name'] == taxon_name]

        grouped_taxon_sentences = taxon_sentences.groupby('subject_gen')
        grouped_taxon_llm_descriptions = taxon_llm_descriptions.groupby('subject')

        for subject, subject_sentences in grouped_taxon_sentences:
            if subject in grouped_taxon_llm_descriptions.groups:
                subject_llm_descriptions = grouped_taxon_llm_descriptions.get_group(subject)

                for _, row in subject_llm_descriptions.iterrows():
                    reference_text = ' '.join(subject_sentences['sentence'].tolist())
                    rouge_score = rouge.compute(
                        predictions=[row['species_description']],
                        references=[reference_text],
                        use_stemmer=False
                    )
                    loop_dict = {
                        'taxon_name': taxon_name,
                        'subject': subject,
                        'llm_description': row['species_description'],
                        'reference_text': reference_text,
                        'rouge1': rouge_score['rouge1'],
                        'rouge2': rouge_score['rouge2'],
                        'rougeL': rouge_score['rougeL'],
                        'rougeLsum': rouge_score['rougeLsum'],
                    }
                    output_list.append(loop_dict)
    return pd.DataFrame(output_list)


# remove llm_description and reference_text columns
def process_rouge_scores(df):
    df = df.drop(columns=['llm_description', 'reference_text'])
    df = df.groupby('subject').agg(
        {
            'rouge1': ['mean', 'sem'],
            'rouge2': ['mean', 'sem'],
            'rougeL': ['mean', 'sem'],
        }
    ).reset_index()
    df.columns = ['subject', 'rouge1_mean', 'rouge1_sem', 'rouge2_mean', 'rouge2_sem', 'rougeL_mean', 'rougeL_sem']
    df = df.melt(id_vars='subject', 
                 value_vars=['rouge1_mean', 'rouge1_sem', 'rouge2_mean', 'rouge2_sem', 'rougeL_mean', 'rougeL_sem'],
                 var_name='metric', value_name='value')
    df[['rouge_type', 'stat']] = df['metric'].str.extract(r'(rouge\w+)_(mean|sem)')
    df = df.pivot_table(index=['subject', 'rouge_type'], columns='stat', values='value').reset_index()
    return df


# Function to compute rouge scores for full descriptions at the level of taxon_name
def rouge_full_description_level(cerat_mono, daem_mono, extra_mono, cerat_llm, daem_llm, extra_llm, rouge):
    cerat_mono = pd.read_csv(cerat_mono)
    daem_mono = pd.read_csv(daem_mono)
    extra_mono = pd.read_csv(extra_mono)
    cerat_llm = pd.read_csv(cerat_llm)
    daem_llm = pd.read_csv(daem_llm)
    extra_llm = pd.read_csv(extra_llm)

    cerat_llm['group'] = 'ceratolobus'
    daem_llm['group'] = 'daemonorops'
    extra_llm['group'] = 'extras'
    cerat_mono['group'] = 'ceratolobus'
    daem_mono['group'] = 'daemonorops'
    extra_mono['group'] = 'extras'
    all_df_llm = pd.concat([cerat_llm, daem_llm, extra_llm], ignore_index=True)
    all_df_mono = pd.concat([cerat_mono, daem_mono, extra_mono], ignore_index=True).rename(columns={'line_cleaned': 'species_description'})

    for taxon_name in all_df_llm['taxon_name'].unique():
        taxon_llm = all_df_llm[all_df_llm['taxon_name'] == taxon_name]
        taxon_mono = all_df_mono[all_df_mono['taxon_name'] == taxon_name]

        for _, row in taxon_llm.iterrows():
            reference_text = ' '.join(taxon_mono['species_description'].tolist())
            rouge_score = rouge.compute(
                predictions=[row['species_description']],
                references=[reference_text],
            )
            loop_dict = {
                'group': row['group'],
                'taxon_name': taxon_name,
                'llm_description': row['species_description'],
                'reference_text': reference_text,
                'rouge1': rouge_score['rouge1'],
                'rouge2': rouge_score['rouge2'],
                'rougeL': rouge_score['rougeL'],
            }
            output_list.append(loop_dict)
    description_level_rouge = pd.DataFrame(output_list)
    print(description_level_rouge)
    return description_level_rouge


def process_description_level_rouge(df):
    df = df.drop(columns=['llm_description', 'reference_text'])
    # Tidy the dataframe
    df = df.melt(id_vars='group',
                 value_vars=['rouge1', 'rouge2', 'rougeL'],
                 var_name='rouge_type', value_name='value')
    # Calculate the mean and SEM for each rouge_type
    df = df.groupby(['group', 'rouge_type']).agg(
        mean=('value', 'mean'),
        sem=('value', 'sem')
    ).reset_index()
    print(df)
    return df


def main():
        # Set up argument parser
    parser = argparse.ArgumentParser(description="Calculate ROUGE and BERT scores ready for plotting")
    parser.add_argument('cerat_mono', help='Ceratolobus monograph sentences/treatments CSV file')
    parser.add_argument('daem_mono', help='Daemonorops monograph sentences/treatments CSV file')
    parser.add_argument('extra_mono', help='Extra monograph sentences/treatments CSV file')
    parser.add_argument('cerat_llm', help='Ceratolobus LLM sentences/treatments CSV file')
    parser.add_argument('daem_llm', help='Daemonorops LLM sentences/treatments CSV file')
    parser.add_argument('extra_llm', help='Extra LLM sentences/treatments CSV file')
    parser.add_argument('output', default='metric_results.csv', help='Output CSV file for metric results')
    parser.add_argument('--metric', choices=['rouge', 'bert'])
    parser.add_argument('--level', choices=['subject', 'group'], help='Level at which to calculate results')
    args = parser.parse_args()

    if args.metric == 'bert' and args.level == 'subject':
        print("Calculating BERT scores by subject...")
        bertscore = load("bertscore")
        df_ceratolobus = compute_bert_for_files(args.cerat_mono, args.cerat_llm, bertscore)
        df_daemonorops = compute_bert_for_files(args.daem_mono, args.daem_llm, bertscore)
        df_extra = compute_bert_for_files(args.extra_mono, args.extra_llm, bertscore)
        all_df = pd.concat([df_ceratolobus, df_daemonorops, df_extra], ignore_index=True)
        all_df = process_bert_scores(all_df)
        all_df.to_csv(args.output, index=False)
        print(f"BERT scores saved to {args.output}")

    if args.metric == 'rouge' and args.level == 'subject':
        print("Calculating ROUGE scores by subject...")
        rouge = load("rouge")
        df_ceratolobus = compute_rouge_for_files(args.cerat_mono, args.cerat_llm, rouge)
        df_daemonorops = compute_rouge_for_files(args.daem_mono, args.daem_llm, rouge)
        df_extra = compute_rouge_for_files(args.extra_mono, args.extra_llm, rouge)
        all_df = pd.concat([df_ceratolobus, df_daemonorops, df_extra], ignore_index=True)
        all_df = process_rouge_scores(all_df)
        all_df.to_csv(args.output, index=False)
        print(f"ROUGE scores saved to {args.output}")

    if args.metric == 'bert' and args.level == 'group':
        print("Calculating BERT scores by group...")
        bertscore = load("bertscore")
        description_level_bert = bert_full_description_level(
            args.cerat_mono, args.daem_mono, args.extra_mono,
            args.cerat_llm, args.daem_llm, args.extra_llm,
            bertscore
        )
        description_level_bert = process_description_level_bert(description_level_bert)
        description_level_bert.to_csv(args.output, index=False)
        print(f"BERT group-level scores saved to {args.output}")

    
    if args.metric == 'rouge' and args.level == 'group':
        print("Calculating ROUGE scores by group...")
        rouge = load("rouge")
        description_level_rouge = rouge_full_description_level(
            args.cerat_mono, args.daem_mono, args.extra_mono,
            args.cerat_llm, args.daem_llm, args.extra_llm,
            rouge
        )
        description_level_rouge = process_description_level_rouge(description_level_rouge)
        description_level_rouge.to_csv(args.output, index=False)
        print(f"ROUGE group-level scores saved to {args.output}")


if __name__ == "__main__":
    main()    