import calendar
import os
import random

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
import pandas as pd

from es_gui.tools.valuation.valuation_optimizer import ValuationOptimizer
from es_gui.tools.valuation.valuation_dms import ValuationDMS


#sb.set()
sb.set_style('whitegrid')
sb.set_context('paper', font_scale=2.25)


# Matplotlib plot appearance settings.
## See: https://matplotlib.org/users/customizing.html

# path = os.path.join('es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Regular.ttf')
# prop = mpl.font_manager.FontProperties(fname=path)
# mpl.rcParams['font.family'] = prop.get_name()

#plt.style.use('ggplot')

font = {'family' : 'sans-serif',
        'weight' : 'regular',
        'size'   : 18
        }
mpl.rc('font', **font)

# params = {
#     # 'text.usetex': True,  # Use latex for all text handling.
#     'axes.spines.top': False,  # Remove the top and right spines.
#     'axes.spines.right': False,
#     'axes.titlesize': 22,
#     'axes.titlepad': 8.0,
#     'axes.labelsize': 14,
#     'axes.labelpad': 8.0,
#     }
# mpl.rcParams.update(params)

# Color palette for chart objects: foundational + support colors for QuESt.
PALETTE_HEX = [(0, 83, 118), (132, 189, 0),
    (0, 173, 208), (255, 163, 0), (255, 88, 93), (174, 37, 115)]
PALETTE = []

for color_hex in PALETTE_HEX:
    # Convert to [0, 1] scale for rgb values.
    PALETTE.append(tuple([rgb_val/255 for rgb_val in color_hex]))

# Lookup table for decision variables for each model/market type.
## Each dict value is a list of tuples in the format (<decision variable as known by ValuationOptimizer>, <variable name for labels, plots, and dict keys>)
ACTIVITIES = dict()
ACTIVITIES['arbitrage'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'),]
ACTIVITIES['pjm_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]
ACTIVITIES['ercot_arbreg'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_ru', 'regulation up'), ('q_rd', 'regulation down'), ]
ACTIVITIES['spp_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_ru', 'regulation up'), ('q_rd', 'regulation down'), ]
ACTIVITIES['miso_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]
ACTIVITIES['isone_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]

def generate_revenue_bar_chart(chart_data, bar_width=0.6, labels=[]):
    """
    Creates a bar chart for revenue using chart_data.

    chart_data should be a list of (solved) ValuationOptimizer objects.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Get the gross revenue data from the ValOp objects.
    indices = np.arange(len(chart_data))
    revenue_list = [op.gross_revenue*1e-3 for op in chart_data]

    # Plot.
    ax.bar(indices, revenue_list, bar_width, color=PALETTE)
    plt.xticks(indices, labels, rotation=0)
    ax.set_yticklabels(['{:,}'.format(int(x)) for x in ax.get_yticks().tolist()])  # Comma separator for y-axis tick labels.
    # sb.despine(offset=10, trim=True)

    # ax.set_title('Gross Revenue by Month')
    # ax.set_ylabel('Revenue [\$]')  # Note the $ is escaped, assuming LaTeX is used to render text.

    return fig, ax

def generate_revenue_multisetbar_chart(chart_data, bar_width=0.4, labels=[]):
    """
    Creates a multiset bar chart for revenue using chart_data, with sets for arbitrage and regulation revenue.

    chart_data should be a list of (solved) ValuationOptimizer objects.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Get the revenue data from the ValOp objects.
    indices = np.arange(len(chart_data))

    try:
        revenue_arb_list = [float(op.results['rev_arb'].tail(1))*1e-3 for op in chart_data]
        revenue_reg_list = [float(op.results['rev_reg'].tail(1))*1e-3 for op in chart_data]
    except TypeError:
        revenue_arb_list = [0 for op in chart_data]
        revenue_reg_list = [0 for op in chart_data]

    # Plot.
    ax.bar(indices, revenue_arb_list, bar_width, color=PALETTE[0],label='arbitrage')
    ax.bar(indices + bar_width, revenue_reg_list, bar_width, color=PALETTE[1], label='regulation')
    plt.xticks(indices + bar_width/2, labels, rotation=0)
    ax.set_yticklabels(['{:,}'.format(int(x)) for x in ax.get_yticks().tolist()])  # Comma separator for y-axis tick labels.

    # Put legend outside on the right.
    box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='upper right')
    # sb.despine(offset=10, top=True, right=True, trim=True)

    # ax.yaxis.grid(True)
    # ax.set_title('Revenue by Stream')
    # ax.set_ylabel('Revenue [\$]')  # Note the $ is escaped, assuming LaTeX is used to render text.

    return fig, ax

def generate_activity_donut_chart(chart_data, market_type):
    """
    Creates a donut chart for revenue stream activity using chart_data.

    chart_data should be a list of (solved) ValuationOptimizer objects.
    market_type is used to look at the module-level lookup table for determining which decision variables to look for. The lookup tables should be updated as market_type values are implemented.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    activity_list = ACTIVITIES[market_type]  # Uses module-level lookup table.

    ## Determine which colors to use.
    colors_list = PALETTE
    
    ## Compute the activity counts for each activity category.
    donut_data = []
    n_activities = dict()

    for (var, name) in activity_list:
        # Count the number non-zero decision variable values.
        n_activity = sum([len(op.results[var].nonzero()[0]) for op in chart_data])
        n_activities[name] = n_activity

        donut_data.append((name, n_activity))

    # Plot.
    donut_data = sorted(donut_data, key=lambda x: x[1], reverse=True)  # Sort by activity count (descending order).
    data = [activity[-1] for activity in donut_data]

    def _pctfunc(pct):
        """Function to pass to pie() to create wedge percentage labels."""
        THRESHOLD = 5

        if pct < THRESHOLD:
            return_str = ''
        else:
            return_str = "{:.1f}%".format(pct)

        return return_str

    wedges, _, _ = ax.pie(data, radius=1, autopct=lambda pct: _pctfunc(pct), pctdistance=1.2, center=(-1, 0), startangle=90, counterclock=False, colors=colors_list, shadow=False, wedgeprops=dict(width=0.33, linewidth=2, edgecolor='w'), textprops={'fontsize': 14})

    ax.set(aspect="equal", title='Device Activity')
    ax.legend(wedges, [name for (name, activity) in donut_data], loc="center left", bbox_to_anchor=(1.1, 0, 0.5, 1))

    return fig, ax

def generate_activity_stackedbar_chart(chart_data, market_type, bar_width=0.6, labels=[]):
    """
    Creates a stacked bar chart for revenue stream activity using chart_data.

    chart_data should be a list of (solved) ValuationOptimizer objects.
    market_type is used to look at the module-level lookup table for determining which decision variables to look for and which of them constitute frequency regulation activities. The lookup tables should be updated as market_type values are implemented.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Determine which colors to use.
    colors_list = PALETTE

    activity_list = ACTIVITIES[market_type]  # Uses module-level lookup table.

    indices = np.arange(len(chart_data))
    bottom = np.zeros(len(indices))

    ## Compute the total number of actions in each stack for normalization.
    n_month_totals = [float(sum([len(op.results[var].nonzero()[0]) for (var, cat) in activity_list])) for op in chart_data]

    ## Compute the activity counts for each activity category.
    for ix, (var, cat) in enumerate(activity_list, start=0):
        component_color = colors_list[ix]
        n_activity_counts = [sum([len(op.results[var].nonzero()[0])]) for op in chart_data]
        n_activity_counts_norm = []

        for iy, count in enumerate(n_activity_counts, start=0):
            try:
                n_activity_normalized = count/n_month_totals[iy]*100
            except ZeroDivisionError:
                n_activity_normalized = 0
            finally:
                n_activity_counts_norm.append(n_activity_normalized)
        
        # Plot set of bar stack component.
        ax.bar(indices, n_activity_counts_norm, bar_width, bottom=bottom, color=component_color, label=cat)

        # Update "bottom" position for each stack. 
        bottom += n_activity_counts_norm

    plt.xticks(indices, labels, rotation=0)
    sb.despine(offset=10, trim=True)

    # Put legend outside on the right.
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_title('Proportion of Activity by Revenue Stream')
    ax.set_ylabel('%')
    # ax.yaxis.grid(True)

    return fig, ax

def generate_revenue_heatmap(data, map_type='revenue'):
    with sb.axes_style('dark'):
        fig, ax = plt.subplots(figsize=(12, 10))

        if map_type == 'revenue':
            cmap = sb.light_palette(PALETTE[0], as_cmap=True)
            records = pd.DataFrame.from_records(data)
            data_pivoted = records.pivot('power rating', 'energy capacity', 'revenue')
            
            sb.heatmap(data_pivoted, annot=True, fmt='.2f', linewidths=.5, cmap=cmap, ax=ax, cbar_kws={'label': 'Revenue [in millions of $]'})
        elif map_type == 'capx':
            records = pd.DataFrame.from_records(data)
            data_pivoted = records.pivot('power rating', 'energy capacity', 'profit capx ratio')
            
            sb.heatmap(data_pivoted, center=0, annot=True, fmt='.2f', linewidths=.5, ax=ax, cbar_kws={'label': 'Ratio'})
        elif map_type == 'payback':
            cmap = sb.light_palette(PALETTE[0], as_cmap=True)
            records = pd.DataFrame.from_records(data)
            data_pivoted = records.pivot('power rating', 'energy capacity', 'simple payback')
            
            sb.heatmap(data_pivoted, annot=True, fmt='.1f', linewidths=.5, cmap=cmap, ax=ax, cbar_kws={'label': 'Years'})


        # ax.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.1f'))
        # ax.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.1f'))

    return fig, ax

def generate_multisetbar_chart(chart_data, cats=[], labels=[]):
    """
    Creates a multiset bar chart for revenue using chart_data.
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    # Get the revenue data from the ValOp objects.
    indices = np.arange(len(chart_data[0]))
    n_cats = len(chart_data)

    bar_width = 1.0/(n_cats+1)

    # Plot.
    with sb.axes_style('whitegrid'):
        for ix, dataset in enumerate(chart_data, start=0):
            ax.bar(indices + ix*bar_width, chart_data[ix], width=bar_width, color=PALETTE[ix], label=cats[ix])

        plt.xticks(indices + bar_width*(n_cats-1)/2, labels, rotation=0)
        ax.set_yticklabels(['{:,}'.format(int(x)) for x in ax.get_yticks().tolist()])  # Comma separator for y-axis tick labels.

        # Put legend outside on the right.
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # ax.legend(loc='upper right')

    return fig, ax

def generate_bar_chart(chart_data, bottoms=None, bar_width=0.4, labels=[], orientation='vertical'):
    """
    Creates a bar chart for revenue using chart_data.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Get the revenue data from the ValOp objects.
    indices = np.arange(len(chart_data))

    # Plot.
    with sb.axes_style('whitegrid'):
        if bottoms is None:
            if orientation == 'horizontal':
                ax.barh(indices, chart_data, height=bar_width, color=PALETTE)
                plt.yticks(indices, labels, rotation=0)
                ax.set_xticklabels(['{:,}'.format(int(x)) for x in ax.get_xticks().tolist()])  # Comma separator for y-axis tick labels.
            else:
                ax.bar(indices, chart_data, width=bar_width, color=PALETTE)
                plt.xticks(indices, labels, rotation=0)
                ax.set_yticklabels(['{:,}'.format(int(x)) for x in ax.get_yticks().tolist()])  # Comma separator for y-axis tick labels.
        else:
            if orientation == 'horizontal':
                ax.barh(indices, chart_data, left=bottoms, height=bar_width, color=PALETTE)
                plt.yticks(indices, labels, rotation=0)
                ax.set_xticklabels(['{:,}'.format(int(x)) for x in ax.get_xticks().tolist()])  # Comma separator for y-axis tick labels.
                # ax.set_xlim(0, max(chart_data))
            else:
                ax.bar(indices, chart_data, bottom=bottoms, width=bar_width, color=PALETTE)
                plt.xticks(indices, labels, rotation=0)
                ax.set_yticklabels(['{:,}'.format(int(x)) for x in ax.get_yticks().tolist()])  # Comma separator for y-axis tick labels.
                # ax.set_ylim(0, max(chart_data))
            
        # sb.despine(offset=10, trim=True)

    return fig, ax


def generate_revenue_stackedbar_chart(zipped_results, bar_width=0.6, labels=[], orientation='vertical'):
    """
    Creates a stacked bar chart to present revenue results from different estimates.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    zipped_results_list = list(zipped_results)

    # Determine which colors to use.
    colors_list = PALETTE

    n_components = len(zipped_results_list[0])
    indices = np.arange(len(zipped_results_list))
    bottom = np.zeros(len(indices))

    chart_data = []

    for result_set in zipped_results_list:
        sorted_results = np.sort(np.array(result_set))
        sorted_increments = np.diff(sorted_results, prepend=0)

        chart_data.append(sorted_increments)

    for ix in range(n_components):
        component_color = colors_list[ix]
        component_set = [x[ix] for x in chart_data]

        ax.bar(indices, component_set, bar_width, bottom=bottom, color=component_color)
        bottom += component_set

    ax.set_yticklabels(['{:,}'.format(int(x)) for x in ax.get_yticks().tolist()])  # Comma separator for y-axis tick labels.

    plt.xticks(indices, labels, rotation=0)
    # sb.despine(offset=10, trim=True)

    # # ax.yaxis.grid(True)

    return fig, ax