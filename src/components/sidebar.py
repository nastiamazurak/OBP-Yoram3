"""
This file is for creating  a sidebar with Inputs.
This component will sit at the left side of the webpage.
"""

import base64
import datetime
import os
import io
import dash
from dash import html, callback, dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np

# local imports
from utils.helpers import save_file


SIDEBAR_STYLE = {
    "width": "100%",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        dbc.Nav(
            [
                html.H2("Inputs"),
                html.Hr(),
                html.P("Upload dataset:", className="lead"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select a File")]),
                    multiple=False,
                    style={
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "align": "center",
                    },
                ),
                html.Br(),
                html.Div(id="output-datatable-info"),
                html.Br(),
                html.P("Provide number of nurses:", className="lead"),
                html.Div(id="suggested-nurses"),
                dcc.Input(
                    id="nurses",
                    type="number",
                    placeholder="Enter a number",
                    style={
                        "height": "40px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderRadius": "5px",
                        "textAlign": "center",
                    },
                ),
                html.Br(),
                dbc.Button("Submit", id="submit-button", n_clicks=0),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    save_file(filename, decoded)
    return html.Div([html.H5(filename)])


@callback(
    Output("output-datatable-info", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)

# Rename passing variables
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children


# ## Figure out how to pass df and call function from utils
@callback(Output("suggested-nurses", "children"))
def suggest_nurses():
    from utils.functions import intial_nurse_number

    nurses = intial_nurse_number()
    return nurses


#     # call function to calculate # of nurses
#     #
#     return html.Div([html.H6("Suggested number of nurses: ")])
