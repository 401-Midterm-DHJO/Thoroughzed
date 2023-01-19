from app.model_predict import predict_horse_price
from app.meta_data_query_and_loop_script import get_summary_horse_data
from app.Horse import Horse
import pandas as pd
import numpy as np
import panel as pn
import holoviews as hv
import ssl
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from matplotlib.ticker import MaxNLocator
pn.extension('tabulator')


def launch_dashboard(id):
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    # GET HORSE DATA FROM API

    horse_object = get_summary_horse_data(id)
    horse = Horse(horse_object)

    ###############################################################################

    # IMPORT AND CLEAN DATABASES

    # clean_market_data = pd.read_csv('https://raw.githubusercontent.com/ThoroughZed-Analytics/Thoroughzed/dev/app/master_db_no_outliers.csv')
    # clean_market_data = clean_market_data[~pd.isna(clean_market_data['converted_price'])]
    market_data_no_outliers = pd.read_csv('https://raw.githubusercontent.com/ThoroughZed-Analytics/Thoroughzed/dev/app/master_db_no_outliers.csv')

    by_breed = market_data_no_outliers.groupby('breed_type').mean().reset_index()
    breed_daily = market_data_no_outliers.groupby(['day_sold', 'breed_type']).mean()
    by_blood = market_data_no_outliers.groupby('bloodline').median().reset_index()
    daily = market_data_no_outliers.groupby(['day_sold', 'bloodline']).mean()

    ################################################################################

    # BREED GRAPHS

    def win_rate_by_breed():
        fig = plt.figure()
        sns.barplot(data=by_breed, x='breed_type', y='win_rate')
        plt.xlabel('Breed')
        plt.ylabel('Win Rate (%)')
        plt.title('Mean Win Rate by Breed')
        return fig

    def avg_win_by_bloodline():
        fig = plt.figure()
        sns.barplot(data=by_blood, x='bloodline', y='overall.first')
        plt.xlabel('Blood Line')
        plt.ylabel('Mean Number of Wins')
        plt.title('Mean Number of Wins by Blood Line')
        return fig

    def violin_price_by_breed():
        fig = plt.figure()
        sns.violinplot(data=market_data_no_outliers, x='breed_type', y='converted_price')
        plt.xlabel('Breed')
        plt.ylabel('Sale Price (USD)')
        plt.title('Sales Price by Breed')
        return fig

    def line_breed():
        fig = plt.figure()
        sns.lineplot(data=breed_daily, x='day_sold', y='converted_price', hue='breed_type')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))
        plt.xticks(rotation=20)
        # fig.set(xlabel=None)
        plt.xlabel('Date')
        plt.ylabel('Sale Price (USD)')
        plt.title('Sale Price by Breed Over Time')
        return fig

    ##############################################################################

    # BLOODLINE GRAPHS

    def barchart_median_win_by_blood():
        fig = plt.figure()
        sns.barplot(data=by_blood, x='bloodline', y='win_rate')
        plt.xlabel('Blood Line')
        plt.ylabel('Win Rate (%)')
        plt.title('Median Win Rate by Blood Line')
        return fig

    def line_blood():
        fig = plt.figure()
        sns.lineplot(data=daily, x='day_sold', y='converted_price', hue='bloodline')
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))
        plt.xticks(rotation=20)
        # fig.set(xlabel=None)
        plt.xlabel('Date')
        plt.ylabel('Sale Price (USD)')
        plt.title('Sale Price by Blood Line Over Time')
        return fig

    ###############################################################################

    # DASHBOARD RENDERING

    corrected_breed = horse.breed.capitalize()

    sidebar_horse_data_message = f"""
    # **{horse.name}**
    ## ***{horse.genotype}*** ***{horse.bloodline}*** ***{corrected_breed}***
    * ## Win: *{"{0:.2f}".format(horse.win_rate)}%*
    * ## Place: *{"{0:.2f}".format(horse.place_rate)}%*
    * ## Show: *{"{0:.2f}".format(horse.show_rate)}%*
    * ## Total Races: *{"{0:,}".format(horse.total_races)}*
    * ## Free Win Rate: *{"{0:.2f}".format(horse.free_win_rate)}%*
    * ## Paid Win Rate: *{"{0:.2f}".format(horse.paid_win_rate)}%*
    """
    template = pn.template.FastListTemplate(
        title='ThoroughZED Analytics - Relative Valuation', logo='https://i.imgur.com/3rpZHfT.png', header_background='black', header_color='red', font='times', shadow=True,
        sidebar=[pn.pane.Markdown(sidebar_horse_data_message),
                 pn.pane.PNG(horse.img_url, sizing_mode='scale_both')],
        # main=[pn.Row(pn.Column(win_rate_by_breed),(avg_win_by_bloodline))],
        # names of graphs: barchart_median_win_by_blood lineplot_price_blood_time lineplot_sale_breed_time violin_price_by_breed avg_win_by_breed win_rate_by_breed
        main=[pn.Row(pn.Column(line_blood),
                    pn.Column(barchart_median_win_by_blood),
                    pn.Column(avg_win_by_bloodline)),
              pn.Row(pn.Column(line_breed),
                    pn.Column(win_rate_by_breed),
                    pn.Column(violin_price_by_breed))],
        accent_base_color="#88d8b0",
    )
    template.show()


if __name__ == "__main__":
    launch_dashboard(8919)
