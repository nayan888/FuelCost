import pandas as pd
import fueltools as ft
import preprocess as pp
import dash
from dash import dcc
from dash import html
from dash import dash_table
import plotly.graph_objects as go



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title='Fit for 55 Impact on Air Transport'

app.html_layout  = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-QNEGJ33FX3"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
        
          gtag('config', 'G-QNEGJ33FX3');
        </script>
        </head>
</html>"""
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


ms_df_outermost = flights_df[
    ((flights_df.ADEP_EU_EEA_EFTA_UK == 'Y') | (flights_df.ADEP_OUTER_CLOSE == 'Y')) &
    (flights_df.ADES_EU_EEA_EFTA_UK == 'Y') &
    ~((flights_df.ADEP_OUTER_CLOSE == 'Y') & (flights_df.ADES_OUTER_CLOSE == 'Y')) &
    (flights_df.STATFOR_Market_Segment.isin(['Lowcost', 'Traditional Scheduled']))]

startSummerIATA, endSummerIATA = ft.getIATASeasons(dataYear)

per_ms_summer_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
    .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','TOTAL_COST']] \
    .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
          'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum'] })
per_ms_summer_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
                                  .groupby(['ADEP_COUNTRY'])[['SAF_COST','TAX_COST', 'ETS_COST']] \
                                  .describe().filter(like='%')

per_ms_summer_out = pd.concat([per_ms_summer_out, per_ms_summer_out_quantiles], axis=1)

per_ms_winter_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
    .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','TOTAL_COST']] \
    .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
          'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']})

per_ms_winter_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
                                  .groupby(['ADEP_COUNTRY'])[['SAF_COST','TAX_COST', 'ETS_COST']] \
                                  .describe().filter(like='%')

per_ms_winter_out = pd.concat([per_ms_winter_out, per_ms_winter_out_quantiles], axis=1)

per_ms_Annual_out = ((per_ms_summer_out * 7) + (per_ms_winter_out * 5))
per_ms_Annual_out.columns = ["_".join(a) for a in per_ms_Annual_out.columns.to_flat_index()]
per_ms_Annual_out.loc[:, per_ms_Annual_out.columns.str.contains('mean|std|%')]=per_ms_Annual_out.loc[:, per_ms_Annual_out.columns.str.contains('mean|std|%')]/12


sel_avg_quantiles_sum = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST','TAX_COST', 'ETS_COST','TOTAL_COST']].describe()
sel_avg_sum_sum = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST','TAX_COST', 'ETS_COST','TOTAL_COST']].sum().reset_index(name ='sum')

selected_summer= sel_avg_quantiles_sum.T
selected_summer['sum'] = sel_avg_sum_sum.loc[:,'sum'].tolist()


sel_avg_quantiles_win = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] [['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST','TAX_COST', 'ETS_COST','TOTAL_COST']].describe()
sel_avg_sum_win = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
        ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] [['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST','TAX_COST', 'ETS_COST','TOTAL_COST']].sum().reset_index(name ='sum')

selected_winter= sel_avg_quantiles_win.T
selected_winter['sum'] = sel_avg_sum_win.loc[:,'sum'].tolist()

sel_ms_Annual = ((selected_summer * 7) + (selected_winter * 5))
sel_ms_Annual = sel_ms_Annual.drop(columns=['min', 'max'])

sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')]=sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')]/12

per_ms_Annual_out.loc[defFromSelection] = (int(sel_ms_Annual.loc[ 'SAF_COST','count']),
                               sel_ms_Annual.loc['SAF_COST',        'mean'],
                               sel_ms_Annual.loc['SAF_COST',        'std' ],
                               sel_ms_Annual.loc['SAF_COST',        'sum' ],
                               sel_ms_Annual.loc['FUEL_COST',       'mean'],
                               sel_ms_Annual.loc['FUEL_COST',       'std' ],
                               sel_ms_Annual.loc['FUEL_COST',       'sum' ],
                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'mean'],
                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'std' ],
                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'sum' ],
                               sel_ms_Annual.loc['TAX_COST',        'mean'],
                               sel_ms_Annual.loc['TAX_COST',        'std' ],
                               sel_ms_Annual.loc['TAX_COST',        'sum' ],
                               sel_ms_Annual.loc['ETS_COST',        'mean'],
                               sel_ms_Annual.loc['ETS_COST',        'std' ],
                               sel_ms_Annual.loc['ETS_COST',        'sum' ],
                               sel_ms_Annual.loc['TOTAL_COST',      'mean'],
                               sel_ms_Annual.loc['TOTAL_COST',      'std' ],
                               sel_ms_Annual.loc['TOTAL_COST',      'sum' ],
                               sel_ms_Annual.loc['SAF_COST',        '25%' ],
                               sel_ms_Annual.loc['SAF_COST',        '50%' ],
                               sel_ms_Annual.loc['SAF_COST',        '75%' ],

                               sel_ms_Annual.loc['TAX_COST',        '25%' ],
                               sel_ms_Annual.loc['TAX_COST',        '50%' ],
                               sel_ms_Annual.loc['TAX_COST',        '75%' ],

                               sel_ms_Annual.loc['ETS_COST',        '25%', ],
                               sel_ms_Annual.loc['ETS_COST',        '50%', ],
                               sel_ms_Annual.loc['ETS_COST',        '75%', ]
                               )

app = dash.Dash(__name__)


per_ms_Annual_out = per_ms_Annual_out.sort_values(by=['SAF_COST_mean'], ascending=False)
per_ms_Annual_out = per_ms_Annual_out.round(2)
per_ms_Annual_out['ECTRL_ID_size'] = per_ms_Annual_out['ECTRL_ID_size'].astype(int)
per_ms_Annual_out = per_ms_Annual_out.rename(columns={'ECTRL_ID_size': 'Flights_size'})
per_ms_Annual_out = per_ms_Annual_out.reset_index()

gdpPerCountry = pd.read_csv('data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2916952.csv',usecols=['COUNTRY','2016','2017','2018','2019'],index_col='COUNTRY')


countryList=regions_df.query( defFromSelection+'=="Y"').loc[:,'COUNTRY'].tolist()
gdpPerCountry.loc[defFromSelection] = gdpPerCountry[gdpPerCountry.index.isin(countryList)].sum().tolist()

per_ms_Annual_gdp=per_ms_Annual_out.join(gdpPerCountry, on='ADEP_COUNTRY',  how='inner')

per_ms_Annual_gdp['TOTAL_GDP_RATIO'] = (per_ms_Annual_gdp['TOTAL_COST_sum']*2/per_ms_Annual_gdp[str(dataYear)]) * 100
per_ms_Annual_gdp['SAF_GDP_RATIO'] = (per_ms_Annual_gdp['SAF_COST_sum']*2/per_ms_Annual_gdp[str(dataYear)]) * 100
per_ms_Annual_gdp['ETS_GDP_RATIO'] = (per_ms_Annual_gdp['ETS_COST_sum']*2/per_ms_Annual_gdp[str(dataYear)]) * 100
per_ms_Annual_gdp['TAX_GDP_RATIO'] = (per_ms_Annual_gdp['TAX_COST_sum']*2/per_ms_Annual_gdp[str(dataYear)]) * 100

dataSetSelection = ft.getYears()

dataSetPeriod = ft.getMonths()
dataSetPeriod.append('ALL')
extrapolateAnnual = True

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

marketSelection = flights_df.STATFOR_Market_Segment.unique().tolist()

data = [
    go.Bar(name='SAF',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['SAF_COST_mean'],
           #error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
           width=0.3,
           offset=-0.3
           ),
    go.Bar(name='TAX',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['TAX_COST_mean'],
           width=0.3,
           offset=-0.3
           ),
    go.Bar(name='ETS',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['ETS_COST_mean'],
           width=0.3,
           offset=-0.3
           ),
    go.Bar(name='JET A1',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly',
           width=0.3,
           offset=-0.3
           ),
    go.Bar(name='Total Fuel Cost',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly',
            width = 0.3,
            offset = 0.0,
            base=0
           ),
    go.Bar(name='Total Cost of Measures',
           x=per_ms_Annual_out['ADEP_COUNTRY'],
           y=per_ms_Annual_out['TOTAL_COST_mean'], visible='legendonly',
           width=0.3,
           offset=0.0,
           base=0
           )
]

per_ms_Annual_gdp = per_ms_Annual_gdp.sort_values(by=['TOTAL_GDP_RATIO'], ascending=False)
dataGDP = [
    go.Bar(name='SAF',
           x=per_ms_Annual_gdp['ADEP_COUNTRY'],
           y=per_ms_Annual_gdp['SAF_GDP_RATIO'],
           #error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
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


layout = go.Layout(
    barmode='stack',
    title='Average Cost per flight of Fit For 55 Proposals'
)

fig = go.Figure(data=data, layout=layout)
fig.update_yaxes(title_text='USD per Flight')

layoutGDP = go.Layout(
    barmode='stack',
    title='Burden on GDP of Fit for 55 Proposals'
)

figGDP = go.Figure(data=dataGDP, layout=layoutGDP)
figGDP.update_yaxes(title_text='Burden on GDP(%)')

app.layout = html.Div([
    html.Div([
        html.H1(children='Analysis of the Fit for 55 legislative proposals on Air Transport'),
    html.Div([
        html.P('Connect with me on: '),
        html.A(
            html.Img(src='assets/images/linkedin.png', className='img'),
            href='https://www.linkedin.com/in/eftychios-eftychiou-88686843/'
        ),
        html.A(
            html.Img(src='/assets/images/twitter.png', className='img'),
            href='https://twitter.com/EEftychiou'
        ),
        html.A(
            html.Img(src='/assets/images/github.png', className='img',
                     id='github'),
            href='https://github.com/eeftychiou'
        )
    ]), ],id='header-div'),


        html.Div([
            html.P('Select dataset', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='DatasetSelection',
                options=[{'label': i, 'value': i} for i in dataSetSelection],
                value=dataYear, disabled=False
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
                options=fromSelDict,
                value=fromSelDict[3]['value']
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
                value=toSelDict[3]['value']
            ),
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
                html.Div([html.P('ETS Price(EURO/tn) ', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPrice", type="number", placeholder=62, min=0, max=1000, step=1, value=62, ), ]),
                html.Div([html.P('Emissions (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPercent", type="number", placeholder=50, min=0, max=100, step=1, value=50, ), ]),

                html.Div([
                html.P('Include Standard Deviation Error Bars', style={"height": "auto", "margin-bottom": "auto"}),
                dcc.RadioItems(
                    id='errorBars',
                    options=[
                        {'label': 'Yes', 'value': 'errorBarsYes'},
                        {'label': 'No', 'value': 'errorBarsNo'}
                    ],
                    value='errorBarsNo',
                    labelStyle={'display': 'inline-block'}
                ),]),
            ], style=dict(display='flex', flexWrap='wrap', width='auto')),

            html.P([]),
            html.Div([html.Button('Submit', style={"height": "auto", "margin-bottom": "20", "margin-top": "20"},
                                  id='submitButton'), ]),

        ],
            style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='Cost_graph',
                figure=fig
            ),
            dcc.Graph(
                id='Gdp_graph',
                figure=figGDP
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
        ], style={'width': '79%', 'float': 'right', 'display': 'inline-block'}),
    # signal value to trigger callbacks
    dcc.Store(id='signal')
    ], style={'padding': '10px 5px'}

)

application = app.server

@app.callback(
    [dash.dependencies.Output('Cost_graph', 'figure'),
     dash.dependencies.Output('Gdp_graph', 'figure'),
    dash.dependencies.Output('table', 'data')],
    [dash.dependencies.Input('submitButton', 'n_clicks'),
     dash.dependencies.Input('fromSelection', 'value'),
     dash.dependencies.Input('toSelection', 'value'),
     dash.dependencies.Input('marketSelection', 'value'),
     dash.dependencies.Input('safPrice', 'value'),
     dash.dependencies.Input('blendingMandate', 'value'),
     dash.dependencies.Input('jetPrice', 'value'),
     dash.dependencies.Input('taxRate', "value"),
     dash.dependencies.Input('emissionsPercent', 'value'),
     dash.dependencies.Input('emissionsPrice', 'value'),
     dash.dependencies.Input('errorBars', 'value'),
     dash.dependencies.Input('outerCheck', 'value'),
     dash.dependencies.Input('DatasetSelection', 'value')

     ])
def update_graph(clicks, fromSel, toSel, market, safPrice, blending, jetPrice, taxRate, emissionsPercent, emissionsPrice, errorBars, outerCheck, yearSelected):


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

    per_ms_summer_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std','sum'], 'TAX_COST': ['mean', 'std','sum'], 'ETS_COST': ['mean', 'std','sum'], 'TOTAL_COST': ['mean', 'std','sum']})
    per_ms_summer_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby(['ADEP_COUNTRY'])[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')

    per_ms_summer_out = pd.concat([per_ms_summer_out, per_ms_summer_out_quantiles], axis=1)

    per_ms_winter_out = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby(['ADEP_COUNTRY'])[['ECTRL_ID', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'SAF_COST': ['mean', 'std','sum'], 'FUEL_COST': ['mean', 'std','sum'],
              'TOTAL_FUEL_COST': ['mean', 'std','sum'], 'TAX_COST': ['mean', 'std','sum'], 'ETS_COST': ['mean', 'std','sum'], 'TOTAL_COST': ['mean', 'std','sum']})

    per_ms_winter_out_quantiles = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby(['ADEP_COUNTRY'])[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')

    per_ms_winter_out = pd.concat([per_ms_winter_out, per_ms_winter_out_quantiles], axis=1)

    per_ms_Annual_out = ((per_ms_summer_out * 7) + (per_ms_winter_out * 5))
    per_ms_Annual_out.columns = ["_".join(a) for a in per_ms_Annual_out.columns.to_flat_index()]
    per_ms_Annual_out.loc[:, per_ms_Annual_out.columns.str.contains('mean|std|%')] = per_ms_Annual_out.loc[:, per_ms_Annual_out.columns.str.contains('mean|std|%')] / 12

    #Calculate from selected region average
    sel_avg_quantiles_sum = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_sum = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].sum().reset_index(name='sum')

    selected_summer = sel_avg_quantiles_sum.T
    selected_summer['sum'] = sel_avg_sum_sum.loc[:, 'sum'].tolist()

    sel_avg_quantiles_win = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_win = ms_df_outermost[(ms_df_outermost['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            ms_df_outermost['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].sum().reset_index(name='sum')

    selected_winter = sel_avg_quantiles_win.T
    selected_winter['sum'] = sel_avg_sum_win.loc[:, 'sum'].tolist()

    sel_ms_Annual = ((selected_summer * 7) + (selected_winter * 5))
    sel_ms_Annual = sel_ms_Annual.drop(columns=['min', 'max'])

    sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] = sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] / 12

    per_ms_Annual_out.loc[defFromSelection] = (int(sel_ms_Annual.loc['SAF_COST', 'count']),
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
    per_ms_Annual_out = per_ms_Annual_out.sort_values(by=['SAF_COST_mean'], ascending=False)
    per_ms_Annual_out = per_ms_Annual_out.round(2)
    per_ms_Annual_out['ECTRL_ID_size'] = per_ms_Annual_out['ECTRL_ID_size'].astype(int)
    per_ms_Annual_out = per_ms_Annual_out.rename(columns={'ECTRL_ID_size': 'Flights_size'})

    per_ms_Annual_out = per_ms_Annual_out.reset_index()

    gdpPerCountry = pd.read_csv('data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2916952.csv', usecols=['COUNTRY', '2016', '2017', '2018', '2019'], index_col='COUNTRY')

    countryList = regions_df.query(fromSel.replace('ADEP_', '' )).loc[:, 'COUNTRY'].tolist()
    rowLoc= fromSel.replace('(ADEP_', '' ).replace('=="Y")','')
    gdpPerCountry.loc[rowLoc] = gdpPerCountry[gdpPerCountry.index.isin(countryList)].sum().tolist()

    per_ms_Annual_gdp = per_ms_Annual_out.join(gdpPerCountry, on='ADEP_COUNTRY', how='inner')

    per_ms_Annual_gdp['TOTAL_GDP_RATIO'] = (per_ms_Annual_gdp['TOTAL_COST_sum'] * 2 / per_ms_Annual_gdp[str(dataYear)]) * 100
    per_ms_Annual_gdp['SAF_GDP_RATIO'] = (per_ms_Annual_gdp['SAF_COST_sum'] * 2 / per_ms_Annual_gdp[str(dataYear)]) * 100
    per_ms_Annual_gdp['ETS_GDP_RATIO'] = (per_ms_Annual_gdp['ETS_COST_sum'] * 2 / per_ms_Annual_gdp[str(dataYear)]) * 100
    per_ms_Annual_gdp['TAX_GDP_RATIO'] = (per_ms_Annual_gdp['TAX_COST_sum'] * 2 / per_ms_Annual_gdp[str(dataYear)]) * 100



    data = [
        go.Bar(name='SAF',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['SAF_COST_mean'],
               #error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly',
                width = 0.3,
                offset = 0.0,
                base = 0
               ),
        go.Bar(name='Total Cost of Measures',
               x=per_ms_Annual_out['ADEP_COUNTRY'],
               y=per_ms_Annual_out['TOTAL_COST_mean'], visible='legendonly',
               base = 0,
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


    tab=per_ms_Annual_out.to_dict('records')


    return fig,figGDP, tab




if __name__ == '__main__':
   #application.run(debug=True, port=8080)
   application.run()
