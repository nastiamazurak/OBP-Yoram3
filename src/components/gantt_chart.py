# -*- coding: utf-8 -*-
import plotly.graph_objects as go

import dash
import pandas as pd

# from IPython.core.display_functions import display
from dash import dcc
from dash import html, Dash, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from utils import helpers as hp
import plotly.express as px
from utils import helpers as hp
import jsonpickle


def render(app: Dash) -> html.Div:
    @app.callback(
        Output("my_gantt", "children"),
        [Input("day_dropdown", "value"), Input("stored-data", "children")],
    )
    def update_first_graph(option_slctd, stored_data) -> html.Div:
        if stored_data is not None:
            data = jsonpickle.decode(stored_data)
            sol = data["sol"]
            nurses = data["nurses"]
            print("Not none!!!!")
            getTss = hp.get_nurse_shifts(sol, nurses)

            if option_slctd != "Weekly overview":
                getTss = getTss[getTss["day"] == option_slctd]
                getTss["start"] = pd.to_datetime(getTss["start"], format="%H:%M")
                getTss["finish"] = pd.to_datetime(getTss["finish"], format="%H:%M")
                fig = px.timeline(
                    getTss,
                    x_start="start",
                    x_end="finish",
                    y="task",
                    title="Daily Schedule",
                )
                fig.update_xaxes(tickformat="%H:%M")

                fig.update_layout(autosize=False, width=1400, height=500)

                return html.Div(dcc.Graph(figure=fig), id="my_gantt")

    return html.Div(id="my_gantt")
