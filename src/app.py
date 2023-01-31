import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc

# local imports
# from components import sidebar as sb
from components.sidebar import sidebar
from components.dropdown_menu import dropdown_menu
from components.loading_bar import loading_bar
from components import bar_nurse_jobs as bnj
from components import gantt_chart as gantt
from components import hrs_worked as hrs
from components import time_shifts as ts


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(sidebar, width=3),
                dbc.Col(
                    [
                        html.H1("Client-centered care"),
                        loading_bar,
                        dropdown_menu,
                        dcc.Store(id="stored-data", data={}),
                        gantt.render(app),
                        bnj.render(app),
                        html.Div(
                            [hrs.render(app), ts.render(app)], style={"display": "flex"}
                        ),
                    ],
                    width=9,
                ),
            ]
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(port=8054)
