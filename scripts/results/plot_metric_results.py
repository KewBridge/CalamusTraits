import argparse
import plotnine as p9
import pandas as pd

# Plot the mean F1 scores with error bars
def plot_bert_score_subject(bert_df):
    # Compute error bar limits as new columns
    bert_df = bert_df.copy()
    bert_df['f1_ymin'] = bert_df['f1_mean'] - bert_df['f1_sem']
    bert_df['f1_ymax'] = bert_df['f1_mean'] + bert_df['f1_sem']

    # plot the means and std for each subject, with improved aesthetics for posters
    nlp_fig = (
        p9.ggplot(bert_df, p9.aes(x='subject', y='f1_mean')) +
        p9.geom_bar(stat='identity', position='dodge', width=0.7, fill = "#008080") +
        p9.geom_errorbar(
            p9.aes(ymin='f1_ymin', ymax='f1_ymax'),
            width=0.15,
            position=p9.position_dodge(width=0.7),
            color='black'
        ) +
        p9.theme_bw(base_size=22) +  # Larger base font size for readability
        p9.labs(
            x='Subject',
            y='Mean BERT Score',
            fill='BERT Metric',
        ) +
        p9.theme(
            axis_text_x=p9.element_text(angle=30, hjust=1, size=18, weight='bold'),
            axis_text_y=p9.element_text(size=18, weight='bold'),
            axis_title_x=p9.element_text(size=22, weight='bold'),
            axis_title_y=p9.element_text(size=22, weight='bold'),
            legend_title=p9.element_text(size=20, weight='bold'),
            legend_text=p9.element_text(size=18),
            plot_title=p9.element_text(size=26, weight='bold', ha='center'),
            figure_size=(16, 8),
            panel_grid_major=p9.element_line(size=0.5, color="#cccccc"),
            panel_grid_minor=p9.element_blank()
        )
    )
    return nlp_fig


def plot_rouge_score_subject(rouge_df):
    # plot the means and std for each subject, with improved aesthetics for posters
    nlp_fig = (
        p9.ggplot(rouge_df, p9.aes(x='subject', y='mean', fill='rouge_type')) +
        p9.geom_bar(stat='identity', position='dodge', width=0.7, color='black') +
        p9.geom_errorbar(
            p9.aes(ymin='mean - sem', ymax='mean + sem'),
            width=0.15,
            position=p9.position_dodge(width=0.7),
            color='black'
        ) +
        p9.theme_bw(base_size=22) +  # Larger base font size for readability
        p9.labs(
            x='Subject',
            y='ROUGE Score',
            fill='ROUGE Metric',
        ) +
        p9.theme(
            axis_text_x=p9.element_text(angle=30, hjust=1, size=18, weight='bold'),
            axis_text_y=p9.element_text(size=18, weight='bold'),
            axis_title_x=p9.element_text(size=22, weight='bold'),
            axis_title_y=p9.element_text(size=22, weight='bold'),
            legend_title=p9.element_text(size=20, weight='bold'),
            legend_text=p9.element_text(size=18),
            plot_title=p9.element_text(size=26, weight='bold', ha='center'),
            figure_size=(16, 8),
            panel_grid_major=p9.element_line(size=0.5, color="#cccccc"),
            panel_grid_minor=p9.element_blank()
        ) +
        p9.scale_fill_manual(values=["#6A5ACD", "#4D4D4D", "#008080"])
    )
    return nlp_fig


def plot_bert_score_group(bert_df):
    nlp_fig = (
        p9.ggplot(bert_df, p9.aes(x='group', y='f1_mean', fill='group')) +
        p9.geom_bar(stat='identity', position='dodge') +
        p9.geom_errorbar(p9.aes(ymin='f1_mean - f1_sem', ymax='f1_mean + f1_sem'), width=0.2, position=p9.position_dodge(width=0.9)) +
        p9.theme_bw() +
        p9.labs(x='Group', y='f1 BERTScore') +
        p9.theme(axis_text_x=p9.element_text(angle=45, hjust=1)) +
        p9.scale_fill_manual(values=["#6A5ACD", "#4D4D4D", "#008080"])
    )
    return nlp_fig


def plot_rouge_score_group(rouge_df):
    # Plot the means and SEM for each rouge_type
    nlp_fig = (
        p9.ggplot(rouge_df, p9.aes(x='group', y='mean', fill='rouge_type')) +
        p9.geom_bar(stat='identity', position='dodge') +
        p9.geom_errorbar(p9.aes(ymin='mean - sem', ymax='mean + sem'), width=0.2, position=p9.position_dodge(width=0.9)) +
        p9.theme_bw() +
        p9.labs(x='Group', y='ROUGE Score', fill='ROUGE metric') +
        p9.theme(axis_text_x=p9.element_text(angle=45, hjust=1)) +
        p9.scale_fill_manual(values=["#6A5ACD", "#4D4D4D", "#008080"])
    )
    return nlp_fig


def main():
    parser = argparse.ArgumentParser(description="Plot BERT and ROUGE scores")
    parser.add_argument('input_file_scores', help='Input CSV file with metric scores')
    parser.add_argument('output_file_plot', help='Output plot file (e.g., plot.png)')
    parser.add_argument('--metric', choices=['rouge', 'bert'])
    parser.add_argument('--level', choices=['subject', 'group'], help='Level at which to plot results')
    args = parser.parse_args()

    if args.metric == 'bert' and args.level == 'subject':
        plot_bert_score_subject(pd.read_csv(args.input_file_scores)).save(args.output_file_plot, dpi=300)

    if args.metric == 'rouge' and args.level == 'subject':
        plot_rouge_score_subject(pd.read_csv(args.input_file_scores)).save(args.output_file_plot, dpi=300)

    if args.metric == 'bert' and args.level == 'group':
        plot_bert_score_group(pd.read_csv(args.input_file_scores)).save(args.output_file_plot, dpi=300)

    if args.metric == 'rouge' and args.level == 'group':
        plot_rouge_score_group(pd.read_csv(args.input_file_scores)).save(args.output_file_plot, dpi=300)


if __name__ == "__main__":
    main()