# spacex_dash_app.py

# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Determine the minimum and maximum payload mass for the RangeSlider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    # Application title
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Add a Launch Site Drop-down Input Component
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),
    
    # TASK 2: Add a callback function to render success-pie-chart based on selected site dropdown
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a Range Slider to Select Payload
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    
    html.Br(),
    html.Br(),
    
    # TASK 4: Add a callback function to render the success-payload-scatter-chart scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # If all sites are selected, show the total success counts for all sites
        fig = px.pie(spacex_df, names='Launch Site', values='class',
                     title='Total Successful Launches by Site')
    else:
        # Filter the dataframe for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Create a pie chart showing Success vs. Failure
        fig = px.pie(filtered_df, names='class', title=f'Total Launches for site {selected_site}',
                     labels={'class': 'Launch Outcome'},
                     category_orders={'class': [1, 0]},
                     color='class',
                     color_discrete_map={1: 'green', 0: 'red'})
    return fig

# TASK 4: Callback for Scatter Plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter the dataframe based on payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    if selected_site == 'ALL':
        filtered_df = spacex_df[mask]
        title = 'Correlation between Payload and Success for All Sites'
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) & mask]
        title = f'Correlation between Payload and Success for site {selected_site}'
    
    # Create a scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=title,
                     labels={'class': 'Launch Outcome'},
                     category_orders={'class': [1, 0]},
                     color_discrete_sequence=px.colors.qualitative.G10)
    fig.update_layout(yaxis=dict(tickvals=[0, 1], ticktext=['Failure', 'Success']))
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()