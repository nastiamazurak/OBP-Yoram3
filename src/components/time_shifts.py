# -*- coding: utf-8 -*-
import plotly.graph_objects as go

import dash

# from IPython.core.display_functions import display
from dash import dcc
from dash import html, Dash, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from utils import helpers as hp
import plotly.express as px
import pandas as pd


def render(app: Dash) -> html.Div:
    @app.callback(
        Output("time_shifts_barchart", "children"),
        [Input("day_dropdown", "value")],
    )
    def update_time_shift_graph(option_slctd) -> html.Div:
        dff = hp.get_hrs_worked()
        if option_slctd != "Weekly overview":
            dff = dff[dff["day"] == option_slctd]

            fig = px.bar(dff, x="nurse_id", y="total_shift")
            fig.update_layout(autosize=False, width=500, height=500)

            return html.Div(dcc.Graph(figure=fig), id="time_shifts_barchart")

        else:
            shifts = dff.groupby("nurse_id")["total_shift"].sum()
            shifts = shifts.reset_index()
            shifts = pd.DataFrame(shifts).reset_index()

            fig = px.bar(shifts, x="nurse_id", y="total_shift")
            fig.update_layout(autosize=False, width=500, height=500)

            return html.Div(dcc.Graph(figure=fig), id="time_shifts_barchart")

    return html.Div(id="time_shifts_barchart")
