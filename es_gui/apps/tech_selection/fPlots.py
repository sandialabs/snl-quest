import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

color_red, color_blue = np.array([247, 140, 102])/255, np.array([102, 163, 224])/255
cBlue = np.array([0, 102, 204])/255
cAmber = np.array([255, 136, 0])/255
cGreen = np.array([108, 179, 18])/255
cOrange = np.array([242, 63, 0])/255
cBlueGrey = np.array([125, 142, 160])/255

plt.style.use(os.path.join('es_gui', 'apps', 'tech_selection', 'mpl_style_presentations.mplstyle'))


def plot_table_feasibility(df_data, figsize=(7, 5),
                           cmap=[color_red, color_blue],
                           xlabel=None, ylabel=None, xticklabels=[], yticklabels=[],
                           update_individual_xticklabel=None):
    """"Display feasibility tables as heatmap plots."""
    
    plt.style.use(os.path.join('es_gui', 'apps', 'tech_selection', 'mpl_style_presentations.mplstyle'))

    # Default labels for the x and y ticklabels, if none are given
    if len(xticklabels) == 0: xticklabels = df_data.columns
    if len(yticklabels) == 0: yticklabels = df_data.index

    # Create feasibility table (as a heatmap plot)
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(df_data, cmap=cmap, cbar=False, linewidths=0.1,
                annot=df_data.applymap(lambda x: 'Yes' if x == 1 else 'No'),
                fmt='s', annot_kws={'fontsize': 2, 'fontfamily': 'sans-serif', 'va': 'center_baseline'},
                xticklabels=xticklabels, yticklabels=yticklabels, ax=ax)
    ax.tick_params(rotation=0)

    # Update settings for x and y labels
    ax.set_xlabel(xlabel, fontsize=12, weight='bold')
    ax.set_ylabel(ylabel, fontsize=12, weight='bold')

    # Update settings for ticks and their labels
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.tick_params(bottom=False, top=False, left=False, right=False)

    # Update settings for individual x ticklabels
    if update_individual_xticklabel is not None:
        for xtick_idx, xtick_props in update_individual_xticklabel.items():
            ax.get_xticklabels()[xtick_idx].update(xtick_props)
            
    # Return figure handle
    return fig


def plot_ranking_techs(df_data):
    fig, axs = plt.subplots(ncols=5, sharey=True, figsize=(1.9, 1))
    for column, color, ax in zip(['Application score', 'Location score', 'Cost score', 'Maturity score', 'Total score'],
                                 [cBlue, cAmber, cGreen, cOrange, cBlueGrey], axs):
        df_data[column].plot.barh(ax=ax, fc=color)
        ax.set_xticks([0, 0.5, 1])
        ax.set_xticklabels(['0', '0.5', '1'])
        ax.set_xlim(0, 1)
        ax.set_ylabel('')
        ax.set_title(column.replace(' score', ''))

    return fig