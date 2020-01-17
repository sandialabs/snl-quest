from __future__ import absolute_import

import os
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt

from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

from es_gui.resources.widgets.common import ResultsViewer


class BtmResultsViewer(ResultsViewer):
    """The screen for displaying plots inside the application or exporting results."""
    current_fig = ObjectProperty()
    current_ax = ObjectProperty()

    def __init__(self, **kwargs):
        super(BtmResultsViewer, self).__init__(**kwargs)

        self.dfs = {}

        self.time_selector.start_time.bind(on_text_validate=self.draw_figure)
        self.time_selector.end_time.bind(on_text_validate=self.draw_figure)

    def on_pre_enter(self):
        #Window.bind(on_key_down=self._on_keyboard_down)

        self._update_toolbar()

        # self.rv.data = self.manager.get_screen('btm_home').handler.solved_ops
        self.rv.data = self.manager.get_screen('btm_home').handler.get_solved_ops()

    def _update_toolbar(self, *args):
        """Updates the data viewing toolbar based on selections."""
        super(BtmResultsViewer, self)._update_toolbar(self)

        vars_list = ['load', 'charge profile', 'total demand', 'state of charge', 
        # 'total bill', 'total savings'
        ]

        self.vars_button.values = vars_list

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

        if plot_type == 'load':
            for key in results:
                df = results[key]
                ax.plot((df['Pload'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('kWh')
            ax.set_xlabel('ending hour')
            ax.set_title('Load (kWh)')
        elif plot_type == 'charge profile':
            for key in results:
                df = results[key]

                ax.plot((df['Pcharge'] - df['Pdischarge'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('kWh')
            ax.set_xlabel('ending hour')
            ax.set_title('Charge Profile (kW)')
        elif plot_type == 'revenue':
            for key in results:
                df = results[key]
                ax.plot(df['revenue'][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

                ax.set_ylabel('$')
                ax.set_xlabel('ending hour')
                ax.set_title('Cumulative Revenue Generated ($)')
                ax.get_yaxis().set_major_formatter(
                    mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        elif plot_type == 'state of charge':
            for key in results:
                df = results[key]
                ax.plot(df['state of charge'][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

                ax.set_ylabel('kWh')
                ax.set_xlabel('ending hour')
                ax.set_title('State of Charge (kWh)')
        elif plot_type == 'total demand':
            for key in results:
                df = results[key]
                ax.plot(df['Ptotal'][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

                ax.set_ylabel('kW')
                ax.set_xlabel('ending hour')
                ax.set_title('Total Demand (kW)')
        # elif plot_type == 'total bill':
        #         ixes = range(len(results))
        #         heights = [results[key]['total_bill_with_es'].tail(1) for key in results]

        #         ax.bar(ixes, heights)
        #         labels=[textwrap.fill(' '.join(key.split(' | ')[:3]), 20) for key in results]

        #         ax.set_ylabel('$')
        #         ax.set_title('Total Bill')
        #         ax.grid(False)
        #         plt.xticks(ixes, labels)
        # elif plot_type == 'total savings':
        #         ixes = range(len(results))
        #         heights = [results[key]['total_bill_without_es'].tail(1) - results[key]['total_bill_with_es'].tail(1) for key in results]

        #         ax.bar(ixes, heights)
        #         labels=[textwrap.fill(' '.join(key.split(' | ')[:3]), 20) for key in results]

        #         ax.set_ylabel('$')
        #         ax.set_title('Total Savings')
        #         ax.grid(False)
        #         plt.xticks(ixes, labels)
        # else:
        #     for key in results:
        #         df = results[key]
        #         ax.plot(df[plot_type][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

        #         ax.set_title(plot_type)

        if plot_type in ['total bill', 'total savings']:
            pass
        else:
            ax.legend(bbox_to_anchor=(1.02, 0.5), loc="center left", borderaxespad=0, shadow=False, labelspacing=1.8)

        self.plotbox.children[0].draw()

    def export_png(self):
        """Exports currently displayed figure to .png file in specified location."""
        outdir_root = os.path.join('results', 'btm', 'plots')

        super(BtmResultsViewer, self).export_png(outdir_root)

    def export_csv(self):
        """Exports selected DataFrames to .csv files in specified location."""
        outdir_root = os.path.join('results', 'btm', 'csv')

        super(BtmResultsViewer, self).export_csv(outdir_root)
