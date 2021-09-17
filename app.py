import pandas as pd
from plotly.graph_objs.bar import marker

import fueltools as ft
import preprocess as pp
import dash
from dash import dcc
from dash import html
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
pp.preProcess()

dataYear = 2018
flights_df = pp.loadDefaultDataset()

flights_df = ft.CalculateSAFCost(flights_df)
flights_df = ft.CalculateFuelCost(flights_df)
flights_df = ft.CalculateTotalFuelCost(flights_df)

regions_df = pd.read_excel('data/ICAOPrefix.xlsx')

memberStates = regions_df.loc[regions_df['EU_EEA_EFTA_UK'] == 'Y', ['COUNTRY']].COUNTRY.unique()

finalDf=flights_df


ms_df_outermost = flights_df[
    ((flights_df.ADEP_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADEP_OUTER_CLOSE == 'Y')) &
    ((flights_df.ADES_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADES_OUTER_CLOSE == 'Y')) &
    ~((flights_df.ADEP_OUTER_CLOSE == 'Y') & (flights_df.ADES_OUTER_CLOSE == 'Y')) &
    (flights_df.STATFOR_Market_Segment.isin(['Lowcost', 'Traditional Scheduled']))]

startSummerIATA, endSummerIATA = ft.getIATASeasons(dataYear)

per_ms_summer_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
    .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']] \
    .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std'], 'FUEL_COST': ['mean', 'std'],
          'TOTAL_FUEL_COST': ['mean', 'std']})
per_ms_summer_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
                                  .groupby(['ADEP_COUNTRY'])[['SAF_COST']] \
                                  .describe(percentiles=[0.25, 0.5, 0.75]).iloc[:, 4:7]

per_ms_summer_out = pd.concat([per_ms_summer_out, per_ms_summer_out_quantiles], axis=1)

per_ms_winter_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
    .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']] \
    .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std'], 'FUEL_COST': ['mean', 'std'],
          'TOTAL_FUEL_COST': ['mean', 'std']})

per_ms_winter_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
                                  .groupby(['ADEP_COUNTRY'])[['SAF_COST']] \
                                  .describe(percentiles=[0.25, 0.5, 0.75]).iloc[:, 4:7]

per_ms_winter_out = pd.concat([per_ms_winter_out, per_ms_winter_out_quantiles], axis=1)

per_ms_Annual_out = ((per_ms_summer_out * 7) + (per_ms_winter_out * 5))
per_ms_Annual_out.iloc[:, 1:] = per_ms_Annual_out.iloc[:, 1:] / 12

eu_avg = ms_df_outermost[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']].agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std'], 'FUEL_COST': ['mean', 'std'],
                                                                                        'TOTAL_FUEL_COST': ['mean', 'std']})

eu_avg_quantiles = ms_df_outermost[['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']].describe(percentiles=[0.25, 0.5, 0.75])

per_ms_Annual_out.loc['EU'] = (int(eu_avg.loc['size', 'ECTRL_ID']),
                               eu_avg.loc['mean', 'SAF_COST'],
                               eu_avg.loc['std', 'SAF_COST'],
                               eu_avg.loc['mean', 'FUEL_COST'],
                               eu_avg.loc['std', 'FUEL_COST'],
                               eu_avg.loc['mean', 'TOTAL_FUEL_COST'],
                               eu_avg.loc['std', 'TOTAL_FUEL_COST'],
                               eu_avg_quantiles.loc['25%', 'SAF_COST'],
                               eu_avg_quantiles.loc['50%', 'SAF_COST'],
                               eu_avg_quantiles.loc['75%', 'SAF_COST'])

app = dash.Dash(__name__)

per_ms_Annual_out.columns = ["_".join(a) for a in per_ms_Annual_out.columns.to_flat_index()]
per_ms_Annual_out = per_ms_Annual_out.sort_values(by=['SAF_COST_mean'], ascending=False)
per_ms_Annual_out = per_ms_Annual_out.round(2)
per_ms_Annual_out['ECTRL_ID_size'] = per_ms_Annual_out['ECTRL_ID_size'].astype(int)
per_ms_Annual_out = per_ms_Annual_out.rename(columns={'ECTRL_ID_size': 'Flights_size'})

per_ms_Annual_out = per_ms_Annual_out.reset_index()

dataSetSelection = ft.getYears()
dataSetPeriod = ft.getMonths()
dataSetPeriod.append('ALL')
extrapolateAnnual = True
fromSelection = regions_df.columns[2:].tolist()
fromSelection = fromSelection + ['!' + x for x in fromSelection]
toSelection = fromSelection
marketSelection = flights_df.STATFOR_Market_Segment.unique().tolist()

data = [
    go.Bar(name='SAF',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['SAF_COST_mean'],
           error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
           ),
    go.Bar(name='JET A1',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly'
           ),
    go.Bar(name='Total Fuel Cost',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly'
           )
]

layout = go.Layout(
    barmode='stack',
    title='Average Cost of Aviation Fuel'
)

fig = go.Figure(data=data, layout=layout)

app.layout = html.Div([
    html.Div([
        html.H1(children='Analysis of the Fit for 55 legislative proposals on Air Transport'),

        html.Div([
            html.P('Select dataset', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='DatasetSelection',
                options=[{'label': i, 'value': i} for i in dataSetSelection],
                value=2018, disabled=True
            ),
            html.P('Select Period', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='monthSelection',
                options=[{'label': i, 'value': i} for i in dataSetPeriod],
                value='ALL', disabled=True
            ),
            html.P('Select Departure Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='fromSelection',
                options=[{'label': i, 'value': i} for i in fromSelection],
                value=fromSelection[3]
            ),
            html.P('Select Destination Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='toSelection',
                options=[{'label': i, 'value': i} for i in toSelection],
                value=fromSelection[3]
            ),
            # html.P('Include Close outermost regions', style={"height": "auto", "margin-bottom": "auto"}),
            # dcc.Checklist(
            #     id='outerCheck',
            #     options=[
            #         {'label': 'Close Outermost Regions', 'value': 'OUTER_CLOSE'}
            #     ],
            #     value=['OUTER_CLOSE']
            # ),
            html.P('Select Market Segment', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='marketSelection',
                options=[{'label': i, 'value': i} for i in marketSelection], multi=True,
                value=['Traditional Scheduled', 'Lowcost']),

            html.Div([
                html.Div([html.P('SAF Price(USD/kg)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="safPrice", type="number", placeholder=3.66, value=3.66, ), ]),
                html.Div([html.P('JetA1 Price(USD/kg)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="jetPrice", type="number", placeholder=0.61, value=0.61, ), ]),
                html.Div([html.P('Blending Mandate (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="blendingMandate", type="number", placeholder=2, min=0, max=100, step=0.1, value=2, ), ]),
                html.Div([html.P('Tax rate(EURO/GJ)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="taxRate", type="number", placeholder=2.15, min=0, max=10.75, step=0.01, value=2.15, ), ]),
                html.Div([html.P('ETS Price(EURO/kg) ', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPrice", type="number", placeholder=60, min=0, max=1000, step=1, value=60, ), ]),
                html.Div([html.P('Emissions (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPercent", type="number", placeholder=50, min=0, max=100, step=1, value=50, ), ]),
            ], style=dict(display='flex', flexWrap='wrap', width=400)),

            html.P([]),
            html.Div([html.Button('Submit', style={"height": "auto", "margin-bottom": "20", "margin-top": "20"},
                                  id='submitButton'), ]),

        ],
            style={'width': '15%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='Cost_graph',
                figure=fig
            ),

            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in per_ms_Annual_out.columns],
                data=per_ms_Annual_out.to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=50,
            ),
            html.Div(id='datatable-interactivity-container')
        ], style={'width': '84%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),
])


@app.callback(
    [dash.dependencies.Output('Cost_graph', 'figure'),
    dash.dependencies.Output('table', 'data')],
    [dash.dependencies.Input('submitButton', 'n_clicks'),
     dash.dependencies.Input('fromSelection', 'value'),
     dash.dependencies.Input('toSelection', 'value'),
     dash.dependencies.Input('marketSelection', 'value'),
     dash.dependencies.Input('safPrice', 'value'),
     dash.dependencies.Input('blendingMandate', 'value'),
     dash.dependencies.Input('jetPrice', 'value')])
def update_graph(clicks, fromSel, toSel, market, safPrice, blending, jetPrice):

    flights_df = ft.CalculateSAFCost(finalDf, costOfSafFuelPerKg = safPrice, safBlendingMandate = blending/100 )
    flights_df = ft.CalculateFuelCost(flights_df, costOfJetFuelPerKg=jetPrice, safBlendingMandate=blending/100)
    flights_df = ft.CalculateTotalFuelCost(flights_df)

    regions_df = pd.read_excel('data/ICAOPrefix.xlsx')

    memberStates = regions_df.loc[regions_df['EU_EEA_EFTA_UK'] == 'Y', ['COUNTRY']].COUNTRY.unique()

    # ms_df = flights_df[(flights_df.ADEP_EU_EEA_EFTA_UK == 'Y') & (flights_df.ADES_EU_EEA_EFTA_UK == 'Y') & (
    #     flights_df.STATFOR_Market_Segment.isin(['Lowcost', 'Traditional Scheduled']))]
    ms_df_outermost = flights_df[
        ((flights_df.ADEP_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADEP_OUTER_CLOSE == 'Y')) &
        ((flights_df.ADES_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADES_OUTER_CLOSE == 'Y')) &
        ~((flights_df.ADEP_OUTER_CLOSE == 'Y') & (flights_df.ADES_OUTER_CLOSE == 'Y')) &
        (flights_df.STATFOR_Market_Segment.isin(market))]

    startSummerIATA, endSummerIATA = ft.getIATASeasons(dataYear)

    per_ms_summer_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']] \
        .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std'], 'FUEL_COST': ['mean', 'std'],
              'TOTAL_FUEL_COST': ['mean', 'std']})
    per_ms_summer_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
                                      .groupby(['ADEP_COUNTRY'])[['SAF_COST']] \
                                      .describe(percentiles=[0.25, 0.5, 0.75]).iloc[:, 4:7]

    per_ms_summer_out = pd.concat([per_ms_summer_out, per_ms_summer_out_quantiles], axis=1)

    per_ms_winter_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']] \
        .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std'], 'FUEL_COST': ['mean', 'std'],
              'TOTAL_FUEL_COST': ['mean', 'std']})

    per_ms_winter_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
                                      .groupby(['ADEP_COUNTRY'])[['SAF_COST']] \
                                      .describe(percentiles=[0.25, 0.5, 0.75]).iloc[:, 4:7]

    per_ms_winter_out = pd.concat([per_ms_winter_out, per_ms_winter_out_quantiles], axis=1)

    per_ms_Annual_out = ((per_ms_summer_out * 7) + (per_ms_winter_out * 5))
    per_ms_Annual_out.iloc[:, 1:] = per_ms_Annual_out.iloc[:, 1:] / 12

    eu_avg = ms_df_outermost[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']].agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std'], 'FUEL_COST': ['mean', 'std'],
                                                                                            'TOTAL_FUEL_COST': ['mean', 'std']})

    eu_avg_quantiles = ms_df_outermost[['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST']].describe(percentiles=[0.25, 0.5, 0.75])

    per_ms_Annual_out.loc['EU'] = (int(eu_avg.loc['size', 'ECTRL_ID']),
                                   eu_avg.loc['mean', 'SAF_COST'],
                                   eu_avg.loc['std', 'SAF_COST'],
                                   eu_avg.loc['mean', 'FUEL_COST'],
                                   eu_avg.loc['std', 'FUEL_COST'],
                                   eu_avg.loc['mean', 'TOTAL_FUEL_COST'],
                                   eu_avg.loc['std', 'TOTAL_FUEL_COST'],
                                   eu_avg_quantiles.loc['25%', 'SAF_COST'],
                                   eu_avg_quantiles.loc['50%', 'SAF_COST'],
                                   eu_avg_quantiles.loc['75%', 'SAF_COST'])

    app = dash.Dash(__name__)

    per_ms_Annual_out.columns = ["_".join(a) for a in per_ms_Annual_out.columns.to_flat_index()]
    per_ms_Annual_out = per_ms_Annual_out.sort_values(by=['SAF_COST_mean'], ascending=False)
    per_ms_Annual_out = per_ms_Annual_out.round(2)
    per_ms_Annual_out['ECTRL_ID_size'] = per_ms_Annual_out['ECTRL_ID_size'].astype(int)
    per_ms_Annual_out = per_ms_Annual_out.rename(columns={'ECTRL_ID_size': 'Flights_size'})

    per_ms_Annual_out = per_ms_Annual_out.reset_index()

    data = [
        go.Bar(name='SAF',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['SAF_COST_mean'],
               error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               ),
        go.Bar(name='JET A1',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly'
               ),
        go.Bar(name='Total Fuel Cost',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly'
               )
    ]

    layout = go.Layout(
        barmode='stack',
        title='Average Cost of Aviation Fuel'
    )

    fig = go.Figure(data=data, layout=layout)

    tab=per_ms_Annual_out.to_dict('records')


    return fig, tab



if __name__ == '__main__':
    app.run_server(debug=True)
