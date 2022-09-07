from __future__ import absolute_import

import os
import textwrap
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
import numpy_financial as npf

import json

import pandas as pd
import geopandas as gpd
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1 import make_axes_locatable

from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

from es_gui.resources.widgets.common import EquityResultsViewer,PALETTE, rgba_to_fraction

STATIC_HOME = 'es_gui/apps/data_manager/_static'
data_file_name = 'disadvantaged_pop_by_county_2010.csv'
GEOJSON = "geojson-counties-fips.json"

class PowerPlantResultsViewer(EquityResultsViewer):
    """The screen for displaying plots inside the application or exporting results."""
    current_fig = ObjectProperty()
    current_ax = ObjectProperty()

    def __init__(self, **kwargs):
        super(PowerPlantResultsViewer, self).__init__(**kwargs)

        self.dfs = {}
        self.run_medidata = {}

        self.time_selector.start_time.bind(on_text_validate=self.draw_figure)
        self.time_selector.end_time.bind(on_text_validate=self.draw_figure)

    def on_pre_enter(self):
        #Window.bind(on_key_down=self._on_keyboard_down)

        self._update_toolbar()

        self.rv.data = self.manager.get_screen('equity_home').handler.get_solved_ops()

        geojon_file = os.path.join(STATIC_HOME, GEOJSON)
        with open(geojon_file) as f:
            self.counties = json.load(f)

        demographic_data_file_name = os.path.join(STATIC_HOME, data_file_name)

        #with open(data_file_name) as csvf:
        self.pop = {}
        self.dis = {}
        self.low = {}
        self.total_pop = 0
        self.total_dis = 0
        self.total_low = 0
        header = True
        with open(demographic_data_file_name, newline='') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')
            for row in csv_file:
                if not header:
                    ID = row[0]
                    self.pop[ID] = float(row[1])
                    self.dis[ID] = float(row[2])
                    self.low[ID] = float(row[3])
                    self.total_pop = self.total_pop + self.pop[ID]
                    self.total_dis = self.total_dis + self.pop[ID]*self.dis[ID]
                    self.total_low = self.total_low + self.pop[ID]*self.low[ID]
                header = False

    def _update_toolbar(self, *args):
        """Updates the data viewing toolbar based on selections."""
        super(PowerPlantResultsViewer, self)._update_toolbar(self)

        vars_list = ['cost-benefit','plant dispatch', 'pv power', 'es power', 'es+pv power', 'state of energy', 'benefits map',
        'disadvantage map', 'low-income map'
        ]

        self.vars_button.values = vars_list

    def draw_figure(self, *args):
        self._update_selection()

        if not self._validate_inputs():
            return

        start_time, end_time = self.time_selector.get_inputs()
        plot_type = self.vars_button.text
        
        results = self.dfs
        power_plant_file = self.rv.data[0]['run_medidata']['path']
        with open(power_plant_file) as f:
            self.power_plant_data = json.load(f)
        
        '''total_disadvantaged_population = self.power_plant_data['health_impact_equity']['total_disadvantaged_population']
        total_low_income_population = self.power_plant_data['health_impact_equity']['total_low_income_population']
        disadvantaged_population_fraction = self.power_plant_data['health_impact_equity']['disadvantaged_population_fraction']
        low_income_population_fraction = self.power_plant_data['health_impact_equity']['low_income_population_fraction']
        total_impact_on_disadvantaged_population_low = self.power_plant_data['health_impact_equity']['total_impact_on_disadvantaged_population_low']
        total_impact_on_disadvantaged_population_high = self.power_plant_data['health_impact_equity']['total_impact_on_disadvantaged_population_high']
        total_impact_on_low_income_population_low = self.power_plant_data['health_impact_equity']['total_impact_on_low_income_population_low']
        total_impact_on_low_income_population_high = self.power_plant_data['health_impact_equity']['total_impact_on_low_income_population_high']
        impact_on_disadvantaged_population_fraction = self.power_plant_data['health_impact_equity']['impact_on_disadvantaged_population_fraction']
        impact_on_low_income_population_fraction = self.power_plant_data['health_impact_equity']['impact_on_low_income_population_fraction']'''
        Pollution_Low_Value = self.power_plant_data['COBRA_results']['Summary']['TotalHealthBenefitsValue_low']
        Pollution_High_Value = self.power_plant_data['COBRA_results']['Summary']['TotalHealthBenefitsValue_high']

        self._reinit_graph(has_legend=True)

        fig = self.current_fig
        ax = self.current_ax
        ax.clear()
        plt.axis('on')
        plt.xticks(rotation=0)
        plt.grid(True)

        if plot_type == 'cost-benefit':
            max_total_cost = 0
            max_total_pollution_high = 0
            SCALE = 1000000
            iii = 0
            for key in self.run_medidata:
                replacement_fraction = self.run_medidata[key]['replacement_fraction']
                
                energy_capacity = self.run_medidata[key]['energy_capacity']
                power_capacity = self.run_medidata[key]['power_capacity']
                pv_capacity = self.run_medidata[key]['pv_capacity']
                
                pv_cost =  self.run_medidata[key]['cost_per_MW_PV_system'] * pv_capacity + self.run_medidata[key]['fixed_cost_of_PV_system']
                ess_cost = self.run_medidata[key]['cost_per_MWh_BESS'] * energy_capacity + self.run_medidata[key]['cost_per_MW_BESS'] * power_capacity + self.run_medidata[key]['fixed_cost_of_the_BESS']
                total_cost = pv_cost + ess_cost
                if total_cost  >max_total_cost:
                    max_total_cost = total_cost
                total_pollution_low = (Pollution_Low_Value + self.run_medidata[key]['cost_per_ton_of_CO2']*self.power_plant_data['CO2_emissions'])*replacement_fraction
                total_pollution_high = (Pollution_High_Value + self.run_medidata[key]['cost_per_ton_of_CO2']*self.power_plant_data['CO2_emissions'])*replacement_fraction
                if total_pollution_high > max_total_pollution_high:
                    max_total_pollution_high = total_pollution_high

                color = PALETTE[divmod(iii, len(PALETTE))[1]]
                ax.plot([total_cost/SCALE,total_cost/SCALE],[total_pollution_low/SCALE,total_pollution_high/SCALE],label='Low to High Est. R.P. ' +str(100*replacement_fraction) + '%',linewidth=5,color=rgba_to_fraction(color))
                iii += 1

            # payback sROI lines
            slope_5_year = -1/npf.pv(self.run_medidata[key]['discount_rate'],5,1,0)
            slope_10_year = -1/npf.pv(self.run_medidata[key]['discount_rate'],10,1,0)
            slope_15_year = -1/npf.pv(self.run_medidata[key]['discount_rate'],15,1,0)
            slope_20_year = -1/npf.pv(self.run_medidata[key]['discount_rate'],20,1,0)

            capital_range_5y  = 1.2*min(max_total_pollution_high/slope_5_year,max_total_cost)
            capital_range_10y = 1.2*min(max_total_pollution_high/slope_10_year,max_total_cost)
            capital_range_15y = 1.2*min(max_total_pollution_high/slope_15_year,max_total_cost)
            capital_range_20y = 1.2*min(max_total_pollution_high/slope_20_year,max_total_cost)

            payback_after_5_years  = capital_range_5y*slope_5_year 
            payback_after_10_years = capital_range_10y*slope_10_year 
            payback_after_15_years = capital_range_15y*slope_15_year 
            payback_after_20_years = capital_range_20y*slope_20_year 

            ax.plot([0,capital_range_5y/SCALE],[0,payback_after_5_years/SCALE],label='5 year sROI @'+str(100*self.run_medidata[key]['discount_rate'])+'%',linewidth=0.5,color=[0,0.1,0])
            ax.plot([0,capital_range_10y/SCALE],[0,payback_after_10_years/SCALE],label='10 year sROI @'+str(100*self.run_medidata[key]['discount_rate'])+'%',linewidth=0.5,color=[0,0.3,0])
            ax.plot([0,capital_range_15y/SCALE],[0,payback_after_15_years/SCALE],label='15 year sROI @'+str(100*self.run_medidata[key]['discount_rate'])+'%',linewidth=0.5,color=[0,0.7,0])
            ax.plot([0,capital_range_20y/SCALE],[0,payback_after_20_years/SCALE],label='20 year sROI @'+str(100*self.run_medidata[key]['discount_rate'])+'%',linewidth=0.5,color=[0,0.9,0])
                

            ax.set_ylabel('M$ / year in health and climate benefits \n and Sotial Return On Investment (sROI) thresholds')
            ax.set_xlabel('M$ captial cost')
            ax.set_title('Cost Benefit Analysis')

        if plot_type == 'plant dispatch':
            for key in results:
                df = results[key]
                ax.plot((df['plant dispatch'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MW')
            ax.set_xlabel('time (hours)')
            ax.set_title('Peaker Dispatch Power (MW)')

        elif plot_type == 'pv power':
            for key in results:
                df = results[key]
                ax.plot((df['Ppv'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MW')
            ax.set_xlabel('time (hours)')
            ax.set_title('PV Power (MW)')
        
        elif plot_type == 'es power':
            for key in results:
                df = results[key]
                ax.plot((df['es power'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MW')
            ax.set_xlabel('time (hours)')
            ax.set_title('ES Power (MW)')

        elif plot_type == 'es+pv power':
            for key in results:
                df = results[key]
                ax.plot((df['es+pv power'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MW')
            ax.set_xlabel('time (hours)')
            ax.set_title('PV Power + ES Power (MW)')

        elif plot_type == 'state of energy':
            for key in results:
                df = results[key]
                ax.plot((df['state of energy'])[start_time:end_time], drawstyle='steps-post', label=textwrap.fill(key, 50))

            ax.set_ylabel('MW')
            ax.set_xlabel('time (hours)')
            ax.set_title('State of Energy (MWh)')

        elif plot_type == 'benefits map':
            l_value_to_dis_per_county = []
            h_value_to_dis_per_county = []
            l_value_to_low_per_county = []
            h_value_to_low_per_county = []

            l_total_value = self.power_plant_data['COBRA_results']['Summary']['TotalHealthBenefitsValue_low']
            h_total_value = self.power_plant_data['COBRA_results']['Summary']['TotalHealthBenefitsValue_high']

            ben_frac = {}
            max_frac = 0
            for impact in self.power_plant_data['COBRA_results']['Impacts']:
                FIPS = impact['FIPS']
                #Shannon County, SD (FIPS code = 46113) was renamed Oglala Lakota County and assigned anew FIPS code (46102) effective in 2014.
                if FIPS == '46102':
                    FIPS = '46113'
                LV = impact['C__Total_Health_Benefits_Low_Value']
                HV = impact['C__Total_Health_Benefits_High_Value']
                ben_frac[FIPS] = HV/h_total_value
                if ben_frac[FIPS] > max_frac:
                    max_frac = ben_frac[FIPS] 
                l_value_to_dis_per_county.append(self.dis[FIPS]*LV)
                h_value_to_dis_per_county.append(self.dis[FIPS]*HV)
                l_value_to_low_per_county.append(self.low[FIPS]*LV)
                h_value_to_low_per_county.append(self.low[FIPS]*HV)

            print('low estemate of total health benfits  : $' + str(l_total_value))
            print('high estemate of total health benfits : $' + str(h_total_value))

            print('% of total population in disadvantaged comunities :' + str(self.total_dis/self.total_pop))
            print('% of total health benfits to disadvantaged comunities :' + str(sum(l_value_to_dis_per_county)/l_total_value))
            print('% of total population that is low income (<200% of poverty):' + str(self.total_low/self.total_pop))
            print('% of total health benfits to low income (<200% of poverty):' + str(sum(l_value_to_low_per_county)/l_total_value))

            colormap = plt.cm.get_cmap('Greens')
            colornorm = mpl.colors.Normalize(vmin=0, vmax=max_frac*100, clip=False)
            n = len(self.counties['features'])
            for ii in range(n):
                FIPS = self.counties['features'][ii]['properties']['STATE'] + self.counties['features'][ii]['properties']['COUNTY']
                #value = dis[FIPS] # set the color value to the % of disadvantaged within a county 
                try:
                    value = ben_frac[FIPS]/max_frac 
                except:
                    value = 0
                for jj in range(len(self.counties['features'][ii]['geometry']['coordinates'])):
                    try:
                        county_area = Polygon(self.counties['features'][ii]['geometry']['coordinates'][jj], False,edgecolor='black', facecolor=colormap(value))
                    except:
                        nnn = len(self.counties['features'][ii]['geometry']['coordinates'][jj])
                        for kk in range(nnn):
                            county_area = Polygon(self.counties['features'][ii]['geometry']['coordinates'][jj][kk], False,edgecolor='black', facecolor=colormap(value))
                    ax.add_patch(county_area)
            ax.set_xlim(-130,-60)
            ax.set_ylim(20,55)
            plt.axis('off')
            plt.title('% of Health Benefits That will go to Each US County\n(only the first selected run is mapped)')
            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            im = plt.cm.ScalarMappable(norm=colornorm, cmap=colormap)
            fig.colorbar(im, cax=cax, orientation='vertical')

        elif plot_type == 'disadvantage map':
            colormap = plt.cm.get_cmap('Oranges')
            colornorm = mpl.colors.Normalize(vmin=0, vmax=100, clip=False)
            n = len(self.counties['features'])
            for ii in range(n):
                FIPS = self.counties['features'][ii]['properties']['STATE'] + self.counties['features'][ii]['properties']['COUNTY']
                #value = dis[FIPS] # set the color value to the % of disadvantaged within a county 
                try:
                    value = self.dis[FIPS]
                except:
                    value = 0
                for jj in range(len(self.counties['features'][ii]['geometry']['coordinates'])):
                    try:
                        county_area = Polygon(self.counties['features'][ii]['geometry']['coordinates'][jj], False,edgecolor='black', facecolor=colormap(value))
                    except:
                        nnn = len(self.counties['features'][ii]['geometry']['coordinates'][jj])
                        for kk in range(nnn):
                            county_area = Polygon(self.counties['features'][ii]['geometry']['coordinates'][jj][kk], False,edgecolor='black', facecolor=colormap(value))
                    ax.add_patch(county_area)
            ax.set_xlim(-130,-60)
            ax.set_ylim(20,55)
            plt.axis('off')
            plt.title('% of Each US County that Lives in a Disadvantaged Community (justice40 data)\n(only the first selected run is mapped)')
            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            im = plt.cm.ScalarMappable(norm=colornorm, cmap=colormap)
            fig.colorbar(im, cax=cax, orientation='vertical')

        elif plot_type == 'low-income map':
            colormap = plt.cm.get_cmap('Blues')
            colornorm = mpl.colors.Normalize(vmin=0, vmax=100, clip=False)
            n = len(self.counties['features'])
            for ii in range(n):
                FIPS = self.counties['features'][ii]['properties']['STATE'] + self.counties['features'][ii]['properties']['COUNTY']
                #value = dis[FIPS] # set the color value to the % of disadvantaged within a county 
                try:
                    value = self.low[FIPS]
                except:
                    value = 0
                for jj in range(len(self.counties['features'][ii]['geometry']['coordinates'])):
                    try:
                        county_area = Polygon(self.counties['features'][ii]['geometry']['coordinates'][jj], False,edgecolor='black', facecolor=colormap(value))
                    except:
                        nnn = len(self.counties['features'][ii]['geometry']['coordinates'][jj])
                        for kk in range(nnn):
                            county_area = Polygon(self.counties['features'][ii]['geometry']['coordinates'][jj][kk], False,edgecolor='black', facecolor=colormap(value))
                    ax.add_patch(county_area)
            ax.set_xlim(-130,-60)
            ax.set_ylim(20,55)
            plt.axis('off')
            plt.title('% of Each US County With Income Below 200% of Poverty (justice40 data)\n(only the first selected run is mapped)')
            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            im = plt.cm.ScalarMappable(norm=colornorm, cmap=colormap)
            fig.colorbar(im, cax=cax, orientation='vertical')

        ax.legend(bbox_to_anchor=(1.02, 0.5), loc="center left", borderaxespad=0, shadow=False, labelspacing=1.8)

        self.plotbox.children[0].draw()

    def export_png(self):
        """Exports currently displayed figure to .png file in specified location."""
        outdir_root = os.path.join('results', 'equity', 'plots')

        super(PowerPlantResultsViewer, self).export_png(outdir_root)

    def export_csv(self):
        """Exports selected DataFrames to .csv files in specified location."""
        outdir_root = os.path.join('results', 'equity', 'csv')

        super(PowerPlantResultsViewer, self).export_csv(outdir_root)
