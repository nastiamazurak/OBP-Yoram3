import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import jsonpickle

import dash

# from IPython.core.display_functions import display
from dash import html, callback, dcc
from dash import html
from dash.dependencies import Input, Output, State
from utils import helpers as hp

# local imports

dropdown_menu = html.Div([html.Div(id="dropdown-menu"), html.Div(id="error-message")])

# Input("submit-inputs", "n_clicks")


@callback(
    Output("dropdown-menu", "children"),
    [Input("stored-data", "children")],
    State("error-message", "children"),
)
def show_menu(stored_data, error_message):
    if stored_data is not None and error_message == "":
        return dcc.Dropdown(
            id="day_dropdown",
            options=[
                # {"label": "Weekly Overview", "value": "Weekly Overview"},
                {"label": "Monday", "value": "monday"},
                {"label": "Tuesday", "value": "tuesday"},
                {"label": "Wednesday", "value": "wednesday"},
                {"label": "Thursday", "value": "thursday"},
                {"label": "Friday", "value": "friday"},
                {"label": "Saturday", "value": "saturday"},
                {"label": "Sunday", "value": "sunday"},
                {"label": "Weekly overview", "value": "Weekly overview"},
            ],
            multi=False,  # whether you can choose multiple options or not
            value="Weekly overview",
            style={"width": "40%"},
        )


@callback(
    Output("day_dropdown", "children"),
    Input("slct_day", "value"),
)
def update_output(input_value):
    return input_value
