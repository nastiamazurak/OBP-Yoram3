import dash
from dash import html, callback, dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc
import time
import jsonpickle

from utils import helpers as hp

loading_bar = html.Div([html.Div(id="output-text"), dcc.Loading(id="loading")])


@callback(Output("output-text", "children"), Input("submit-inputs", "n_clicks"))
def run_algorithm(n_clicks):
    if n_clicks > 0:
        return "Algorithm is running..."


@callback(
    Output("loading", "children"),
    Input("submit-inputs", "n_clicks"),
    State("stored-data", "children"),
    # State("error-message", "children"),
)
def run_loading(n_clicks, stored_data):
    if n_clicks > 0:
        while stored_data is None:
            time.sleep(0.2)

        # replace with your actual algorithm


@callback(
    Output("output-text", "style"),
    [Input("stored-data", "children")],
    State("error-message", "children"),
)
def hide_text(stored_data, error_message):
    if stored_data is not None or error_message is not None:
        return {"display": "none"}


@callback(
    Output("loading", "style"),
    Input("stored-data", "children"),
    State("error-message", "children"),
)
def hide_loading(stored_data, error_message):
    if stored_data is not None or error_message is not None:
        return {"display": "none"}
