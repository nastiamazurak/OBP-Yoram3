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
from utils import helpers as hp

# button_id = "submit-button"
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
                    id="input-nurses",
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
                dbc.Button("Submit", id="submit-inputs", n_clicks=0),
                html.Div(id="hidden-output"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


@callback(
    Output("output-datatable-info", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(contents, filename):
    content_string = contents.split(",")[1]
    decoded = base64.b64decode(content_string)
    hp.save_file(decoded)
    return html.Div([html.H5(filename)])


@callback(
    Output("suggested-nurses", "children"), Input("output-datatable-info", "children")
)
def update_output_nurses(*vals):
    if hp.check_if_saved:
        return html.H6(
            "Suggested number of nurses: " + str(hp.get_suggested_number_of_nurses())
        )
    else:
        return html.H5("Please, load the file again.")


@callback(Output("hidden-output", "children"), Input("submit-inputs", "n_clicks"))
def submit_input(n_clicks):
    if n_clicks > 0:
        sol, nurses = hp.run_algorithms()
        return dcc.Store(sol, nurses)


# @callback(Output("not-used-output", "children"), Input("submit-inputs", "n_clicks"))
# def submit_input(n_clicks):
#     print(n_clicks)
#     if n_clicks > 0:
#         # sol, nurses = hp.run_algorithms()
#         # print(sol, nurses)
#         # return [dcc.Store(sol, nurses), html.H6("Heeeey")]
#         return html.H6("The button was clicked.")
