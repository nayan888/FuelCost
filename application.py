import pandas as pd
import fueltools as ft
import preprocess as pp
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash(__name__) #external_stylesheets=external_stylesheets)

app.title='Fit for 55 Impact on Air Transport'

pp.pre_process()

dataYear = 2018
flights_df = pp.loadDefaultDataset()

flights_df = ft.CalculateSAFCost(flights_df)
flights_df = ft.CalculateFuelCost(flights_df)
flights_df = ft.CalculateTotalFuelCost(flights_df)
flights_df = ft.CalculateTaxCost(flights_df)
flights_df = ft.CalculateETSCost(flights_df)

flights_df['TOTAL_COST'] = flights_df['SAF_COST'] + flights_df['TAX_COST'] + flights_df['ETS_COST']

regions_df = pd.read_excel('data/ICAOPrefix.xlsx')
#default from selection
fromSelection = regions_df.columns[2:].tolist()
defFromSelection = fromSelection[3]

finalDf=flights_df


dataSetSelection = ft.getYears()
dataSetPeriod = ft.getMonths()

fromSelection = fromSelection + ['!' + x for x in fromSelection]
fromSelDict =  [
    {'label':fromSelection[0] , 'value':'(ADEP_' + fromSelection[0] + '=="Y")'},
    {'label':fromSelection[1] , 'value':'(ADEP_' + fromSelection[1] + '=="Y")'},
    {'label':fromSelection[2] , 'value':'(ADEP_' + fromSelection[2] + '=="Y")'},
    {'label':fromSelection[3] , 'value':'(ADEP_' + fromSelection[3] + '=="Y")'},
    {'label':fromSelection[4] , 'value':'(ADEP_' + fromSelection[4] + '=="Y")'},
    {'label':fromSelection[5] , 'value':'(ADEP_' + fromSelection[5][1:] + '=="N")'},
    {'label':fromSelection[6] , 'value':'(ADEP_' + fromSelection[6][1:] + '=="N")'},
    {'label':fromSelection[7] , 'value':'(ADEP_' + fromSelection[7][1:] + '=="N")'},
    {'label':fromSelection[8] , 'value':'(ADEP_' + fromSelection[8][1:] + '=="N")'},
    {'label':fromSelection[9] , 'value':'(ADEP_' + fromSelection[9][1:] + '=="N")'},
]
toSelection = fromSelection

toSelDict =  [
    {'label':fromSelection[0] , 'value':'(ADES_' + fromSelection[0] + '=="Y")'},
    {'label':fromSelection[1] , 'value':'(ADES_' + fromSelection[1] + '=="Y")'},
    {'label':fromSelection[2] , 'value':'(ADES_' + fromSelection[2] + '=="Y")'},
    {'label':fromSelection[3] , 'value':'(ADES_' + fromSelection[3] + '=="Y")'},
    {'label':fromSelection[4] , 'value':'(ADES_' + fromSelection[4] + '=="Y")'},
    {'label':fromSelection[5] , 'value':'(ADES_' + fromSelection[5][1:] + '=="N")'},
    {'label':fromSelection[6] , 'value':'(ADES_' + fromSelection[6][1:] + '=="N")'},
    {'label':fromSelection[7] , 'value':'(ADES_' + fromSelection[7][1:] + '=="N")'},
    {'label':fromSelection[8] , 'value':'(ADES_' + fromSelection[8][1:] + '=="N")'},
    {'label':fromSelection[9] , 'value':'(ADES_' + fromSelection[9][1:] + '=="N")'},
]

groupByDict = [
    { 'label' : 'Country'   , 'value': 'ADEP_COUNTRY'},
    { 'label' : 'Aerodrome' , 'value': 'ADEP'},
    { 'label' : 'Airline'   , 'value': 'AC_Operator' }
]

marketSelection = flights_df.STATFOR_Market_Segment.unique().tolist()

app.layout = html.Div([
    html.Div([
        html.H1(children='Analysis of the Fit for 55 legislative proposals on Air Transport'),

    html.Div([
        html.P('Connect with me on: '),
        html.A(
            html.Img(src='assets/images/linkedin.png', className='img'),
            href='https://www.linkedin.com/in/eftychios-eftychiou-88686843/'),
        html.A(
            html.Img(src='/assets/images/twitter.png', className='img'),
            href='https://twitter.com/EEftychiou'
        ),
        html.A(
            html.Img(src='/assets/images/github.png', className='img',
                     id='github'),
            href='https://github.com/eeftychiou'
        ),
        html.A(
            html.Img(src='/assets/images/gmail.png', className='img',
                     id='gmail'),
            href='mailto:eftychios.eftychiou@gmail.com'
        )

    ]), ],id='header-div'),

    html.Div([
        html.P('Uses Eurocontrol R&D Archive', style={"height": "auto", "margin-bottom": "auto"}),
        html.A("Wiki Page", href="https://github.com/eeftychiou/FuelCost/wiki/Fit55-Impact-Calculator", target="_blank")]),

        html.Div([
            html.P('Select dataset', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='DatasetSelection',
                options=[{'label': i, 'value': i} for i in dataSetSelection],
                value=dataYear, disabled=False, clearable = False
            ),
            html.P('Select Period', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='monthSelection', multi=True,
                options=[{'label': i, 'value': i} for i in dataSetPeriod],
                value=dataSetPeriod, disabled=True, clearable = False
            ),
            html.P('Select Departure Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='fromSelection',
                options=fromSelDict,
                value=fromSelDict[3]['value'], clearable = False
            ),
            html.P('Include Close outermost regions', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='outerCheck',
                options=[
                    {'label': 'Close Outermost Regions', 'value': 'OUTER_CLOSE'},
                    {'label': 'Outermost Regions', 'value': 'OUTERMOST_REGIONS'}

                ],
                value='OUTER_CLOSE'

            ),
            html.P('Select Destination Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='toSelection',
                options=toSelDict,
                value=toSelDict[3]['value'], clearable = True
            ),
            html.P('Select Market Segment', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='marketSelection',
                options=[{'label': i, 'value': i} for i in marketSelection], multi=True,
                value=['Traditional Scheduled', 'Lowcost'], clearable = False),
            html.P('Select Grouping option', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='groupSelection',
                options=groupByDict, multi=False,
                value='ADEP_COUNTRY', clearable=False),

            html.Div([
                html.Div([html.P('SAF Price(USD/kg)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="safPrice", type="number", placeholder=3.66, value=3.66, min=0, debounce=True), ]),
                html.Div([html.P('JetA1 Price(USD/kg)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="jetPrice", type="number", placeholder=0.61, value=0.61,min=0, debounce=True ), ]),
                html.Div([html.P('Blending (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="blendingMandate", type="number", placeholder=2, min=0, max=100, step=0.1, value=2,debounce=True ), ]),
                html.Div([html.P('Tax rate(EURO/GJ)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="taxRate", type="number", placeholder=2.15, min=0, max=10.75, step=1.075, value=2.15,debounce=True ), ]),
                html.Div([html.P('ETS Price(EURO/tn) ', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPrice", type="number", placeholder=62, min=0, max=1000, value=62,debounce=True ), ]),
                html.Div([html.P('Emissions (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPercent", type="number", placeholder=50, min=0, max=100, step=1, value=50, debounce=True), ]),
                html.Div([html.P('Projection Year', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="yearGDP", type="number", placeholder=2025, min=2021, max=2080, step=1, value=2025,debounce=True ), ]),
                html.Div([html.P('GDP Growth(%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="gdpGrowth", type="number", placeholder=1.09, min=-200, max=20, value=1.09, debounce=True), ]),
                dcc.Checklist(id="extrapolateRet", options=[{'label': 'Extrapolate Return Leg', 'value': 'Yes'}], value=['Yes'])

            ], style=dict(display='flex', flexWrap='wrap', width='auto')),

            html.P([]),
            html.Div([html.Button('Submit', style={"height": "auto", "margin-bottom": "20", "margin-top": "20"},
                                  id='submitButton'), ]),

        ],
            style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='Cost_graph',

            ),
            dcc.Graph(
                id='Gdp_graph',

            ),
            dcc.Dropdown(id='heatSel', multi=True, clearable=False,searchable=True),
            dcc.Graph(
                id='connHeatMap'
            ),
            dcc.Store(id='heatMapdf'),

            dash_table.DataTable(
                id='table',
                data=None,
                columns=None,
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="single",
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=100,
                export_format= 'csv'
            ),

            html.Div(id='datatable-interactivity-container')
        ], style={'width': '79%', 'float': 'right', 'display': 'inline-block'}),
    # signal value to trigger callbacks
    dcc.Store(id='signal')
    ], style={'padding': '10px 5px'}

)

application = app.server

@app.callback(
    [dash.dependencies.Output('Cost_graph', 'figure'),
     dash.dependencies.Output('Gdp_graph', 'figure'),
     dash.dependencies.Output('table', 'data'),
     dash.dependencies.Output('table', 'columns'),
     dash.dependencies.Output('heatSel', 'options'),
     dash.dependencies.Output('heatSel', 'value'),
     dash.dependencies.Output('heatMapdf', 'data')
     ],
    [dash.dependencies.State('monthSelection', 'value'),
     dash.dependencies.State('fromSelection', 'value'),
     dash.dependencies.State('toSelection', 'value'),
     dash.dependencies.State('marketSelection', 'value'),
     dash.dependencies.State('safPrice', 'value'),
     dash.dependencies.State('blendingMandate', 'value'),
     dash.dependencies.State('jetPrice', 'value'),
     dash.dependencies.State('taxRate', "value"),
     dash.dependencies.State('emissionsPercent', 'value'),
     dash.dependencies.State('emissionsPrice', 'value'),
     dash.dependencies.State('outerCheck', 'value'),
     dash.dependencies.State('DatasetSelection', 'value'),
     dash.dependencies.State('groupSelection', 'value'),
     dash.dependencies.State('yearGDP', 'value'),
     dash.dependencies.State('gdpGrowth' ,'value'),
     dash.dependencies.Input('submitButton', 'n_clicks'),
     dash.dependencies.State('extrapolateRet', 'value')

     ])
def update_graph(monthSel, fromSel, toSel, market, safPrice, blending, jetPrice, taxRate,
                 emissionsPercent, emissionsPrice, outerCheck, yearSelected, groupSel,
                 yearGDP, gdpGrowth, nclicks, extrapolateRet):

    if nclicks in [0, None]:
        raise PreventUpdate

    flights_df = finalDf
    flights_df = ft.CalculateSAFCost(flights_df, costOfSafFuelPerKg = safPrice, safBlendingMandate = blending/100 )
    flights_df = ft.CalculateFuelCost(flights_df, costOfJetFuelPerKg = jetPrice, safBlendingMandate = blending/100)
    flights_df = ft.CalculateTotalFuelCost(flights_df)
    flights_df = ft.CalculateTaxCost(flights_df, FuelTaxRateEurosPerGJ = taxRate, blendingMandate=blending/100 )
    flights_df = ft.CalculateETSCost(flights_df, safBlendingMandate=blending/100, ETSCostpertonne = emissionsPrice, ETSpercentage = emissionsPercent )

    flights_df['TOTAL_COST'] = flights_df['SAF_COST'] + flights_df['TAX_COST'] + flights_df['ETS_COST']

    #Build query based on input values
    if outerCheck=='OUTER_CLOSE':
        fromQuery = '(' + fromSel + ' | ' + '(ADEP_OUTER_CLOSE=="Y"))'
        # toQuery   = '(' + toSel + ' | ' + '(ADES_OUTER_CLOSE=="Y"))'
        toQuery = toSel
    elif outerCheck=='OUTERMOST_REGIONS':
        fromQuery = '(' + fromSel + ' | ' + '(ADEP_OUTERMOST_REGIONS=="Y"))'
        toQuery   = toSel
    else:
        fromQuery =  fromSel
        toQuery   = toSel

    if toSel:
        dfquery =  fromQuery  + ' & ' + toQuery + ' & ' 'not ((ADEP_OUTERMOST_REGIONS == "Y"  &  ADES_OUTERMOST_REGIONS == "Y" ))' + ' & ' + \
                  'STATFOR_Market_Segment in @market'
    else:
        dfquery = fromQuery + ' & ' 'not ((ADEP_OUTERMOST_REGIONS == "Y"  &  ADES_OUTERMOST_REGIONS == "Y" ))' + ' & ' + \
                  'STATFOR_Market_Segment in @market'

    ms_df_outermost=flights_df.query(dfquery)

    startSummerIATA, endSummerIATA = ft.getIATASeasons(yearSelected)

    dfRatio= ft.getDFRatio(set(monthSel))

    if groupSel=='ADEP_COUNTRY':
        countryPairsSummer_df = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
                ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        countryPairsSummer_df = countryPairsSummer_df * 7/dfRatio[0]

        countryPairsWinter_df = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
                ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        countryPairsWinter_df = countryPairsWinter_df * 5/dfRatio[1]

        countryPairTotal_df = countryPairsSummer_df + countryPairsWinter_df

    elif groupSel == 'ADEP':
        airportPairsSummer_df = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
                ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        airportPairsSummer_df = airportPairsSummer_df * 7/dfRatio[0]

        airportPairsWinter_df = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
                ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        airportPairsWinter_df = airportPairsWinter_df * 5/dfRatio[1]

        airportPairsTotal = airportPairsSummer_df + airportPairsWinter_df
    elif groupSel == 'AC_Operator':
        pass



    per_ms_summer_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby([groupSel])[['ECTRL_ID','FUEL', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'FUEL':'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std','sum'], 'TAX_COST': ['mean', 'std','sum'], 'ETS_COST': ['mean', 'std','sum'], 'TOTAL_COST': ['mean', 'std','sum']})
    per_ms_summer_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby([groupSel])[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')

    per_ms_summer_out = pd.concat([per_ms_summer_out, per_ms_summer_out_quantiles], axis=1)

    per_ms_winter_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby([groupSel])[['ECTRL_ID','FUEL', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size','FUEL':'sum', 'SAF_COST': ['mean', 'std','sum'], 'FUEL_COST': ['mean', 'std','sum'],
              'TOTAL_FUEL_COST': ['mean', 'std','sum'], 'TAX_COST': ['mean', 'std','sum'], 'ETS_COST': ['mean', 'std','sum'], 'TOTAL_COST': ['mean', 'std','sum']})

    per_ms_winter_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby([groupSel])[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')

    per_ms_winter_out = pd.concat([per_ms_winter_out, per_ms_winter_out_quantiles], axis=1)

    #divide by ratio of months per IATA season in dataset
    per_ms_summer_out.columns = ["_".join(a) for a in per_ms_summer_out.columns.to_flat_index()]
    per_ms_winter_out.columns = ["_".join(a) for a in per_ms_winter_out.columns.to_flat_index()]
    per_ms_summer_out.loc[:, ~per_ms_summer_out.columns.str.contains('mean|std|%')] = per_ms_summer_out.loc[:, ~per_ms_summer_out.columns.str.contains('mean|std|%')] / dfRatio[0]
    per_ms_winter_out.loc[:, ~per_ms_winter_out.columns.str.contains('mean|std|%')] = per_ms_winter_out.loc[:, ~per_ms_winter_out.columns.str.contains('mean|std|%')] / dfRatio[1]

    per_ms_Annual_out = ((per_ms_summer_out * 7) + (per_ms_winter_out * 5))
    #per_ms_Annual_out.columns = ["_".join(a) for a in per_ms_Annual_out.columns.to_flat_index()]
    per_ms_Annual_out.loc[:, per_ms_Annual_out.columns.str.contains('mean|std|%')] = per_ms_Annual_out.loc[:, per_ms_Annual_out.columns.str.contains('mean|std|%')] / 12


    #Calculate from selected region average
    sel_avg_quantiles_sum = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['FUEL','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_sum = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['FUEL','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].sum().reset_index(name='sum')

    selected_summer = sel_avg_quantiles_sum.T
    selected_summer['sum'] = (sel_avg_sum_sum.loc[:, 'sum']/dfRatio[0]).tolist()

    sel_avg_quantiles_win = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['FUEL','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_win = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['FUEL','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].sum().reset_index(name='sum')

    selected_winter = sel_avg_quantiles_win.T
    selected_winter['sum'] = (sel_avg_sum_win.loc[:, 'sum']/dfRatio[1]).tolist()

    sel_ms_Annual = ((selected_summer * 7) + (selected_winter * 5))
    sel_ms_Annual = sel_ms_Annual.drop(columns=['min', 'max'])

    sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] = sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] / 12

    per_ms_Annual_out.loc[defFromSelection] = (int(sel_ms_Annual.loc['SAF_COST', 'count']),
                                               sel_ms_Annual.loc['FUEL', 'sum'] ,
                                               sel_ms_Annual.loc['SAF_COST', 'mean'],
                                               sel_ms_Annual.loc['SAF_COST', 'std'],
                                               sel_ms_Annual.loc['SAF_COST', 'sum'],
                                               sel_ms_Annual.loc['FUEL_COST', 'mean'],
                                               sel_ms_Annual.loc['FUEL_COST', 'std'],
                                               sel_ms_Annual.loc['FUEL_COST', 'sum'],
                                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'mean'],
                                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'std'],
                                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'sum'],
                                               sel_ms_Annual.loc['TAX_COST', 'mean'],
                                               sel_ms_Annual.loc['TAX_COST', 'std'],
                                               sel_ms_Annual.loc['TAX_COST', 'sum'],
                                               sel_ms_Annual.loc['ETS_COST', 'mean'],
                                               sel_ms_Annual.loc['ETS_COST', 'std'],
                                               sel_ms_Annual.loc['ETS_COST', 'sum'],
                                               sel_ms_Annual.loc['TOTAL_COST', 'mean'],
                                               sel_ms_Annual.loc['TOTAL_COST', 'std'],
                                               sel_ms_Annual.loc['TOTAL_COST', 'sum'],
                                               sel_ms_Annual.loc['SAF_COST', '25%'],
                                               sel_ms_Annual.loc['SAF_COST', '50%'],
                                               sel_ms_Annual.loc['SAF_COST', '75%'],

                                               sel_ms_Annual.loc['TAX_COST', '25%'],
                                               sel_ms_Annual.loc['TAX_COST', '50%'],
                                               sel_ms_Annual.loc['TAX_COST', '75%'],

                                               sel_ms_Annual.loc['ETS_COST', '25%',],
                                               sel_ms_Annual.loc['ETS_COST', '50%',],
                                               sel_ms_Annual.loc['ETS_COST', '75%',]
                                               )

    app = dash.Dash(__name__)
    per_ms_Annual_out=per_ms_Annual_out.dropna()

    indexList =  per_ms_Annual_out.index.tolist()

    if outerCheck == 'OUTER_CLOSE' and groupSel=='ADEP_COUNTRY':
        if 'Canary Islands' in indexList:
            # Merge Spanish Outermost Regions
            multCa = per_ms_Annual_out.loc['Canary Islands', 'ECTRL_ID_size'] / \
                     (per_ms_Annual_out.loc['Canary Islands', 'ECTRL_ID_size'] + per_ms_Annual_out.loc['Spain', 'ECTRL_ID_size'])
            multSp = per_ms_Annual_out.loc['Spain', 'ECTRL_ID_size'] / \
                     (per_ms_Annual_out.loc['Canary Islands', 'ECTRL_ID_size'] + per_ms_Annual_out.loc['Spain', 'ECTRL_ID_size'])

            per_ms_Annual_out.loc['Spain', per_ms_Annual_out.columns.str.contains('mean|std|%')] = per_ms_Annual_out.loc['Spain', per_ms_Annual_out.columns.str.contains('mean|std|%')] * multSp
            caRow = per_ms_Annual_out.loc[['Canary Islands']]
            caRow.loc['Canary Islands', caRow.columns.str.contains('mean|std|%')] = caRow.loc['Canary Islands', caRow.columns.str.contains('mean|std|%')] * multCa
            per_ms_Annual_out.loc['Spain'] = per_ms_Annual_out.loc['Spain'] + caRow.loc['Canary Islands']

        if 'Azores' in indexList and 'Madeira' in indexList:
            # Merge Portugese Close regions
            multAz = per_ms_Annual_out.loc['Azores', 'ECTRL_ID_size'] / \
                     (per_ms_Annual_out.loc[['Azores', 'Madeira'], 'ECTRL_ID_size'].sum() + per_ms_Annual_out.loc['Portugal', 'ECTRL_ID_size'])
            multMa = per_ms_Annual_out.loc['Madeira', 'ECTRL_ID_size'] / \
                     (per_ms_Annual_out.loc[['Azores', 'Madeira'], 'ECTRL_ID_size'].sum() + per_ms_Annual_out.loc['Portugal', 'ECTRL_ID_size'])
            multPt = 1 - (multAz+multMa)

            per_ms_Annual_out.loc['Portugal', per_ms_Annual_out.columns.str.contains('mean|std|%')] = per_ms_Annual_out.loc['Portugal', per_ms_Annual_out.columns.str.contains('mean|std|%')] * multPt
            azmaRow = per_ms_Annual_out.loc[['Azores', 'Madeira']]

            azmaRow.loc['Azores', azmaRow.columns.str.contains('mean|std|%')] = azmaRow.loc['Azores', azmaRow.columns.str.contains('mean|std|%')] * multAz
            azmaRow.loc['Madeira', azmaRow.columns.str.contains('mean|std|%')] = azmaRow.loc['Madeira', azmaRow.columns.str.contains('mean|std|%')] * multMa
            per_ms_Annual_out.loc['Portugal'] = per_ms_Annual_out.loc['Portugal'] + azmaRow.loc['Azores'] + azmaRow.loc['Madeira']

    per_ms_Annual_out = per_ms_Annual_out.sort_values(by=['SAF_COST_mean'], ascending=False)
    per_ms_Annual_out = per_ms_Annual_out.round(2)
    per_ms_Annual_out['ECTRL_ID_size'] = per_ms_Annual_out['ECTRL_ID_size'].astype(int)
    per_ms_Annual_out = per_ms_Annual_out.rename(columns={'ECTRL_ID_size': 'Flights_size'})

    per_ms_Annual_out = per_ms_Annual_out.reset_index()

    gdpPerCountry = pd.read_csv('data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2916952.csv', usecols=['COUNTRY', '2016', '2017', '2018', '2019', '2020'], index_col='COUNTRY')

    gdpPerCountry[yearGDP] = gdpPerCountry['2020'] * (1+ gdpGrowth/100)**(yearGDP-2020)

    figpairs = None
    _cols = None
    heatSelOptions, heatSelValue, PairTotal_df = [], [], None
    if groupSel=='ADEP_COUNTRY':
        fig, figGDP, tab,_cols, figpairs, heatSelOptions, heatSelValue, PairTotal_df = update_per_ms(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out, yearGDP, countryPairTotal_df, extrapolateRet)
    elif groupSel=='ADEP':
        fig, figGDP, tab,_cols, figpairs,heatSelOptions, heatSelValue, PairTotal_df = update_per_airport(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out, yearGDP , airportPairsTotal)
    elif groupSel == 'AC_Operator':
        fig, figGDP, tab,_cols, figpairs = update_per_operator(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out, yearGDP)
    else:
        fig, figGDP , tab, figpairs = None,None, None, None

    if PairTotal_df is None:
        PairTotal_df = pd.DataFrame()

    PairTotal_df=PairTotal_df.to_json(date_format='iso', orient='split')

    #return fig,figGDP, tab, _cols, figpairs, heatSelOptions, heatSelValue, countryPairTotal_df.to_json(date_format='iso', orient='split')
    return fig, figGDP, tab, _cols, heatSelOptions, heatSelValue, PairTotal_df

def update_per_airport(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out, yearGDP, airportPairsTotal):

    data = [
        go.Bar(name='SAF',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Measures',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               )
    ]
    layout = go.Layout(
        barmode='stack',
        title='Average Cost per flight of Fit For 55 Proposals'
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(title_text='USD per Flight')

    #update table
    _col=[{"name": i, "id": i} for i in per_ms_Annual_out.columns]
    datatab=per_ms_Annual_out.to_dict('records')


    #update heatmap
    rowNames = airportPairsTotal.index.tolist()

    figPairs = px.imshow(airportPairsTotal, labels=dict(x="Destination Airport",  y='Departure Airport', color='Number of Flights'))
    heatSelOptions =[{'label': i, 'value': i} for i in rowNames]
    heatSelValue = [x['value'] for x in heatSelOptions][:10]

    return fig, go.Figure(data=[go.Scatter(x=[], y=[])]), datatab, _col, go.Figure(data=[go.Scatter(x=[], y=[])]) , heatSelOptions, heatSelValue, airportPairsTotal

def update_per_operator(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out, yearGDP):
    data = [
        go.Bar(name='SAF',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Measures',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               )
    ]
    layout = go.Layout(
        barmode='stack',
        title='Average Cost per flight of Fit For 55 Proposals'
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(title_text='USD per Flight')

    #update table
    _col=[{"name": i, "id": i} for i in per_ms_Annual_out.columns]
    datatab=per_ms_Annual_out.to_dict('records')

    return fig, go.Figure(data=[go.Scatter(x=[], y=[])]), datatab, _col, go.Figure(data=[go.Scatter(x=[], y=[])])

def update_per_ms(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out, yearGDP , countryPair, extrapolateRet):
    countryList = regions_df.query(fromSel.replace('ADEP_', '')).loc[:, 'COUNTRY'].tolist()
    rowLoc = fromSel.replace('(ADEP_', '').replace('=="Y")', '')
    gdpPerCountry.loc[rowLoc] = gdpPerCountry[gdpPerCountry.index.isin(countryList)].sum().tolist()
    per_ms_Annual_gdp = per_ms_Annual_out.join(gdpPerCountry, on='ADEP_COUNTRY', how='inner')

    if 'Yes' in extrapolateRet:
        retMult = 2
    else:
        retMult = 1


    per_ms_Annual_gdp['TOTAL_GDP_RATIO'] = (per_ms_Annual_gdp['TOTAL_COST_sum']*retMult / per_ms_Annual_gdp[yearGDP]) * 100
    per_ms_Annual_gdp['SAF_GDP_RATIO'] = (per_ms_Annual_gdp['SAF_COST_sum']*retMult / per_ms_Annual_gdp[yearGDP]) * 100
    per_ms_Annual_gdp['ETS_GDP_RATIO'] = (per_ms_Annual_gdp['ETS_COST_sum']*retMult / per_ms_Annual_gdp[yearGDP]) * 100
    per_ms_Annual_gdp['TAX_GDP_RATIO'] = (per_ms_Annual_gdp['TAX_COST_sum']*retMult / per_ms_Annual_gdp[yearGDP]) * 100
    data = [
        go.Bar(name='SAF',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Measures',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               )
    ]
    layout = go.Layout(
        barmode='stack',
        title='Average Cost per flight of Fit For 55 Proposals'
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(title_text='USD per Flight')
    per_ms_Annual_gdp = per_ms_Annual_gdp.sort_values(by=['TOTAL_GDP_RATIO'], ascending=False)
    dataGDP = [
        go.Bar(name='SAF',
               x=per_ms_Annual_gdp['ADEP_COUNTRY'],
               y=per_ms_Annual_gdp['SAF_GDP_RATIO'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.4,
               offset=-0.4
               ),
        go.Bar(name='TAX',
               x=per_ms_Annual_gdp['ADEP_COUNTRY'],
               y=per_ms_Annual_gdp['TAX_GDP_RATIO'],
               width=0.4,
               offset=-0.4
               ),
        go.Bar(name='ETS',
               x=per_ms_Annual_gdp['ADEP_COUNTRY'],
               y=per_ms_Annual_gdp['ETS_GDP_RATIO'],
               width=0.4,
               offset=-0.4
               ),
        go.Bar(name='Total GDP Ratio of Measures',
               x=per_ms_Annual_gdp['ADEP_COUNTRY'],
               y=per_ms_Annual_gdp['TOTAL_GDP_RATIO'], visible='legendonly',
               width=0.4,
               offset=0.0,
               base=0
               )
    ]
    layoutGDP = go.Layout(
        barmode='stack',
        title='Burden on GDP of Fit For 55 Proposals'
    )
    figGDP = go.Figure(data=dataGDP, layout=layoutGDP)
    figGDP.update_yaxes(title_text='Burden on GDP(%)')


    #update table
    _col=[{"name": i, "id": i} for i in per_ms_Annual_out.columns]
    datatab=per_ms_Annual_out.to_dict('records')

    #update heatmap
    rowNames = countryPair.index.tolist()
    colNames = countryPair.columns.tolist()
    for rowName in rowNames:
        if rowName in colNames:
            countryPair.loc[rowName, rowName] = 0

    figPairs = px.imshow(countryPair, labels=dict(x="Destination Country",  y='Departure Country', color='Number of Flights'))
    heatSelOptions =[{'label': i, 'value': i} for i in rowNames]
    heatSelValue = [x['value'] for x in heatSelOptions][:10]

    return fig, figGDP, datatab, _col, figPairs, heatSelOptions, heatSelValue, countryPair

@app.callback(
    dash.dependencies.Output("connHeatMap", "figure"),
    [dash.dependencies.Input("heatSel", "value"),
     dash.dependencies.State('heatMapdf', 'data')])
def filter_heatmap(cols, jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return go.Figure(data=[go.Scatter(x=[], y=[])])

    dff = pd.read_json(jsonified_cleaned_data, orient='split')
    if dff.empty is True:
        return go.Figure(data=[go.Scatter(x=[], y=[])])

    colset=set(cols)
    dffcols = set(dff.columns)
    finalCols = list(colset.intersection(dffcols))
    newdf = dff.loc[cols,finalCols]
    newdf = newdf.dropna(axis=1)
    fig = px.imshow(newdf)

    return fig


app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-7SVRF3W4H8"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-7SVRF3W4H8');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta property="og:type" content="article">
        <meta property="og:title" content="Air Transport Fit55 Dashboard"">
        <meta property="og:site_name" content="http://fit55.cyatcu.org">
        <meta property="og:url" content="http://fit55.cyatcu.org">
        <meta property="article:published_time" content="2020-11-01">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

if __name__ == '__main__':
   #app.run_server(debug=True)
   application.run()
