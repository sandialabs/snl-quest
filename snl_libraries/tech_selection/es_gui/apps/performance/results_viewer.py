from __future__ import absolute_import

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import calendar

from kivy.properties import ObjectProperty

from es_gui.resources.widgets.common import ResultsViewer


class PerformanceResultsViewer(ResultsViewer):
    """The screen for displaying plots inside the application or exporting results."""

    current_fig = ObjectProperty()
    current_ax = ObjectProperty()

    def __init__(self, **kwargs):
        super(PerformanceResultsViewer, self).__init__(**kwargs)

        self.dfs = {}
        self.variables = []

        self.time_selector.start_time.bind(on_text_validate=self.draw_figure)
        self.time_selector.end_time.bind(on_text_validate=self.draw_figure)

    def on_pre_enter(self):
        """Set toolbar."""
        self.rv.data = self.manager.handler.get_solved_sims()
        self.variables = ['Energy', 'Hourly HVAC Power', 'Hourly Battery Power', 'Efficiency']
        self._update_toolbar()

    def _update_toolbar(self, *args):
        """Update the data viewing toolbar based on selections."""
        super(PerformanceResultsViewer, self)._update_toolbar(self)

        self.vars_button.values = self.variables

    def draw_figure(self, *args):
        """Plot figures."""
        self._update_selection()

        if not self._validate_inputs():
            return

        start_time, end_time = self.time_selector.get_inputs()
        plot_type = self.vars_button.text

        results = self.dfs

        if plot_type in ['total bill', 'total savings']:
            self._reinit_graph(has_legend=False)
        else:
            self._reinit_graph(has_legend=True)

        ax = self.current_ax
        ax.clear()

        plt.xticks(rotation=0)
        plt.grid(True)

        # create dataframes for plotting
        results_ls = [results[key] for key in results]
        resultsF = pd.concat(results_ls, axis=0, ignore_index=True)
        resultsF[['Discharge Power', 'Charge Power']] *= 1000                                   # convert to kW
        resultsF['Battery Power'] = resultsF['Charge Power'] - resultsF['Discharge Power']
        resultsF['Facility Total HVAC Electricity Demand Rate'] /= 1000                         # convert to kW
        resultsF['Discharge Energy'] = resultsF['Discharge Power']*0.25                         # convert to kWh
        resultsF['Charge Energy'] = resultsF['Charge Power']*0.25                               # convert to KWh
        resultsF['HVAC Energy'] = resultsF['Facility Total HVAC Electricity Demand Rate']*0.25  # convert to kWh
        resultsF['Load Percent'] = 100*resultsF['Discharge Energy'].sum()/resultsF['Charge Energy'].sum()
        resultsF['HVAC Percent'] = 100*resultsF['HVAC Energy'].sum()/resultsF['Charge Energy'].sum()
        resultsF['Month'] = [calendar.month_abbr[month_num] for month_num in resultsF['Month']]
        resultsF['Month'] = pd.Categorical(resultsF['Month'], categories=[month_abbr for month_abbr in calendar.month_abbr], ordered=True)
        resultsF['Month'] = resultsF['Month'].cat.remove_unused_categories()
        groupedF = resultsF.groupby(['Month', 'Day', 'Hour'])

        energyF = groupedF.sum().reset_index()
        energyF['Hour of Month'] = (energyF['Day']-1)*24 + energyF['Hour']
        energyF = energyF.loc[energyF['Hour of Month'].between(start_time, end_time, 'both')]

        powerF = groupedF.mean().reset_index()
        powerF['Hour of Month'] = (energyF['Day'] - 1)*24 + energyF['Hour']
        powerF = powerF.loc[powerF['Hour of Month'].between(start_time, end_time, 'both')]

        # make plots
        if plot_type == 'Energy':
            ax = energyF.groupby('Month').sum()[['Discharge Energy', 'Charge Energy', 'HVAC Energy']].plot(kind='bar', ax=ax, legend=True, rot=45)
            ax.set_title('Energy Consumption')
            ax.set_ylabel('kWh')
            ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
        elif plot_type == 'Hourly HVAC Power':
            powerF = powerF.groupby(['Month', 'Day', 'Hour']).mean().unstack(level=0)
            days = powerF.index.get_level_values('Day').unique().to_list()
            max_hours = len(powerF.index)
            ax = powerF['Facility Total HVAC Electricity Demand Rate'].plot(kind='line', ax=ax, legend=True, rot=0, colormap='tab20')
            ax.set_xticks(np.linspace(0, max_hours, len(days), endpoint=False))
            ax.set_xticklabels(days)
            ax.set_ylabel('kW')
            ax.set_xlabel('Day of Month')
            ax.set_title('Hourly HVAC Power Consumption')
            ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
        elif plot_type == 'Hourly Battery Power':
            powerF = powerF.groupby(['Month', 'Day', 'Hour']).mean().unstack(level=0)
            days = powerF.index.get_level_values('Day').unique().to_list()
            max_hours = len(powerF.index)
            ax = powerF['Battery Power'].plot(kind='line', ax=ax, legend=True, rot=0, colormap='tab20')
            ax.set_xticks(np.linspace(0, max_hours, len(days), endpoint=False))
            ax.set_xticklabels(days)
            ax.set_ylabel('kW')
            ax.set_xlabel('Day of Month')
            ax.set_title('Hourly Battery Power Consumption')
            ax.legend(bbox_to_anchor=(1, 1), loc='upper left')
        elif plot_type == 'Efficiency':
            efficiencyF = energyF.groupby('Month').sum()
            ax = (efficiencyF['Discharge Energy']*100/(efficiencyF['Charge Energy']+efficiencyF['HVAC Energy'])).plot(kind='bar', ax=ax, legend=False, rot=45)
            ticks = ax.get_yticks()
            ax.set_yticklabels([str(tick) + '%' for tick in ticks])
            ax.set_yticks(ticks)
            ax.set_title('Monthly Efficiency')

            for container in ax.containers:
                labels = [str(round(num, 1)) + '%' for num in container.datavalues]
                ax.bar_label(container, labels=labels)

        self.plotbox.children[0].draw()

    def _update_selection(self):
        """Update the dictionary of DataFrames whenever new selections of data are made."""
        # Identify the selected run(s) from RunSelector.
        rv = self.rv
        runs_selected = [rv.data[selected_ix] for selected_ix in rv.layout_manager.selected_nodes]

        results = {}

        for run in runs_selected:
            label = run['name']
            df = run['results']

            results[label] = df

        self.dfs = results
        self._update_toolbar()

    def export_png(self):
        """Export currently displayed figure to .png file in specified location."""
        outdir_root = os.path.join('results', 'btm', 'plots')

        super(PerformanceResultsViewer, self).export_png(outdir_root)

    def export_csv(self):
        """Export selected DataFrames to .csv files in specified location."""
        outdir_root = os.path.join('results', 'btm', 'csv')

        super(PerformanceResultsViewer, self).export_csv(outdir_root)
