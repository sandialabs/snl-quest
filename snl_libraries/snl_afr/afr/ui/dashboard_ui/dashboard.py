from PySide6.QtWidgets import QWidget, QLabel

from PySide6.QtCore import Signal, QUrl, Qt

from afr.ui.dashboard_ui.ui.ui_dashboard import Ui_dashboard
import plotly.graph_objects as go
from afr.ui.ui_tools.table_widget import rps_table
import tempfile
import os
from afr.ui.ui_tools.pie_charts import CircularGraphicWidget, LegendWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from afr.paths import get_path
base_dir = get_path()

class dashboard_widget(QWidget, Ui_dashboard):
    """Class for the results dashboard page."""
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(dashboard_widget, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler
        self.pie_chart_data = []  # Data for the entire time horizon
        color_test =  ["#ebdc78", "#5ad45a", "#00b7c7", "#b30000", "#7c1158", "#4421af", "#1a53ff", "#006400"]
        self.pie_chart_names = ["PV", "Wind"] + [gen for gen in self.data_handler.Pgen]
        self.pie_chart_widget = CircularGraphicWidget(self.pie_chart_data, self.pie_chart_names, color_test)
        self.legend_widget = LegendWidget(self.pie_chart_names, self.pie_chart_widget.colors)
        self.pie_layout.addWidget(self.pie_chart_widget, alignment=Qt.AlignTop)
        self.pie_layout.addWidget(self.legend_widget)

        #setting up the stacked widget for the results
        self.stacked_results.setCurrentWidget(self.disp_sto_page)
        self.disp_sto.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.disp_sto_page))
        self.disp_no.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.disp_no_page))
        self.cap_sto.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.cap_sto_page))
        self.cap_no.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.cap_no_page))
        self.sankey.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.sankey_page))
        self.daily_gen.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.daily_page))
        self.place_holder.clicked.connect(lambda: self.stacked_results.setCurrentWidget(self.placeholder))


    def display_results(self):
        """Add optimization results to the dashboard page"""
        for layout in [self.disp_sto_layout, self.disp_no_layout, self.cap_sto_layout, self.cap_no_layout, self.sankey_layout, self.daily_page_layout, self.place_layout]:
            for i in reversed(range(layout.count())):
                widget_to_remove = layout.itemAt(i).widget()
                layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)

        # Get the Plotly figures from the optimizer
        figures = self.visualize_results()

        # Add the Plotly figures to the respective layouts
        layouts = [self.disp_sto_layout, self.disp_no_layout, self.cap_sto_layout, self.cap_no_layout, self.sankey_layout, self.daily_page_layout, self.place_layout]
        for fig, layout in zip(figures, layouts):
            web_view = QWebEngineView()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
                fig.write_html(f.name, config={'responsive': True})

                # Read the generated HTML content with UTF-8 encoding
                with open(f.name, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Inject CSS for the background color and margins
                styled_html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                            background-color: #1e1e1e;
                            overflow: auto;
                        }}
                        .content {{
                            position: relative;
                            z-index: 1;
                            margin: 20px;
                            background-color: #1e1e1e;
                            padding: 30px;
                            box-sizing: border-box;
                           # transform: scale(0.8);
                            transform-origin: top left; /* Scale from the top-left corner */
                           # width: calc(100% / .8); /* Adjust width to fill the space */
                            height: calc(100% / 1.7); /* Adjust height to fill the space */
                        }}
                        .overlay {{
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            background-color: #1e1e1e;
                            z-index: 0;
                            pointer-events: none;
                        }}
                        .overlay::before {{
                            content: '';
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            border: 30px solid #1e1e1e;
                            box-sizing: border-box;
                        }}
                        /* Style the scrollbar */
                        ::-webkit-scrollbar {{
                            width: 12px;
                        }}
                        ::-webkit-scrollbar-track {{
                            background: #1e1e1e;
                        }}
                        ::-webkit-scrollbar-thumb {{
                            background-color: #555;
                            border-radius: 10px;
                            border: 3px solid #1e1e1e;
                        }}
                        ::-webkit-scrollbar-corner {{
                            background: #1e1e1e;
                        }}
                    </style>
                </head>
                <body>
                    <div class="overlay"></div>
                    <div class="content">
                        {html_content}
                    </div>
                </body>
                </html>
                """

                # Write the styled HTML content back to the file with UTF-8 encoding
                with open(f.name, 'w', encoding='utf-8') as file:
                    file.write(styled_html_content)

                web_view.setUrl(QUrl.fromLocalFile(f.name))
            layout.addWidget(web_view)

        # Calculate RPS targets
        rps_data = self.calculate_rps_target()

        if hasattr(self, 'rps_display'):
            self.results_table_layout.removeWidget(self.rps_display)
            self.rps_display.deleteLater()

        # Create and update the YearCategoryTable
        # rps_80_year = int(self.rps_80_year.currentText())
        # rps_100_year = int(self.rps_100_year.currentText())
        self.rps_display = rps_table(self.data_handler.rps_target_years)
        self.rps_display.update_table(rps_data)

        # Add the YearCategoryTable to the layout

        self.disclaimer = QLabel("The results presented here are dependent on the assumptions made and should be treated as minimum requirements. Further detail can be assessed using capacity expansion, resource adequacy, and production cost models.")
        self.results_table_layout.addWidget(self.rps_display, alignment=Qt.AlignCenter)
        self.results_table_layout.addWidget(self.disclaimer, alignment=Qt.AlignCenter)

        start_year = int(self.data_handler.start_year)
        end_year = int(self.data_handler.end_year) + 1
        for year in range(start_year, end_year):
            self.pie_combo.addItem(str(year))
        self.pie_combo.currentIndexChanged.connect(self.update_gen_chart)

        self.pie_chart_names = ["PV", "Wind"] + [gen for gen in self.data_handler.Pgen]
        self.legend_widget.names = self.pie_chart_names
        self.legend_widget.update()
        self.pie_chart_widget.names = self.pie_chart_names
        self.pie_chart_data = [value for value in self.calculate_energy_generation_by_source_total().values()]  # Data for the entire time horizon
        self.pie_chart_widget.data = self.pie_chart_widget.normalize_data(self.pie_chart_data)
        self.pie_chart_widget.update()

        # Update the labels with the calculated values
        time_index = self.data_handler.end_year - self.data_handler.start_year
        self.es_cap_label.setText(f"{self.calculate_energy_storage_capacity(time_index):,.2f} MW")
        total_es_investment = self.calculate_energy_storage_investment(time_index)
        self.es_invest_label.setText(f"$ {total_es_investment:,.2f}")

        self.re_cap_label.setText(f"{self.calculate_renewable_capacity(time_index):,.2f} MW")
        total_re_investment = self.calculate_renewable_investment(time_index)[-1]
        self.re_inv_label.setText(f"$ {total_re_investment:,.2f}")

        self.change_page.emit(1)
       # self.stackedWidget.setCurrentWidget(self.results)

    def calculate_energy_generation_by_source_total(self):
        """Calculate the total energy generation by source over the entire time horizon."""

        return {gen: sum(sum(self.data_handler.results[gen][yr]) for yr in range(self.data_handler.horizon)) 
                        for gen in ['Epv', 'Ewind'] + [gen for gen in self.data_handler.Pgen]}

    def update_gen_chart(self):
        """Update the pie chart based on the combo box selection."""
        selected_option = self.pie_combo.currentText()
        if selected_option == "Total":
            self.pie_chart_data = [value for value in self.calculate_energy_generation_by_source_total().values()]
        else:
            start_year = int(self.data_handler.start_year)
            year = int(selected_option) - start_year
            self.pie_chart_data = self.calculate_energy_generation_by_source(year)
        self.pie_chart_widget.data = self.pie_chart_widget.normalize_data(self.pie_chart_data)
        self.pie_chart_widget.update_data(self.pie_chart_data)

    def calculate_energy_generation_by_source(self, year):
        """Calculate the total energy generation by source for a specific year."""
      
        gen = [sum(self.data_handler.results[gen][year]) for gen in ['Epv', 'Ewind'] + \
               [gen for gen in self.data_handler.Pgen]]

        return gen

    def calculate_non_renewable_energy_generation(self, year):
        """Calculate the total non-renewable energy generation for a specific year."""

        year = year - self.data_handler.start_year
        return sum([sum(self.data_handler.results[gen][year]) for gen in 
                    [self.data_handler.dirty[i] for i in self.data_handler.dirty]])

    def calculate_rps_target(self):
        """Calculate the RPS target based on the target years."""

        rps_data = {}
        for year in self.data_handler.rps_target_years:
            year = year - self.data_handler.start_year
            gen = self.calculate_energy_generation_by_source(year)
            clean = [0, 1] + [i + 2 for i in self.data_handler.clean]
            dirty = [i + 2 for i in self.data_handler.dirty]
            rps_data[year] = [
                self.calculate_energy_storage_investment(year),
                self.calculate_energy_storage_capacity(year),
                self.calculate_renewable_capacity(year),
                self.calculate_renewable_investment(year)[-1],
                sum([gen[i] for i in clean]),  # Renewable energy generation
                sum([gen[i] for i in dirty])   # Non-renewable energy generation
            ]

        return rps_data

    def calculate_energy_storage_investment(self, horizon):
        """Calculate the total energy storage investment up to a specified horizon."""

        investments = {}
        for device in self.data_handler.es_devices:
            duration = self.data_handler.es_devices[device]['duration']
            investments[f"{device} Power"] = sum(self.data_handler.results[f"{device} Power"][yr]*(duration * self.data_handler.Ces[device][yr] + self.data_handler.Cpcs[yr])
                                   for yr in range(horizon+1))

        total_investment = sum(investments[device] for device in investments)

        return total_investment


    def calculate_energy_storage_capacity(self, time_diff):
        """Calculate the total energy storage capacity for a specific year."""
        
        Pes_final = sum(self.data_handler.results[f"{device} Total Power"].iloc[time_diff]
                        for device in self.data_handler.es_devices)

        return Pes_final

    def calculate_renewable_capacity(self, time_diff):
        """Calculate the total renewable capacity for a specific year."""
        Ppv_final = self.data_handler.results['Ppv_tot'].iloc[time_diff]
        Pwind_final = self.data_handler.results['Pwind_tot'].iloc[time_diff]

        return Ppv_final + Pwind_final

    def calculate_renewable_investment(self, horizon):
        """Calculate the total renewable investment up to a specified horizon."""
        pv_investment = sum(self.data_handler.results['Ppv'][yr] * self.data_handler.Cpv[yr] for yr in range(horizon+1))
        wind_investment = sum(self.data_handler.results['Pwind'][yr] * self.data_handler.Cwind[yr] for yr in range(horizon+1))

        # Debugging: Print intermediate values
        print(f"Horizon: {horizon}")
        print(f"Total PV Investment: {pv_investment}, Total Wind Investment: {wind_investment}")

        total_investment = pv_investment + wind_investment

        # Debugging: Print total investment
        print(f"Total Renewable Investment: {total_investment}")

        return pv_investment, wind_investment, total_investment


    def visualize_results(self):
        # Create a list to hold the Plotly figures
        figures = []

        # Generate the x-axis labels based on the start year and horizon
        years = [self.data_handler.start_year + i for i in range(self.data_handler.horizon)]

        # Define a dark theme layout
        dark_theme_layout = {
            'paper_bgcolor': '#1e1e1e',  # Match QWidget background color
            'plot_bgcolor': '#1e1e1e',   # Match QWidget background color
            'font': {
                'color': '#d4d4d4'       # Match QWidget text color
            },
            'xaxis': {
                'gridcolor': '#3c3c3c',  # Match QTextEdit border color
                'zerolinecolor': '#3c3c3c',
                'linecolor': '#d4d4d4',  # Match QWidget text color
                'tickcolor': '#d4d4d4',  # Match QWidget text color
                'tickmode': 'linear',    # Ensure ticks are at integer intervals
                'dtick': 1               # Set the interval between ticks to 1 year
            },
            'yaxis': {
                'gridcolor': '#3c3c3c',  # Match QTextEdit border color
                'zerolinecolor': '#3c3c3c',
                'linecolor': '#d4d4d4',  # Match QWidget text color
                'tickcolor': '#d4d4d4'   # Match QWidget text color
            },
            'autosize': True  # Enable autosize to make the figure responsive
        }

        # Define color palette
        # contrast_colors =["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"]
        contrast_colors =["#ebdc78", "#8be04e", "#006400", "#00b7c7", "#0d88e6", "#1a53ff", "#4421af", "#7c1158", "#b30000"]
        renewable_colors = ["#8be04e", "#5ad45a", "#006400", "#003300"]
        non_renewable_colors = ["#b30000", "#7c1158", "#4421af", "#1a53ff",]
        storage_colors = ["#5ad45a", "#8be04e", "#00b7c7", "#0d88e6"]  # Greens and cool colors for storage
        generation_colors = ["#5ad45a", "#0d88e6"]  # Greens and cool colors for generation
         # Figure 1: Yearly total installed capacities
        fig1 = go.Figure()
        capacities = ['Ppv_tot', 'Pwind_tot'] + [f"{device} Total Power" for device 
                                                 in self.data_handler.es_devices]
        for i, capacity in enumerate(capacities):
            print(capacity)
            print(self.data_handler.results[capacity])
            fig1.add_trace(go.Bar(
                x=years,
                y=self.data_handler.results[capacity],
                name=capacity.replace('_', ' ').title(),
                marker_color=contrast_colors[i % len(contrast_colors)]
            ))
        fig1.update_layout(
            barmode='stack',
            title='Yearly Total Installed Capacities',
            xaxis_title='Year',
            yaxis_title='Capacity (MW)',
            **dark_theme_layout
        )
        figures.append(fig1)

        # Figure 2: Yearly Capacity Investments
        fig2 = go.Figure()
        inv_ls = ['PV', 'Wind'] + [device for device in self.data_handler.es_devices]
        investments = {
            'Ppv': self.data_handler.Cpv,
            'Pwind': self.data_handler.Cwind,
        }
        for device in self.data_handler.es_devices:
            duration = self.data_handler.es_devices[device]['duration']
            investments[f"{device} Power"] = [(duration * self.data_handler.Ces[device][yr] + self.data_handler.Cpcs[yr])
                                   for yr in range(self.data_handler.horizon)]

        for i, (investment, costs) in enumerate(investments.items()):
            y_values = [self.data_handler.results[investment][yr] * costs[yr] for yr in range(self.data_handler.horizon)]

            fig2.add_trace(go.Bar(
                x=years,
                y=y_values,
                name=investment.replace('_', ' ').title(),
                marker_color=contrast_colors[i % len(contrast_colors)]
            ))

        fig2.update_layout(
            barmode='stack',
            title='Yearly Capacity Investments',
            xaxis_title='Year',
            yaxis_title='Capacity Investment ($)',
            **dark_theme_layout
        )
        figures.append(fig2)

        # Figure 3: Total investments split by technology
        total_investments = {
            'PV': sum(self.data_handler.results['Ppv'][yr] * self.data_handler.Cpv[yr] for yr in range(self.data_handler.horizon)),
            'Wind': sum(self.data_handler.results['Pwind'][yr] * self.data_handler.Cwind[yr] for yr in range(self.data_handler.horizon)),
        }
        for device in self.data_handler.es_devices:
            duration = self.data_handler.es_devices[device]['duration']
            total_investments[device] = sum(self.data_handler.results[f"{device} Power"][yr] * 
                                            (duration * self.data_handler.Ces[device][yr] + self.data_handler.Cpcs[yr])
                                   for yr in range(self.data_handler.horizon))
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=list(total_investments.keys()),
            y=list(total_investments.values()),
            marker_color=contrast_colors[:2] + contrast_colors[2:6]  # Use renewable colors for all bars
        ))
        fig3.update_layout(
            title='Total Investments Split by Technology',
            xaxis_title='Technology',
            yaxis_title='Total Investment ($)',
            **dark_theme_layout
        )
        figures.append(fig3)

        # Figure 4: Yearly energy generation split by renewable and non-renewable technologies
        renewable_sources = ['Epv', 'Ewind'] + [self.data_handler.clean[key] for key in self.data_handler.clean]
        non_renewable_sources = [self.data_handler.dirty[key] for key in self.data_handler.dirty]
        yearly_renewable_generation = [
            sum(sum(self.data_handler.results[source][yr]) for source in renewable_sources) for yr in range(self.data_handler.horizon)
        ]
        yearly_non_renewable_generation = [
            sum(sum(self.data_handler.results[source][yr]) for source in non_renewable_sources) for yr in range(self.data_handler.horizon)
        ]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=years,
            y=yearly_renewable_generation,
            name='Renewable',
            marker_color=renewable_colors[0]
        ))
        fig4.add_trace(go.Bar(
            x=years,
            y=yearly_non_renewable_generation,
            name='Non-Renewable',
            marker_color=non_renewable_colors[0]
        ))
        fig4.update_layout(
            barmode='stack',
            title='Yearly Energy Generation Split by Technology',
            xaxis_title='Year',
            yaxis_title='Energy Generation (MWh)',
            **dark_theme_layout
        )
        figures.append(fig4)

        # Figure 5: Seasonal energy generation split by renewable and non-renewable technologies
        seasons = {
            'Winter': range(1, 91),   # Days 1-90
            'Spring': range(91, 182), # Days 91-181
            'Summer': range(182, 273),# Days 182-272
            'Fall': range(273, 365)   # Days 273-364
        }
        seasonal_renewable_generation = {season: [] for season in seasons}
        seasonal_non_renewable_generation = {season: [] for season in seasons}
        for season, days in seasons.items():
            for yr in range(self.data_handler.horizon):
                seasonal_renewable_generation[season].append(
                    sum(sum(self.data_handler.results[source][yr][day-1] for day in days) for source in renewable_sources)
                )
                seasonal_non_renewable_generation[season].append(
                    sum(sum(self.data_handler.results[source][yr][day-1] for day in days) for source in non_renewable_sources)
                )

        fig5 = go.Figure()

        # Add renewable traces first
        for i, season in enumerate(seasons):
            fig5.add_trace(go.Bar(
                x=years,
                y=seasonal_renewable_generation[season],
                name=f'Renewable ({season})',
                marker_color=renewable_colors[i % 4]  # Use the first 4 colors for renewables
            ))

        # Add non-renewable traces on top
        for i, season in enumerate(seasons):
            fig5.add_trace(go.Bar(
                x=years,
                y=seasonal_non_renewable_generation[season],
                name=f'Non-Renewable ({season})',
                marker_color=non_renewable_colors[i % 4]  # Use the last 4 colors for non-renewables
            ))

        fig5.update_layout(
            barmode='stack',
            title='Seasonal Energy Generation Split by Technology',
            xaxis_title='Year',
            yaxis_title='Energy Generation (MWh)',
            **dark_theme_layout
        )
        figures.append(fig5)

        # Update dark theme layout for x-axis ticks
        dark_theme_layout_with_ticks = dark_theme_layout.copy()
        dark_theme_layout_with_ticks['xaxis'] = {
            'gridcolor': '#3c3c3c',  # Match QTextEdit border color
            'zerolinecolor': '#3c3c3c',
            'linecolor': '#d4d4d4',  # Match QWidget text color
            'tickcolor': '#d4d4d4',  # Match QWidget text color
            'tickmode': 'linear',    # Ensure ticks are at integer intervals
            'dtick': 10              # Set the interval between ticks to 10 days
        }

        # Figure 6: Daily energy storage charge/discharge for each year/season
        fig6 = go.Figure()
        storage_sources = [f"{device} Discharge Energy" for device in self.data_handler.es_devices]
        for i, source in enumerate(storage_sources):
            for yr in range(self.data_handler.horizon):
                fig6.add_trace(go.Scatter(
                    x=list(range(1, 366)),
                    y=self.data_handler.results[source][yr],
                    mode='lines',
                    name=f"{source.replace('_', ' ').title()} Year {self.data_handler.start_year + yr}",
                    line=dict(color=storage_colors[i % len(storage_colors)])
                ))
        fig6.update_layout(
            title='Daily Energy Storage Discharge',
            xaxis_title='Day of Year',
            yaxis_title='Energy (MWh)',
            **dark_theme_layout_with_ticks
        )
        figures.append(fig6)

        # Figure 7: Daily wind/PV energy generation for each year/season
        fig7 = go.Figure()
        generation_sources = ['Epv', 'Ewind']
        for i, source in enumerate(generation_sources):
            for yr in range(self.data_handler.horizon):
                fig7.add_trace(go.Scatter(
                    x=list(range(1, 366)),
                    y=self.data_handler.results[source][yr],
                    mode='lines',
                    name=f"{source.replace('_', ' ').title()} Year {self.data_handler.start_year + yr}",
                    line=dict(color=generation_colors[i % len(generation_colors)])
                ))
        fig7.update_layout(
            title='Daily Wind/PV Energy Generation',
            xaxis_title='Day of Year',
            yaxis_title='Energy (MWh)',
            **dark_theme_layout_with_ticks
        )
        figures.append(fig7)
        return figures
