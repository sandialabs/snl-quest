from __future__ import absolute_import

import os
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt

from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

from es_gui.resources.widgets.common import ResultsViewer


class ValuationResultsViewer(ResultsViewer):
    """The screen for displaying plots inside the application or exporting results."""
    current_fig = ObjectProperty()
    current_ax = ObjectProperty()

    def __init__(self, **kwargs):
        super(ValuationResultsViewer, self).__init__(**kwargs)

        self.dfs = {}

        self.time_selector.start_time.bind(on_text_validate=self.draw_figure)
        self.time_selector.end_time.bind(on_text_validate=self.draw_figure)

    def on_pre_enter(self):
        """Updates the navigation bar's title."""
        ab = self.manager.nav_bar
        # ab.build_valuation_results_nav_bar()

        #Window.bind(on_key_down=self._on_keyboard_down)

        self._update_toolbar()

        self.rv.data = self.manager.get_screen('valuation_home').handler.get_solved_ops()
        # self.run_selector.rv.data = self.manager.get_screen('valuation_home').handler.solved_ops

    def _update_toolbar(self, *args):
        """Updates the data viewing toolbar based on selections."""
        super(ValuationResultsViewer, self)._update_toolbar(self)

        vars_list = ['revenue', 'state of charge', 'arbitrage activity', 'regulation capacity offered', 'price of electricity', 'price of electricity (box)']

        self.vars_button.values = vars_list

    def draw_figure(self, *args):
        self._update_selection()

        if not self._validate_inputs():
            return

        start_time, end_time = self.time_selector.get_inputs()
        plot_type = self.vars_button.text

        results = self.dfs

        if plot_type in ['price of electricity (box)']:
            self._reinit_graph(has_legend=False)
        else:
            self._reinit_graph(has_legend=True)

        fig = self.current_fig
        ax = self.current_ax
        ax.clear()

        plt.xticks(rotation=0)
        plt.grid(True)

        if plot_type == 'arbitrage activity':
            for key in results:
                df = results[key]
                ax.plot((df['q_r'] - df['q_d'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MWh')
            ax.set_xlabel('ending hour')
            ax.set_title('Energy Charged/Discharged (MWh)')
        elif plot_type == 'regulation capacity offered':
            for key in results:
                df = results[key]

                if (df['q_reg'] != 0).any():
                    ax.plot(df['q_reg'][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))
                else:
                    ax.plot((df['q_rd'] - df['q_ru'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MWh')
            ax.set_xlabel('ending hour')
            ax.set_title('Regulation Capacity Offered (MWh)')
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

                ax.set_ylabel('MWh')
                ax.set_xlabel('ending hour')
                ax.set_title('State of Charge (MWh)')
        elif plot_type == 'price of electricity':
            for key in results:
                df = results[key]
                ax.plot(df['price of electricity'][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

                ax.set_ylabel('$/MWh')
                ax.set_xlabel('ending hour')
                ax.set_title('Price of Electricity ($/MWh)')
        elif plot_type == 'price of electricity (box)':
                ax.boxplot([results[key]['price of electricity'][start_time:end_time] for key in results], labels=[textwrap.fill(' '.join(key.split()[:3]), 8) for key in results])

                ax.set_ylabel('$/MWh')
                ax.set_title('Price of Electricity ($/MWh)')
        else:
            for key in results:
                df = results[key]
                ax.plot(df[plot_type][start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

                ax.set_title(plot_type)

        if plot_type in ['price of electricity (box)']:
            pass
        else:
            ax.legend(bbox_to_anchor=(1.02, 0.5), loc="center left", borderaxespad=0, shadow=False, labelspacing=1.8)

        self.plotbox.children[0].draw()

    def export_png(self):
        """Exports currently displayed figure to .png file in specified location."""
        outdir_root = os.path.join('results', 'valuation', 'plots')

        super(ValuationResultsViewer, self).export_png(outdir_root)

    def export_csv(self):
        """Exports selected DataFrames to .csv files in specified location."""
        outdir_root = os.path.join('results', 'valuation', 'csv')

        super(ValuationResultsViewer, self).export_csv(outdir_root)


class RunSelector(ModalView):
    """
    A ModalView used for selecting which saved runs to view or export results from.
    """
    pass
