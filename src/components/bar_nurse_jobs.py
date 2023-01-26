# -*- coding: utf-8 -*-
import plotly.graph_objects as go

import dash

# from IPython.core.display_functions import display
from dash import dcc, callback
from dash import html, Dash, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from utils import helpers as hp
import plotly.express as px
import pandas as pd


bar_nurse_jobs = html.Div(id="my_first_barchart")


@callback(
    Output("my_first_barchart", "children"),
    [Input("day_dropdown", "value")],
)
def update_first_graph(option_slctd) -> html.Div:
    dff = hp.get_nurse_jobs()
    if option_slctd == "Weekly overview":
        weekly = dff.groupby(["client_id"])["Nurses"].nunique()
        weekly = weekly.reset_index()
        weekly = pd.DataFrame(weekly).reset_index()

        fig = px.bar(weekly, x="client_id", y="Nurses")
        fig.update_layout(autosize=False, width=1000, height=500)

        return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

    else:
        dff = dff[dff["day"] == option_slctd]
        fig = px.bar(dff, x="client_id", y="Nurses")
        fig.update_layout(autosize=False, width=1000, height=500)
        return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")


# def render(app: Dash) -> html.Div:
#     @app.callback(
#         Output("my_first_barchart", "children"),
#         [Input("day_dropdown", "value")],
#     )
#     def update_first_graph(option_slctd) -> html.Div:
#         dff = hp.get_nurse_jobs()
#         if option_slctd == "Weekly overview":
#             weekly = dff.groupby(["client_id"])["Nurses"].nunique()
#             weekly = weekly.reset_index()
#             weekly = pd.DataFrame(weekly).reset_index()

#             fig = px.bar(weekly, x="client_id", y="Nurses")
#             fig.update_layout(autosize=False, width=1000, height=500)

#             return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

#         else:
#             dff = dff[dff["day"] == option_slctd]
#             fig = px.bar(dff, x="client_id", y="Nurses")
#             fig.update_layout(autosize=False, width=1000, height=500)
#             return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

#     return html.Div(id="my_first_barchart")
