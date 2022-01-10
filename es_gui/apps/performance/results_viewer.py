from __future__ import absolute_import

import os
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sb

from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

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
        
        self.rv.data = self.manager.handler.get_solved_sims()
        self.variables = ['Energy','Hourly Power']
        
        self._update_toolbar()        

    def _update_toolbar(self, *args):
        """Updates the data viewing toolbar based on selections."""
        super(PerformanceResultsViewer, self)._update_toolbar(self)

        self.vars_button.values = self.variables

    def draw_figure(self, *args):
        self._update_selection()

        if not self._validate_inputs():
            return

        start_time, end_time = self.time_selector.get_inputs()
        plot_type = self.vars_button.text

        results = self.dfs

        if plot_type in ['total bill', 'total savings',]:
            self._reinit_graph(has_legend=False)
        else:
            self._reinit_graph(has_legend=True)

        fig = self.current_fig
        ax = self.current_ax
        ax.clear()

        plt.xticks(rotation=0)
        plt.grid(True)
        
        results_ls = [results[key] for key in results]
        resultsF = pd.concat(results_ls,axis=0,ignore_index=True)
        resultsF[['Discharge Power','Charge Power']] *= 1000 #convert to kW
        resultsF['Facility Total HVAC Electricity Demand Rate'] /= 1000 #convert to kW
        resultsF['Discharge Energy'] = resultsF['Discharge Power']*0.25#convert to kWh
        resultsF['Charge Energy'] = resultsF['Charge Power']*0.25#convert to KWh
        resultsF['HVAC Energy'] = resultsF['Facility Total HVAC Electricity Demand Rate']*0.25#convert to kWh
        resultsF['Load Percent'] = 100*resultsF['Discharge Energy'].sum()/resultsF['Charge Energy'].sum()
        resultsF['HVAC Percent'] = 100*resultsF['HVAC Energy'].sum()/resultsF['Charge Energy'].sum()
        monthlyF = resultsF.groupby('Month')
        groupedF = resultsF.groupby(['Month','Day','Hour']).mean()
            
        if plot_type == 'Energy':
            monthlyF[['Discharge Energy','Charge Energy','HVAC Energy']].sum().plot(kind='bar',ax=ax,legend=True,rot=0)
            ax.set_title('Energy Consumption')
            ax.set_ylabel('kWh')
        elif plot_type == 'Hourly Power':
            groupedF = groupedF.unstack(level=[0])
            days = groupedF.index.get_level_values('Day').unique().to_list()
            max_hours = len(groupedF.index)
            groupedF['Facility Total HVAC Electricity Demand Rate'].plot(kind='line',ax=ax,legend=True,rot=0,colormap='tab20')
            ax.set_xticks(np.linspace(0,max_hours,len(days),endpoint=False))
            ax.set_xticklabels(days)
            ax.set_ylabel('kW')
            ax.set_xlabel('Day of Month')
            ax.set_title('Hourly HVAC Power Consumption')
        elif plot_type == 'Efficiency':
            groupedF = groupedF.unstack(level=[0])
            days = groupedF.index.get_level_values('Day').unique().to_list()
            max_hours = len(groupedF.index)
            (groupedF['Discharge Energy']/(groupedF['Charge Energy']+groupedF['HVAC Energy'])).plot(kind='line',ax=ax,legend=True,rot=0,colormap='tab20')
            ax.set_xticks(np.linspace(0,max_hours,len(days),endpoint=False))
            ax.set_xticklabels(days)
#            ax.set_ylabel('kW')
            ax.set_xlabel('Day of Month')
            ax.set_title('Efficiency')
#        elif plot_type == 'Bill':
#            for key in results:
#                resultsF = results[key]

        self.plotbox.children[0].draw()
        
    def _update_selection(self):
        """Updates the dict. of DataFrames whenever new selections of data are made."""

        # Identify the selected run(s) from RunSelector.
        rv = self.rv
        runs_selected = [rv.data[selected_ix] for selected_ix in rv.layout_manager.selected_nodes]

        results = {}

        for run in runs_selected:
            label = run['name']
            df = run['results']
#            print(run)

            results[label] = df

        self.dfs = results
        
        self._update_toolbar()

    def export_png(self):
        """Exports currently displayed figure to .png file in specified location."""
        outdir_root = os.path.join('results', 'btm', 'plots')

        super(PerformanceResultsViewer, self).export_png(outdir_root)

    def export_csv(self):
        """Exports selected DataFrames to .csv files in specified location."""
        outdir_root = os.path.join('results', 'btm', 'csv')

        super(PerformanceResultsViewer, self).export_csv(outdir_root)
