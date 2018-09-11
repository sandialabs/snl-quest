from __future__ import absolute_import

import os
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window

from es_gui.resources.widgets.common import WarningPopup, MyPopup


class PlotScreen(Screen):
    """The screen for displaying plots inside the application or exporting results."""
    current_fig = ObjectProperty()
    current_ax = ObjectProperty()

    def __init__(self, **kwargs):
        super(PlotScreen, self).__init__(**kwargs)

        self.dfs = {}

        self.time_selector.start_time.bind(on_text_validate=self.draw_figure)
        self.time_selector.end_time.bind(on_text_validate=self.draw_figure)

    def on_pre_enter(self):
        """Updates the navigation bar's title."""
        ab = self.manager.nav_bar
        ab.build_valuation_results_nav_bar()
        ab.set_title('Results Viewer')

        #Window.bind(on_key_down=self._on_keyboard_down)

        self._update_toolbar()

        self.rv.data = self.manager.get_screen('valuation_home').handler.solved_ops
        # self.run_selector.rv.data = self.manager.get_screen('valuation_home').handler.solved_ops

    def on_leave(self):
        """Resets all selections and the graph."""
        self._reset_screen()

    # def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
    #     if keycode == 40:  # 40 - Enter key pressed
    #         self.draw_figure()

    def _select_all_runs(self):
        for selectable_node in self.rv.layout_manager.get_selectable_nodes():
            self.rv.layout_manager.select_node(selectable_node)

    def _deselect_all_runs(self):
        while len(self.rv.layout_manager.selected_nodes) > 0:
            for selected_node in self.rv.layout_manager.selected_nodes:
                self.rv.layout_manager.deselect_node(selected_node)

    def _reset_screen(self):
        #rv = self.run_selector.rv
        rv = self.rv

        self._deselect_all_runs()

        # Clears graph.
        while len(self.plotbox.children) > 0:
            for widget in self.plotbox.children:
                if isinstance(widget, FigureCanvasKivyAgg):
                    self.plotbox.remove_widget(widget)

        # Reset spinners.
        self.vars_button.text = 'Select data'

        # Reset text input fields.
        self.time_selector.start_time.text = '0'
        self.time_selector.end_time.text = '744'

    def _reinit_graph(self, has_legend=True):
        # Clears graph.
        while len(self.plotbox.children) > 0:
            for widget in self.plotbox.children:
                if isinstance(widget, FigureCanvasKivyAgg):
                    self.plotbox.remove_widget(widget)
        
        fig, ax = plt.subplots()
        self.current_fig = fig
        self.current_ax = ax

        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        plt.rcParams.update({'font.size': 18, 'xtick.labelsize': 12, 'ytick.labelsize': 12,
                             'lines.linewidth': 2})
        plt.rc('legend', **{'fontsize': 10})

        if has_legend:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])

        plotbox = self.plotbox
        canvas = FigureCanvasKivyAgg(self.current_fig)
        plotbox.add_widget(canvas, index=0)

    def _update_toolbar(self, *args):
        """Updates the data viewing toolbar based on selections."""
        # if not self.dfs:
        #     # if no selections made, disable all toolbar buttons and return
        #     self.vars_button.disabled = True
        #     self.time_button.disabled = True
        #     self.draw_button.disabled = True
        #     self.csv_export_button.disabled = True
        #     self.png_export_button.disabled = True
        #
        #     return

        self.vars_button.disabled = False
        #self.time_button.disabled = False
        self.draw_button.disabled = False
        self.csv_export_button.disabled = False
        self.png_export_button.disabled = False

        vars_list = ['revenue', 'state of charge', 'arbitrage activity', 'regulation capacity offered', 'price of electricity', 'price of electricity (box)']

        self.vars_button.values = vars_list

    def _update_selection(self):
        """Updates the dict. of DataFrames whenever new selections of data are made."""

        # Identify the selected run(s) from RunSelector.
        #rv = self.run_selector.rv
        rv = self.rv
        runs_selected = [rv.data[selected_ix] for selected_ix in rv.layout_manager.selected_nodes]

        results = {}

        for run in runs_selected:
            label = run['name']
            df = run['optimizer'].results

            results[label] = df

        self.dfs = results

    def _validate_inputs(self):
        if not self.dfs:
            # No selections made.
            popup = WarningPopup()
            popup.popup_text.text = "Let's pick some solved models to view first."
            popup.open()

            return False

        plot_type = self.vars_button.text

        if plot_type == 'Select data':
            # No data to plot has been selected.
            popup = WarningPopup()
            popup.popup_text.text = "Let's select some data to view first."
            popup.open()

            return False

        if not self.time_selector.validate():
            return False

        return True

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
        os.makedirs(outdir_root, exist_ok=True)

        self._update_selection()

        if self.dfs:
            outname = os.path.join(outdir_root, self.vars_button.text+'.png')
            self.plotbox.children[0].export_to_png(outname)

            popup = WarningPopup(size_hint=(0.4, 0.4))
            popup.title = 'Success!'
            popup.popup_text.text = 'Figure successfully exported to:\n\n' + os.path.abspath(outname)
            popup.open()
        else:
            popup = WarningPopup()
            popup.popup_text.text = "Let's pick some solved models to view first."
            popup.open()

    def export_csv(self):
        """Exports selected DataFrames to .csv files in specified location."""
        outdir_root = os.path.join('results', 'valuation', 'csv')
        os.makedirs(outdir_root, exist_ok=True)
        
        self._update_selection()

        if self.dfs:
            for run in self.dfs:
                # Split and regenerate run label to make it filename-friendly.
                run_label_split = run.split(' | ')
                run_name = ' '.join(run_label_split[:4])

                # Strip non-alphanumeric chars.
                delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
                run_name = run_name.translate({ord(i): None for i in delchars})

                outname = os.path.join(outdir_root, run_name + '.csv')
                df = self.dfs[run]
                os.makedirs(outdir_root, exist_ok=True)
                df.to_csv(outname, index=False)

            popup = WarningPopup(size_hint=(0.4, 0.4))
            popup.title = 'Success!'
            popup.popup_text.text = 'File(s) successfully exported to:\n\n' + os.path.abspath(outdir_root)
            popup.open()
        else:
            popup = WarningPopup()
            popup.popup_text.text = "Let's pick some solved models to view first."
            popup.open()


class TimeSelector(MyPopup):
    """
    A Popup with TextInput fields for determining the range of time to display in the figure.
    """

    def __init__(self, **kwargs):
        super(TimeSelector, self).__init__(**kwargs)

    def _validate(self):
        """
        Validates the field entries before closing the TimeSelector.
        """
        try:
            start_time = int(self.start_time.text)
            end_time = int(self.end_time.text)
            assert(start_time < end_time)
        except ValueError:
            # empty text input
            popup = WarningPopup()
            popup.popup_text.text = 'All input fields must be populated to continue.'
            popup.open()
        except AssertionError:
            # start_time > end_time
            popup = WarningPopup()
            popup.popup_text.text = 'The start time cannot be greater than the end time.'
            popup.open()
        else:
            self.dismiss()

        # Note: We do not necessarily need to check for index errors because Series slicing does not throw exceptions


class TimeSelectorRow(GridLayout):
    def get_inputs(self):
        return int(self.start_time.text), int(self.end_time.text)

    def validate(self):
        """Validates the field entries before closing the TimeSelector."""
        try:
            start_time = int(self.start_time.text)
            end_time = int(self.end_time.text)
            assert(start_time < end_time)
        except ValueError:
            # empty text input
            popup = WarningPopup()
            popup.popup_text.text = 'All input fields must be populated to continue.'
            popup.open()

            return False
        except AssertionError:
            # start_time > end_time
            popup = WarningPopup()
            popup.popup_text.text = 'The start time cannot be greater than the end time.'
            popup.open()

            return False
        else:
            return True


class TimeTextInput(TextInput):
    """
    A TextInput field for entering time indices. Limited to three int characters only.
    """
    def insert_text(self, substring, from_undo=False):
        # limit to 3 chars
        substring = substring[:3 - len(self.text)]
        return super(TimeTextInput, self).insert_text(substring, from_undo=from_undo)


class RunSelector(ModalView):
    """
    A ModalView used for selecting which saved runs to view or export results from.
    """
    pass
