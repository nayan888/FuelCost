from maindash import app
from views.first_view import make_layout
import pandas as pd
import fueltools as ft
import preprocess as pp
import plotly.express as px

def loadDefaultDataset(year=None, month=None):
    # get available dataset years
    if year == None:
        yearsAvailable= ft.getYears()
        year = max(yearsAvailable)

    flights_df = ft.loadPickle(year, month)

    print("Loaded pickles for year ", year)
    print("Dataframe Shape:", flights_df.shape)
    print("Dataframe head", flights_df.head())

    return flights_df




def preProcess():

    fileList = ft.getfilenamesForProcessing('data')
    pp.preprocess(fileList)


def create_figure(df):
    fig = px.bar(df, x='year', y='pop')
    return fig


if __name__ == '__main__':


    # process any new files
    preProcess()

    dataYear = 2018
    flights_df = loadDefaultDataset()

    flights_df = ft.CalculateSAFCost(flights_df)
    flights_df = ft.CalculateFuelCost(flights_df)
    flights_df = ft.CalculateTotalFuelCost(flights_df)


    regions_df = pd.read_excel('data/ICAOPrefix.xlsx')

    memberStates=regions_df.loc[regions_df['EU_EEA_EFTA_UK']=='Y', ['COUNTRY']].COUNTRY.unique()

    ms_df = flights_df[(flights_df.ADEP_EU_EEA_EFTA_UK=='Y') & (flights_df.ADES_EU_EEA_EFTA_UK=='Y') & (flights_df.STATFOR_Market_Segment.isin(['Lowcost', 'Traditional Scheduled']))]
    ms_df_outermost = flights_df[((flights_df.ADEP_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADEP_OUTERMOST_REGIONS=='Y')) &
                                 ((flights_df.ADES_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADES_OUTERMOST_REGIONS=='Y')) &
                                 ~((flights_df.ADEP_OUTERMOST_REGIONS=='Y') & (flights_df.ADES_OUTERMOST_REGIONS=='Y')) &
                                 (flights_df.STATFOR_Market_Segment.isin(['Lowcost', 'Traditional Scheduled']))]

    startSummerIATA, endSummerIATA = ft.getIATASeasons(dataYear)

    per_ms_summer=ms_df[(ms_df['FILED_OFF_BLOCK_TIME']>=startSummerIATA) & (ms_df['FILED_OFF_BLOCK_TIME']<endSummerIATA)].groupby(['ADEP_COUNTRY'])[['SAF_COST','FUEL_COST','TOTAL_FUEL_COST']].mean()
    per_ms_winter=ms_df[(ms_df['FILED_OFF_BLOCK_TIME']<startSummerIATA) | (ms_df['FILED_OFF_BLOCK_TIME']>=endSummerIATA)].groupby(['ADEP_COUNTRY'])[['SAF_COST','FUEL_COST','TOTAL_FUEL_COST']].mean()

    per_ms_summer_out=ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME']>=startSummerIATA) & (ms_df_outermost['FILED_OFF_BLOCK_TIME']<endSummerIATA)].groupby(['ADEP_COUNTRY'])[['ECTRL_ID','SAF_COST','FUEL_COST','TOTAL_FUEL_COST']] \
        .agg({'ECTRL_ID':'size', 'SAF_COST': ['mean', 'std']})
    per_ms_winter_out=ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME']<startSummerIATA) | (ms_df_outermost['FILED_OFF_BLOCK_TIME']>=endSummerIATA)].groupby(['ADEP_COUNTRY'])[['SAF_COST','FUEL_COST','TOTAL_FUEL_COST']]\
        .agg(FLIGHT_COUNT='size', AVERAGE='mean')
    per_ms_Annual_out = ((per_ms_summer_out * 7) + (per_ms_winter_out * 5)) / 12

    per_ms_Annual = ((per_ms_summer * 7) + (per_ms_winter * 5)) / 12

    eu_avg = ms_df.loc[(ms_df['ADEP_OUTERMOST_REGIONS']=='N') & (ms_df['ADES_OUTERMOST_REGIONS']=='N'),['SAF_COST','FUEL_COST','TOTAL_FUEL_COST']].mean()
    eu_avg.name = 'EU'
    per_ms_Annual = per_ms_Annual.append(eu_avg)


    figure = create_figure(per_ms_Annual)



    app.layout = make_layout()
    app.run_server(debug=True)