from maindash import app
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_html_components as html

def make_layout():
    app.layout = html.Div([

        # first row
        html.Div(children=[

            # first column of first row
            html.Div(children=[

                dcc.RadioItems(id='radio-item-1',
                               options=[dict(label='option A', value='A'),
                                        dict(label='option B', value='B'),
                                        dict(label='option C', value='C')],
                               value='A',
                               labelStyle={'display': 'block'}),

                html.P(id='text-1',
                       children='First paragraph'),

            ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'}),

            # second column of first row
            html.Div(children=[

                dcc.RadioItems(id='radio-item-2',
                               options=[dict(label='option 1', value='1'),
                                        dict(label='option 2', value='2'),
                                        dict(label='option 3', value='3')],
                               value='1',
                               labelStyle={'display': 'block'}),

                html.P(id='text-2',
                       children='Second paragraph'),

            ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'}),

            # third column of first row
            html.Div(children=[

                html.Div(dcc.Graph(id='main-graph',
                                   figure=figure)),

            ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'}),

        ], className='row'),

        # second row
        html.Div(children=[

            html.Div(dash_table.DataTable(id='main-table',
                                          columns=[{"name": i, "id": i} for i in df.columns],
                                          data=df.to_dict('records'),
                                          style_table={'margin-left': '3vw', 'margin-top': '3vw'})),

        ], className='row'),

    ])
    return app.layout



@app.callback(Output(component_id='my-div', component_property='children'),
              [Input(component_id='costOfSaf', component_property='value')])
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)