from logging import PlaceHolder
import os
# from dash_html_components.H2 import H2
import pandas as pd
import numpy as np
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import io
import requests
import schedule
import time
import json
import folium
from numpy import float64, int64


################################### DATA ###################################
############################################################################

urlx = "https://api.covid19india.org/csv/latest/case_time_series.csv"

i1=requests.get(urlx).content
India=pd.read_csv(io.StringIO(i1.decode('utf-8')))
India.drop(['Date'], axis= 1, inplace= True)
India.rename(columns={"Date_YMD": "Date", "Daily Deceased": "Daily_Deaths", "Total Deceased":"Total_Deaths", "Total Confirmed":"Total_Confirmed", "Total Recovered":"Total_Recovered",  "Daily Confirmed":"Daily_Confirmed",  "Daily Recovered":"Daily_Recovered",}, inplace= True)
India['Active'] = India['Total_Confirmed'] - India['Total_Recovered'] - India['Total_Deaths']

urly = "https://disease.sh/v3/covid-19/gov/India"
response = requests.get(urly)
resp = response.json()
state = ["India","Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh",
         "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir",
        "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", 
        "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
         "Uttarakhand", "Uttar Pradesh", "West Bengal"]
sactive = []
srecovered = []
sdeaths= []
scases = []
stodaycases = []
stodaydeaths = []
stodayrecovered = []

srecovered.append(resp['total']['recovered'])
sactive.append(resp['total']['active'])
sdeaths.append(resp['total']['deaths']) 
scases.append(resp['total']['cases'])
stodaycases.append(resp['total']['todayCases'])
stodaydeaths.append(resp['total']['todayDeaths'])
stodayrecovered.append(resp['total']['todayRecovered'])

for x in resp['states']:
    srecovered.append(x['recovered'])
    sactive.append(x['active'])
    sdeaths.append(x['deaths']) 
    scases.append(x['cases'])
    stodaycases.append(x['todayCases'])
    stodaydeaths.append(x['todayDeaths'])
    stodayrecovered.append(x['todayRecovered'])
  
State = pd.DataFrame()  
State['State'] = state
State['Daily Cases'] = stodaycases
State['Daily Deaths'] = stodaydeaths
State['Daily Recovered'] = stodayrecovered
State['Active'] = sactive
State['Total Cases'] = scases
State['Total Deaths'] = sdeaths
State['Total Recovered'] = srecovered


urla = "http://api.covid19india.org/csv/latest/cowin_vaccine_data_statewise.csv"


ia=requests.get(urla).content
VacState=pd.read_csv(io.StringIO(ia.decode('utf-8')), low_memory=False)
VacState.replace("", float("NaN"), inplace=True)
VacState.dropna(subset = ['Total Individuals Vaccinated'], inplace= True)
VacState.drop(['Sessions', ' Sites ', 'Total Individuals Vaccinated', 'AEFI'], axis = 1, inplace=True)
VacState.reset_index(inplace = True)
VacState.replace(float("NaN"), 0, inplace = True)
for col in VacState:
    if VacState[col].dtypes == float64:
        VacState[col] = VacState[col].astype(int64)
VacState.drop(['index'], axis=1, inplace=True)
VacState.rename(columns = {"Male (Doses Administered)":"Male", "Female (Doses Administered)":"Female", "Transgender (Doses Administered)":"Transgender",
                        " Covaxin (Doses Administered)" : "Covaxin", "CoviShield (Doses Administered)": "CoviShield", "Sputnik V (Doses Administered)":"Sputnik V",
                        "Total Doses Administered": "Total","First Dose Administered":"First Dose", "Second Dose Administered":"Second Dose",
                        "18-44 Years (Doses Administered)":"18-45", "45-60 Years (Doses Administered)":"45-60","60+ Years (Doses Administered)":"60+", "Updated On":"Date"}, inplace = True)
VacState['Date'] =  pd.to_datetime(VacState['Date'], infer_datetime_format=True)


urlb = "http://api.covid19india.org/csv/latest/cowin_vaccine_data_districtwise.csv"

ib=requests.get(urlb).content
VacDist=pd.read_csv(io.StringIO(ib.decode('utf-8')), low_memory=False)
VacDist.drop(['State_Code', 'State', 'District_Key', 'Cowin Key', 'S No'],axis = 1, inplace = True)
VacDist = VacDist.replace(np.nan, ' ', regex=True)
count=0
for i in VacDist.columns:
    if VacDist.iat[148,count] == ' ':
        VacDist.drop(VacDist.columns[[count]], axis=1,inplace=True)
        count-=1
    count+=1
VacDist.drop(VacDist.iloc[:, 1:count-10],axis = 1, inplace = True)
VacDist['District'][0] = 'District'
headers = VacDist.iloc[0]
VacDist  = pd.DataFrame(VacDist.values[1:], columns=headers)
VacDist.drop(['Total Sessions Conducted'], axis=1, inplace=True)
VacDist.drop(VacDist.columns[[2]], axis=1, inplace=True)
VacDist.rename(columns={"Total Individuals Vaccinated":"Total", "First Dose Administered":"First Dose", "Second Dose Administered":"Second Dose",
                       "Male(Doses Administered)":"Male", "Female(Doses Administered)":"Female", "Transgender(Doses Administered)":"Transgender",
                       "Total Covaxin Administered":"Covaxin","Total CoviShield Administered":"Covishield"}, inplace = True)
VacDist.sort_values(by = ['District'], inplace=True)
############################################################################


################################### SQL ####################################
############################################################################

# import sqlalchemy
# from sqlalchemy import create_engine


# engine = create_engine('mysql+pymysql://prateekp:prateekp@localhost/Dashboard')

# engine.execute("TRUNCATE TABLE India")
# India.to_sql("India", con = engine, if_exists = 'append', index = False)

# engine.execute("TRUNCATE TABLE State")
# State.to_sql("State", con = engine, if_exists = 'append', index = False)

############################################################################


################################### GRAPHS #################################
############################################################################

fig0 = px.bar(India
             ,x="Date"
             ,y="Daily_Confirmed"
             ,hover_data=['Daily_Confirmed']
             ,title="<b>Daily Cases</b>"
                ,labels = {
                    "Daily_Confirmed":""
                }
             ,width=800, height=400
              ,template='plotly_white')

fig1 = px.bar(India
             ,x="Date"
             ,y="Daily_Deaths"
             ,hover_data=['Daily_Deaths']
             ,title="<b>Daily Deaths</b>"
               ,labels = {
                    "Daily_Deaths":""
                }
             ,width=800, height=400
              ,template='plotly_white')
fig2 = px.bar(India
             ,x="Date"
             ,y="Daily_Recovered"
             ,hover_data=['Daily_Recovered']
             ,title="<b>Daily Recoverd</b>"
               ,labels = {
                    "Daily_Recovered":""
                }
             ,width=800, height=400
              ,template='plotly_white')
fig3 = px.bar(India
             ,x="Date"
             ,y="Total_Confirmed"
             ,hover_data=['Total_Confirmed']
             ,title="<b>Total Confirmed</b>"
               ,labels = {
                    "Total_Confirmed":""
                }
             ,width=800, height=400
              ,template='plotly_white')
fig4 = px.bar(India
             ,x="Date"
             ,y="Total_Recovered"
             ,hover_data=['Total_Recovered']
             ,title="<b>Total Recoverd</b>"
               ,labels = {
                    "Total_Recovered":""
                }
             ,width=800, height=400
              ,template='plotly_white')
fig5 = px.bar(India
             ,x="Date"
             ,y="Total_Deaths"
             ,hover_data=['Total_Deaths']
             ,title="<b>Total Deaths</b>"
               ,labels = {
                    "Total_Deaths":""
                }
             ,width=800, height=400
              ,template='plotly_white')
fig6 = px.bar(India
             ,x="Date"
             ,y="Active"
             ,hover_data=['Active']
             ,title="<b>Active Cases</b>"
               ,labels = {
                    "Active":""
                }
             ,width=800, height=400
              ,template='plotly_white')


############################################################################


##################################### MAPS ##################################
############################################################################


pd.set_option('display.max_rows', None)
distwiseurl = 'https://api.covid19india.org/csv/latest/districts.csv'
distcord = pd.read_csv('dist_cord.csv')
distcord.drop(['State'], axis =1, inplace = True)
d1=requests.get(distwiseurl).content
Dist1=pd.read_csv(io.StringIO(d1.decode('utf-8')))
n = len(Dist1)
datereq = Dist1['Date'].values[n-1]
Districts = Dist1[Dist1.Date == datereq]
# Districts = Districts[Districts.District != 'Unassigned']
Districts.drop(['Date', 'State', 'Other','Tested'], axis = 1, inplace = True)
Districts['Active'] = Districts['Confirmed']-Districts['Recovered']-Districts['Deceased']
# print(distcord)
# Districts.sort_values(by=['District'], ascending=True)
Districts = pd.merge(Districts, distcord, on="District")


OSMBright = r'https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.png'
import folium
mactive=folium.Map(location=[22.3905,81.8632], zoom_start=5, tiles=OSMBright,
            attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors')



def circle_maker(x):
    folium.Circle(location=[x[0],x[1]],
                 radius=float(x[2])*5,
                 color="red",
                  fill = "True",
                 popup='{}\n Active cases:{}'.format(x[3],x[2])).add_to(mactive)
Districts[['Latitude','Longitude','Active','District']].apply(lambda x:circle_maker(x),axis=1)
mactive.save('mactive.html')

mdeaths=folium.Map(location=[22.3905,81.8632], zoom_start=5, tiles=OSMBright,
            attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors')

def circle_maker(x):
    folium.Circle(location=[x[0],x[1]],
                 radius=float(x[2])*5,
                 color="grey",
                  fill = "True",
                 popup='{}\n Total Deaths:{}'.format(x[3],x[2])).add_to(mdeaths)
Districts[['Latitude','Longitude','Deceased','District']].apply(lambda x:circle_maker(x),axis=1)
mdeaths.save('mdeaths.html')

mcases=folium.Map(location=[22.3905,81.8632], zoom_start=5, tiles=OSMBright,
            attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors')

def circle_maker(x):
    folium.Circle(location=[x[0],x[1]],
                 radius=float(x[2])/5,
                 color="#3186cc",
                  fill = "True",
                 popup='{}\n Total Cases:{}'.format(x[3],x[2])).add_to(mcases)
Districts[['Latitude','Longitude','Confirmed','District']].apply(lambda x:circle_maker(x),axis=1)
mcases.save('mcases.html')

mrecovered=folium.Map(location=[22.3905,81.8632], zoom_start=5, tiles=OSMBright,
            attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors')


def circle_maker(x):
    folium.Circle(location=[x[0],x[1]],
                 radius=float(x[2])/5,
                 color="green",
                 fill = "True",
                 popup='{}\n Recovered:{}'.format(x[3],x[2])).add_to(mrecovered)
Districts[['Latitude','Longitude','Recovered','District']].apply(lambda x:circle_maker(x),axis=1)
mrecovered.save('mrecovered.html')

############################################################################
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
################################  PAGES   ##################################
############################################################################

dfmajorillness=pd.read_csv(r'C:\Users\Prateek Pandey\Documents\temp\dashboardproj\combine.csv',sep=',')


majorillness = dfmajorillness[['DATE', 'DEATHS_DUE_TO_MAJOR_ILLNESS', 'DEATHS_DUE_BOTH_COVID_MAJOR_ILLNESS','PREDICTED_DEATHS_DUE_MAJOR_ILLNESS_IF_COVID_NEVER_HAPPEN' ,'DEATH_DUE_TO_ROAD_ACCIDENTS','DEATHS_BOTH_COVID_AND_ACCIDENTS','PREDICTED_ACCIDENTS_IF_COVID_NEVER_HAPPENS']]

majorillness['totald'] = majorillness['PREDICTED_DEATHS_DUE_MAJOR_ILLNESS_IF_COVID_NEVER_HAPPEN']+majorillness['PREDICTED_DEATHS_DUE_MAJOR_ILLNESS_IF_COVID_NEVER_HAPPEN']
majorillness['totald2'] = majorillness['DEATHS_DUE_BOTH_COVID_MAJOR_ILLNESS']+majorillness['DEATHS_BOTH_COVID_AND_ACCIDENTS']
majorillness['totald3'] = majorillness['DEATHS_DUE_TO_MAJOR_ILLNESS']+majorillness['DEATH_DUE_TO_ROAD_ACCIDENTS']
# DEATHS_DUE_TO_MAJOR_ILLNESS= list(majorillness.DEATHS_DUE_TO_MAJOR_ILLNESS )
# DEATHS_DUE_BOTH_COVID_MAJOR_ILLNESS = list(majorillness.DEATHS_DUE_BOTH_COVID_MAJOR_ILLNESS)
# PREDICTED_DEATHS_DUE_MAJOR_ILLNESS_IF_COVID_NEVER_HAPPEN = list(majorillness.PREDICTED_DEATHS_DUE_MAJOR_ILLNESS_IF_COVID_NEVER_HAPPEN)
# DEATH_DUE_TO_ROAD_ACCIDENTS= list(majorillness.DEATH_DUE_TO_ROAD_ACCIDENTS )
# DEATHS_BOTH_COVID_AND_ACCIDENTS = list(majorillness.DEATHS_BOTH_COVID_AND_ACCIDENTS)
# PREDICTED_ACCIDENTS_IF_COVID_NEVER_HAPPENS = list(majorillness.PREDICTED_ACCIDENTS_IF_COVID_NEVER_HAPPENS)
fig20 = go.Figure()
fig20.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['totald'],
                    mode='lines',
                    name='predicted deaths due to major illnesses and accidents'))
fig20.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['totald2'],
                    mode='lines',
                    name='due to both corona,major illness and accidents'))
fig20.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['totald3'],
                    mode='lines',
                    name='Due to major illness and accdents')),
fig20.add_hline(y=0.63, line_width=3, line_dash="dash", annotation_text="Total Death Rate- India", line_color="red")
fig20.add_vline(x=24, line_width=3, line_dash="dash", line_color="green",annotation_text="Start of corona virus",annotation_position="top left",)                                  
fig20.update_layout(title='Death Rate (Monthly)',
                xaxis_title='Date',
                yaxis_title='DEATHS',
                template="plotly_white",
                legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1))

fig16 = go.Figure()
fig16.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['PREDICTED_DEATHS_DUE_MAJOR_ILLNESS_IF_COVID_NEVER_HAPPEN'],
                    mode='lines',
                    name='Predicted deaths due to major illnesses if corona never happened'))
fig16.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['DEATHS_DUE_BOTH_COVID_MAJOR_ILLNESS'],
                    mode='lines',
                    name='due to both corona and major illness'))
fig16.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['DEATHS_DUE_TO_MAJOR_ILLNESS'],
                    mode='lines',
                    name='Due to major illness')),
fig16.add_vline(x=24, line_width=3, line_dash="dash", line_color="green",annotation_text="Start of corona virus",annotation_position="top left",)                                  
fig16.update_layout(title='Death Rate (Monthly)',
                xaxis_title='Date',
                yaxis_title='DEATHS',
                template="plotly_white",
                legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1))
fig17 = go.Figure()
fig17.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['PREDICTED_ACCIDENTS_IF_COVID_NEVER_HAPPENS'],
                    mode='lines',
                    name='Predicted Accidental Deaths if corona never happened'))
fig17.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['DEATHS_BOTH_COVID_AND_ACCIDENTS'],
                    mode='lines',
                    name='Due to both accidents and corona'))
fig17.add_trace( go.Scatter(x=majorillness['DATE'], y=majorillness['DEATH_DUE_TO_ROAD_ACCIDENTS'],
                    mode='lines',
                    name='Due to road accidents')),
fig17.add_vline(x=24, line_width=3, line_dash="dash", line_color="green",annotation_text="Start of corona virus",annotation_position="top left",)                                  
fig17.update_layout(title='Death Rate (Monthly)',
                xaxis_title='Date',
                yaxis_title='DEATHS',
                template="plotly_white",
                legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))


homepage = html.Div([
    html.H1("Welcome to COVID-19 Dashboard", style= {"text-align":"center", "block":"inline-block","margin":"2%", "padding":"2%"}),
    html.P(""),
    html.Div(children=[
        dcc.Graph(
            figure=fig20,
            style={"display": "inline-block", "margin":"3%", "width": "100%"}
        ),
        dcc.Graph(
            figure=fig16,
            style={"display": "inline-block", "margin":"3%", "width": "100%"}
        ),
        dcc.Graph(
            figure=fig17,
            style={"display": "inline-block", "margin":"3%", "width": "100%"}
        )
    ],style={ "margin":"2%", "display": "inline-block"})
# ])
])


page1 = html.Div([
    html.Div([
        html.Div(dcc.Graph(
              figure=fig6,
              style={"display": "inline-block", "margin-left":"20%", "margin-right":"20%", "width": "60%"}
        )),
        html.Div([  
            html.Div([
                html.H2("Daily Parameters:"),
                dcc.Dropdown(
                    id='daily-dropdown',
                    options=[
                        {'label': 'Daily Cases', 'value': 'fig0'},
                        {'label': 'Daily Recovered', 'value': 'fig2'},
                        {'label': 'Daily Deaths', 'value': 'fig1'},
                    ],
                    value='fig0'
                ),
                html.Div(id='daily-graph')
            ],style={ "display": "inline-block", "margin-left":"20%", "margin-right":"20%", "width": "60%"}),
            html.Div([
                html.H2("Total Parameters:"),
                dcc.Dropdown(
                    id='total-dropdown',
                    options=[   
                        {'label': 'Total Cases', 'value': 'fig3'},
                        {'label': 'Total Recovred', 'value': 'fig4'},
                        {'label': 'Total Deaths', 'value': 'fig5'},
                    ],
                    value='fig3'
                ),
                html.Div(id='total-graph')
            ],style={ "display": "inline-block", "margin-left":"20%", "margin-right":"20%", "width": "60%"})
        ]),
        html.Hr(),
        html.Div([
            html.Div([

                dcc.RadioItems(
                    id='map-button',
                    labelStyle = {"display": "inline-block", "margin":"2%"},
                    options = [
                        {'label': 'Active Cases', 'value': 'mactive'},
                        {'label': 'Total Cases', 'value': 'mcases'},
                        {'label': 'Total Recovred', 'value': 'mrecovered'},
                        {'label': 'Total Deaths', 'value': 'mdeaths'},
                    ],
                    value = 'mactive',
                    style = {'text-align': 'center'}, className = 'dcc_compon'),
            ]),
            html.Div(id = 'map-draw') 
        ],style={ "margin":"2%"}),
        ],style={'padding-left': '2%', 'padding-right': '2%'})

])


page2 = html.Div(
    [   
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dbc.Card(
                        dbc.CardBody([
                            html.Div(dash_table.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i,} for i in (State.columns[0:-1])],
                            data=State.to_dict('records'),
                            style_cell = {
                                'background-color':'  #C0B7B4',
                                'border-radius':'12px',
                                'font-family': 'sans-serif',
                                'padding': '3px',
                                'width': '20px',
                                'height': '50px',
                                'font-size':'14px',
                                'overflow-x': 'hidden'
                             },
                            editable=True,
                            style_data={ 'border': '3px solid white' ,'color':'black','border-radius': '20px','text-align':'center','width':'30px'},
                            style_header={ 'border': '3px solid white' ,'backgroundColor': '#E0D9D8','border-radius': '13px','color':'black','text-align':'center','overflowY': 'auto',
                                'font-size':'15px',}, 
                            style_table= {
                                'color': '#666',
                                'font-weight':'20',
                                'padding-bottom': '10px',
                                'padding-top': '10px',
                                'width':'100%',
                                'height':'100%' ,
                                'border-radius': '25px',
                            },
                            sort_action="native",
                            sort_mode="multi",
                            page_action="native",
                            page_current= 0,
                            page_size= 40,
                            ))
                        ])
                    ),
                ]) 
            ]), color = 'white'
        )
    ])

page3 = html.Div([
    html.Div([
        html.Div([
            html.H2("Select a State:"),
            dcc.Dropdown(
                id='state-select',
                options=[{'label': state, 'value': state} for state in VacState['State'].unique()],
                value='Andaman and Nicobar Islands'
            ),
        ],style={ "margin":"2%", "display": "inline-block","margin-top":"2%"}),
        html.Div(id = 'selected-output'),
    ]),
    html.Div([
        html.Div([
            html.H2("Select a Dsitrict:"),
            dcc.Dropdown(
                id='dist-select',
                options=[{'label': dist, 'value': dist} for dist in VacDist['District'].unique()],
                value='New Delhi',
            ),
        ],style={ "margin":"2%", "display": "inline-block","margin-top":"2%"}),
        html.Div(id = 'dist-output')
    ]),
    
])



############################################################################


##############################  SIDEBAR   ##################################
############################################################################

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "15%",
    "padding": "2% 1%",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18%",
    "margin-right": "2%",
    "padding": "2% 1%",
}

sidebar = html.Div(
    [
        html.Img(
            src = app.get_asset_url('mask.png'),
            height = '200 px',
            width = 'auto'),
        html.Hr(),
        html.P(
            "A concise and efficient page for all Covid-19 status", className="lead"
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                html.Hr(),
                dbc.NavLink("COVID-19 India", href="/Covid19India", active="exact"),
                html.Hr(),
                dbc.NavLink("Covid-19 Statewise", href="/Covid19States", active="exact"),
                html.Hr(),
                dbc.NavLink("Vacccination Stats", href="/Covid19Vaccination", active="exact"),
                html.Hr(),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


############################################################################
content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return homepage
    elif pathname == "/Covid19India":
        return page1            
    elif pathname == "/Covid19States":
        return page2
    elif pathname == "/Covid19Vaccination":
        return page3
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(
    dash.dependencies.Output('daily-graph', 'children'),
    [dash.dependencies.Input('daily-dropdown', 'value')])
def update_output(value):
    X = fig0
    if value == 'fig0':
        X = fig0
    elif value == 'fig1':
        X = fig1
    elif value == 'fig2':
        X=fig2
    return html.Div([
        dbc.Card(
            dbc.CardBody([
            html.Div(dcc.Graph(
                figure=X,
                style={"display": "inline-block"}
                ))
            ])
        ),
    ])

@app.callback(
    dash.dependencies.Output('total-graph', 'children'),
    [dash.dependencies.Input('total-dropdown', 'value')])
def update_output(value):
    Y = fig3
    if value == 'fig3':
        Y = fig3
    elif value == 'fig4':
        Y = fig4
    elif value == 'fig5':
        Y = fig5
    return html.Div([
        dbc.Card(
            dbc.CardBody([
            html.Div(dcc.Graph(
                figure=Y,
                style={"display": "inline-block" }
                ))
            ])
        ),
    ])


@app.callback(
    dash.dependencies.Output('map-draw', 'children'),
    [dash.dependencies.Input('map-button', 'value')])
def update_output(value):
    htmllink = 'mactive.html'
    texth = "Active Cases"
    if value == 'mactive':
        htmllink = 'mactive.html'
        texth = "Active Cases"
    elif value == 'mdeaths':
        htmllink = 'mdeaths.html'
        texth = "Total Deaths"
    elif value == 'mrecovered':
        htmllink = 'mrecovered.html'
        texth = "Total Recovered"
    elif value == 'mcases':
        htmllink = 'mcases.html'
        texth = "Total Cases"
    return html.Div([
                html.Div([html.H2(texth),], style = {"text-align": "center"}),
                html.Iframe(id = 'map', srcDoc = open(htmllink,'r').read(),width = '60%', height = '850',style={ "margin-left":"18%","margin-right":"10%", "margin-top":"3%"}),
            ],style={"margin":"2%"})
    
@app.callback(
    dash.dependencies.Output('selected-output', 'children'),
    [dash.dependencies.Input('state-select', 'value')])
def page3_graphs(value):
    temp_df = VacState[VacState.State == value]
    # print(temp_df)
    fig0 = go.Figure()
    fig0.add_trace(go.Scatter(x = temp_df["Date"], y = temp_df["Total"], mode = 'lines', name = 'Total Doses Administered'))
    fig0.update_layout(title='Total Doses Administered',
                   xaxis_title='Date',
                   yaxis_title='Doses',
                   template="plotly_white")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['Male'],
                    mode='lines',
                    name='Male'))
    fig1.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['Female'],
                    mode='lines',
                    name='Female'))
    fig1.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['Transgender'],
                    mode='lines', name='Transgender'))
    fig1.update_layout(title='Doses Administered by Gender',
                   xaxis_title='Date',
                   yaxis_title='Doses',
                   template="plotly_white")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['CoviShield'],
                    mode='lines',
                    name='Covishield'))
    fig2.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['Covaxin'],
                    mode='lines',
                    name='Covaxin'))
    fig2.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['Sputnik V'],
                    mode='lines', name='Sputnik V'))
    fig2.update_layout(title='Doses Administered by Vaccine',
                   xaxis_title='Date',
                   yaxis_title='Doses',
                   template="plotly_white")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['18-45'],
                    mode='lines',
                    name='18-45 years'))
    fig3.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['45-60'],
                    mode='lines',
                    name='45-60 years'))
    fig3.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['60+'],
                    mode='lines', name='60+ years'))
    fig3.update_layout(title='Doses Administered by Age Group',
                   xaxis_title='Date',
                   yaxis_title='Doses',
                   template="plotly_white")

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['First Dose'],
                    mode='lines',
                    name='First Dose'))
    fig4.add_trace(go.Scatter(x=temp_df['Date'], y=temp_df['Second Dose'],
                    mode='lines',
                    name='Second Dose'))
    fig4.update_layout(title='Doses Administered by Dose',
                   xaxis_title='Date',
                   yaxis_title='Doses',
                   template="plotly_white")

    return html.Div(children = [
        dcc.Graph(figure=fig0, style={ "margin":"2%"}),
        dcc.Graph(figure=fig4, style={ "margin":"2%"}),
        dcc.Graph(figure=fig1, style={ "margin":"2%"}),
        dcc.Graph(figure=fig2, style={ "margin":"2%"}),
        dcc.Graph(figure=fig3, style={ "margin":"2%"}),
    ])


@app.callback(
    dash.dependencies.Output('dist-output', 'children'),
    [dash.dependencies.Input('dist-select', 'value')])
def page3_dist_graphs(value):
    row=0
    for i in VacDist['District']:
        if VacDist['District'][row]==value:
            break
        row+=1
    # params = [['Total','First Dose', 'Second Dose', 'Covishield', 'Covaxin', 'Male', 'Female', 'Transgender'],[VacDist['Total'][row],
    #             VacDist['First Dose'][row], VacDist['Second Dose'][row], VacDist['Covishield'][row], VacDist['Covaxin'][row],
    #             VacDist['Male'][row], VacDist['Female'][row], VacDist['Transgender'][row]]]
    c1 = ['Total','First Dose', 'Second Dose', 'Covishield', 'Covaxin', 'Male', 'Female', 'Transgender']
    c2 = [VacDist['Total'][row],VacDist['First Dose'][row], VacDist['Second Dose'][row], VacDist['Covishield'][row], VacDist['Covaxin'][row],
                VacDist['Male'][row], VacDist['Female'][row], VacDist['Transgender'][row]]
    df = pd.DataFrame()
    df['Parameters'] = c1
    df['Doses Administered'] = c2
    return html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} 
                 for i in df.columns],
            data=df.to_dict('records'),
            style_cell = {
                'background-color':'  #C0B7B4',
                'border-radius':'12px',
                'font-family': 'sans-serif',
                'padding': '3px',
                'width': '20px',
                'height': '50px',
                'font-size':'14px',
                'overflow-x': 'hidden'
            },
            style_data={ 'border': '3px solid white' ,'color':'black','border-radius': '20px','text-align':'center','width':'30px'},
            style_header={ 'border': '3px solid white' ,'backgroundColor': '#E0D9D8','border-radius': '13px','color':'black','text-align':'center','overflowY': 'auto',
                            'font-size':'15px',}, 
            style_table= {
                'color': '#666',
                'font-weight':'20',
                'padding-bottom': '10px',
                'padding-top': '10px',
                'width':'40%',
                'height':'100%' ,
                'border-radius': '25px',
            },
            page_action="native",
            page_current= 0,
            page_size= 40,
        )
    ])




if __name__ == "__main__":
    app.run_server()