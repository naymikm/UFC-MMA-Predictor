"""
The UFC MMA Predictor Web App

author: Jason Chan Jin An
GitHub: www.github.com/jasonchanhku

"""

# Libraries used for Section 1
import pandas as pd
from sklearn.neural_network import MLPClassifier  # simple lightweight deep learning
import numpy as np
import plotly.graph_objs as go
# Libraries used for Section 2
import dash
import dash_core_components as dcc
import dash_html_components as html
import search_google.api
from dash.dependencies import Input, Output, State

# Section 1: Data loading and Machine Learning
# Make sure Machine Learning only run once
fights_db = pd.read_csv('/Users/jasonchan/PycharmProjects/UFC-MMA-Predictor/Datasets/Cleansed_Data.csv')

fighters_db = pd.read_csv('/Users/jasonchan/PycharmProjects/UFC-MMA-Predictor/Datasets/UFC_Fighters_Database.csv')

fighters_db = fighters_db[(fighters_db['TD'] != 0) & (fighters_db['Weight'] <= 265)]

fighters_db = fighters_db[(fighters_db['Weight'] == 115) | (fighters_db['Weight'] == 125)
                          | (fighters_db['Weight'] == 135) | (fighters_db['Weight'] == 140)
                          | (fighters_db['Weight'] == 145)
                          | (fighters_db['Weight'] == 155) | (fighters_db['Weight'] == 170)
                          | (fighters_db['Weight'] == 185) | (fighters_db['Weight'] == 205)
                          | (fighters_db['Weight'] > 205)]

inactive_fighters = ['Aleksander Emelianenko', 'AJ McKee', 'Aaron Ely', 'Alexandre Pantoja', 'Abongo Humphrey',
                     'Achmed Labasanov', 'Alex Stiebling', 'Adam Meredith', 'Akihiro Gono', 'Adam Cella']

fighters_db = fighters_db[-fighters_db['NAME'].isin(inactive_fighters)]

fighters = fighters_db['NAME']

# Manual sorting
weightclass = ['strawweight', 'flyweight', 'bantamweight', 'featherweight', 'lightweight', 'welterweight',
               'middleweight', 'lightheavyweight', 'heavyweight']

best_cols = ['SLPM_delta', 'SAPM_delta', 'STRD_delta', 'TD_delta', 'Odds_delta']

all_X = fights_db[best_cols]
all_y = fights_db['Label']

# This was the best model identified in the ipynb documentation
mlp = MLPClassifier(activation='tanh', alpha=0.0001, batch_size='auto', beta_1=0.9,
                    beta_2=0.999, early_stopping=False, epsilon=1e-08,
                    hidden_layer_sizes=(5, 5), learning_rate='constant',
                    learning_rate_init=0.001, max_iter=200, momentum=0.9,
                    nesterovs_momentum=True, power_t=0.5, random_state=1, shuffle=True,
                    solver='adam', tol=0.0001, validation_fraction=0.1, verbose=False,
                    warm_start=False)

mlp.fit(all_X, all_y)


def predict_outcome(data):
    prediction = mlp.predict_proba(data.reshape(1, -1))

    return prediction


#######################################################################################################################

# Section 2: Data Visualization Prep

# Columns to normalize
cols_norm = fighters_db.columns.tolist()[3:]


def normalize(df):
    result = df.copy()
    for feature_name in cols_norm:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result


fighters_db_normalize = normalize(fighters_db)

fighters_db_normalize = fighters_db_normalize.rename(columns={

    'SLPM': 'Striking <br> Volume',
    'SAPM': 'Damage <br> Taken',
    'STRA': 'Striking <br> Accuracy',
    'TDA': 'Wrestling',
    'SUBA': 'Submission'

})

select_cols = ['NAME', 'Striking <br> Volume', 'Damage <br> Taken', 'Striking <br> Accuracy', 'Wrestling', 'Submission']

fighters_db_normalize = fighters_db_normalize[select_cols]

col_y = fighters_db_normalize.columns.tolist()[1:]


#######################################################################################################################

# Section 3: Dash web app


def get_fighter_url(fighter):
    buildargs = {
        'serviceName': 'customsearch',
        'version': 'v1',
        'developerKey': 'AIzaSyAQACPWQ00cwV72F3YIOP70RqqkyZyBaUQ'
    }

    # Define cseargs for search
    cseargs = {
        'q': fighter + '' + 'Official Fighter Profile',
        'cx': '007364733105595844420:eu9ova5tqdg',
        'num': 1,
        'searchType': 'image',
        'imgType': 'clipart',
        'fileType': 'png',
        'safe': 'off'
    }

    # Create a results object
    results = search_google.api.results(buildargs, cseargs)
    url = results.links[0]

    if fighter == 'Max Holloway':
        url = 'https://media.ufc.tv/fighter_images/Max_Holloway/HOLLOWAY_MAX_BELT.png'
    elif fighter == 'Michael Bisping':
        url = 'https://media.ufc.tv/fighter_images/Michael_Bisping/BISPING_MICHAEL.png'

    return url


colors = {

    'background': '#F4F6F7',
    'text': '#34495E'

}

size = {
    'font': '20px'
}

app = dash.Dash()

app.layout = html.Div(style={'backgroundColor': colors['background'],
                             'backgroundImage': 'url(http://assets.fightland.com/content-images/'
                                                'contentimage/51034/NOTORIOUS.jpg)',
                             'backgroundRepeat': 'no-repeat',
                             'backgroundPosition': 'center top',
                             'backgroundSize': 'auto',
                             'height': '850px'
                             }, children=[

    html.H1(
        "UFC MMA Predictor v1.0",
        style={
            'textAlign': 'center'
        }
    ),

    html.H3(
        'Current Model Accuracy: 70.4%',
        style={
            'textAlign': 'center',
        }

    ),

    html.Div(style={'textAlign': 'center'}, children=[

        html.Div(style={'width': '30%', 'float': 'left', 'textAlign': 'left'}, children=[

            html.Label(
                'Favourite Fighter',
                style={
                    'textAlign': 'center',
                    'fontSize': '40px'

                }
            ),

            html.Label('Select Weightclass',

                       style={

                           'fontSize': size['font']

                       }

                       ),

            dcc.Dropdown(
                id='f1-weightclass',
                options=[{'label': i.capitalize(), 'value': i} for i in weightclass],
                value='welterweight'
            ),

            html.Br(),

            html.Label('Select Fighter',

                       style={

                           'fontSize': size['font']

                       }

                       ),

            dcc.Dropdown(
                id='f1-fighter'
            ),

            html.Br(),

            html.Label(
                'Select Odd Margin',
                style={
                    'fontSize': size['font'],
                    'textAlign': 'center'
                }
            ),

            html.Center(

                dcc.RadioItems(
                    id='f1-odds',
                    options=[{'label': i, 'value': i} for i in ['Big Favourite', 'Slight Favourite']],
                    value='Slight Favourite',
                    labelStyle={'display': 'inline-block'}
                    # inline block makes the buttons in one line horizontally rather than vertically
                )
            ),

            html.Br(),

            html.Center(

                html.Img(id='f1-image',
                         width='100%'
                         )
            )

        ]),

        html.Div(style={'width': '30%', 'float': 'right', 'textAlign': 'left'}, children=[

            html.Label(
                'Underdog Fighter',
                style={
                    'textAlign': 'center',
                    'fontSize': '40px'

                }
            ),

            html.Label('Select Weightclass',

                       style={

                           'fontSize': size['font']

                       }

                       ),

            dcc.Dropdown(
                id='f2-weightclass',
                options=[{'label': i.capitalize(), 'value': i} for i in weightclass],
                value='welterweight'
            ),

            html.Br(),

            html.Label('Select Fighter',

                       style={

                           'fontSize': size['font']
                       }

                       ),

            dcc.Dropdown(
                id='f2-fighter'
            ),

            html.Br(),

            html.Label(
                'Select Odd Margin',
                style={
                    'fontSize': size['font'],
                    'textAlign': 'center'
                }
            ),

            html.Center(
                dcc.RadioItems(
                    id='f2-odds',
                    options=[{'label': i, 'value': i} for i in ['Big Underdog', 'Slight Underdog']],
                    value='Slight Underdog',
                    labelStyle={'display': 'inline-block'}
                )
            ),

            html.Br(),

            html.Center(

                html.Img(id='f2-image',
                         src=get_fighter_url('Tony Ferguson'),
                         width='100%'
                         )
            )

        ]),

        html.Div(style={'width': '40%', 'marginLeft': 'auto', 'marginRight': 'auto', 'textAlign': 'left'

                        }, children=[

            dcc.Graph(
                id='fight-stats',
                config={'displayModeBar': False,
                        'staticPlot': True}

            ),

            html.Br(),

            html.Center(

                html.Button('Predict', id='button', style={

                    'fontSize': '32px',
                    'backgroundColor': 'rgba(255,255,255,0.8)'

                })
            ),

            html.Br(),

            html.Div(style={

                'width': '35%',
                'float': 'left',
                'textAlign': 'left',
                'backgroundColor': 'rgba(255,255,255,0.7)'

            },

                children=[

                    html.H2('Favourite', style=

                    {'textAlign': 'center',
                     'color': 'rgb(102, 0, 0)'}

                            ),

                    html.H3(children=['click \n predict'], id='f1-proba', style={'textAlign': 'center'})

                ]

            ),

            html.Div(style={

                'width': '35%',
                'float': 'right',
                'textAlign': 'left',
                'backgroundColor': 'rgba(255,255,255,0.7)'

            },

                children=[

                    html.H2('Underdog', style=

                    {'textAlign': 'center',
                     'color': 'rgb(0, 51, 102)'}

                            ),

                    html.H3(children=['click \n predict'], id='f2-proba', style={'textAlign': 'center'})

                ]

            )

        ]

                 )

    ]),

    html.Br(),

    html.Br()

])


# Decorators

# Update f1-fighter amd f2-fighter based on input from f1-weightclass and f2-weightclass

# Fighter 1


@app.callback(
    Output('f1-fighter', 'options'),
    [Input('f1-weightclass', 'value')]
)
def set_f1_fighter(weightclasses):
    return [{'label': i, 'value': i} for i in
            fighters_db[fighters_db['WeightClass'] == weightclasses]['NAME'].sort_values()]


@app.callback(
    Output('f1-fighter', 'value'),
    [Input('f1-fighter', 'options')]
)
def set_f1_fighter_value(options):
    return options[0]['value']


# Fighter 2


@app.callback(
    Output('f2-fighter', 'options'),
    [Input('f2-weightclass', 'value')]
)
def set_f1_fighter(weightclasses):
    return [{'label': i, 'value': i} for i in
            fighters_db[fighters_db['WeightClass'] == weightclasses]['NAME'].sort_values()]


@app.callback(
    Output('f2-fighter', 'value'),
    [Input('f2-fighter', 'options')]
)
def set_f1_fighter_value(options):
    return options[1]['value']


# Callback for change of picture

@app.callback(
    Output('f1-image', 'src'),
    [Input('f1-fighter', 'value')]
)
def set_image_f1(fighter1):
    if fighter1 == 'Aleksei Oleinik':
        fighter1 = 'Aleksei Oliynyk'

    return get_fighter_url(fighter1)


@app.callback(
    Output('f2-image', 'src'),
    [Input('f2-fighter', 'value')]
)
def set_image_f2(fighter2):
    if fighter2 == 'Aleksei Oleinik':
        fighter2 = 'Aleksei Oliynyk'

    return get_fighter_url(fighter2)


@app.callback(
    Output('fight-stats', 'figure'),
    [Input('f1-fighter', 'value'),
     Input('f2-fighter', 'value')]
)
def update_graph(f1, f2):
    f1_x = fighters_db_normalize[fighters_db_normalize['NAME'] == f1].iloc[0, :].values.tolist()[1:]
    f2_x = fighters_db_normalize[fighters_db_normalize['NAME'] == f2].iloc[0, :].values.tolist()[1:]

    trace1 = go.Bar(
        y=col_y,
        x=[x * -1 for x in f1_x],
        name=f1,
        orientation='h',
        hoverinfo='none',
        marker=dict(
            color='rgba(102, 0, 0, 0.8)',
            line=dict(
                color='rgba(102, 0, 0, 1.0)',
                width=3)
        )
    )
    trace2 = go.Bar(
        y=col_y,
        x=f2_x,
        name=f2,
        orientation='h',
        hoverinfo='none',
        marker=dict(
            color='rgba(0, 51, 102, 0.8)',
            line=dict(
                color='rgba(0, 51, 102, 1.0)',
                width=3)
        )
    )

    return {

        'data': [trace1, trace2],
        'layout': go.Layout(
            barmode='overlay',
            title='Fight Stats',
            titlefont={
                'size': 30
            },
            paper_bgcolor='rgba(255,255,255,0.7)',
            plot_bgcolor='rgba(255,255,255,0)',
            showlegend=False,
            xaxis=dict(
                showticklabels=False
            )
        )

    }


@app.callback(

    Output('f1-proba', 'children'),
    [Input('button', 'n_clicks')],
     state=[State('f1-fighter', 'value'),
     State('f2-fighter', 'value'),
     State('f1-odds', 'value'),
     State('f2-odds', 'value')]

)
def update_f1_proba(nclicks, f1, f2, f1_odds, f2_odds):

    if nclicks > 0:
        cols = ['SLPM', 'SAPM', 'STRD', 'TD']
        y = fighters_db[fighters_db['NAME'] == f1][cols].append(
            fighters_db[fighters_db['NAME'] == f2][cols], ignore_index=True)

        if (f1_odds == 'Big Favourite') & (f2_odds == 'Big Underdog'):
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -5.5)
        elif (f1_odds == 'Big Favourite') & (f2_odds == 'Slight Underdog'):
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -2.5)
        elif (f1_odds == 'Slight Favourite') & (f2_odds == 'Big Underdog'):
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -1.5)
        else:
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -0.1)

    return str(round(predict_outcome(delta_y)[0][0] * 100, 1)) + '%'


@app.callback(

    Output('f2-proba', 'children'),
    [Input('button', 'n_clicks')],
     state=[State('f1-fighter', 'value'),
     State('f2-fighter', 'value'),
     State('f1-odds', 'value'),
     State('f2-odds', 'value')]

)
def update_f2_proba(nclicks, f1, f2, f1_odds, f2_odds):

    if nclicks > 0:
        cols = ['SLPM', 'SAPM', 'STRD', 'TD']
        y = fighters_db[fighters_db['NAME'] == f1][cols].append(
            fighters_db[fighters_db['NAME'] == f2][cols], ignore_index=True)

        if (f1_odds == 'Big Favourite') & (f2_odds == 'Big Underdog'):
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -5.5)
        elif (f1_odds == 'Big Favourite') & (f2_odds == 'Slight Underdog'):
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -2.5)
        elif (f1_odds == 'Slight Favourite') & (f2_odds == 'Big Underdog'):
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -1.5)
        else:
            delta_y = np.append((y.loc[0] - y.loc[1]).reshape(1, -1), -0.1)

    return str(round(predict_outcome(delta_y)[0][1] * 100, 1)) + '%'


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == "__main__":
    app.run_server(debug=True)
