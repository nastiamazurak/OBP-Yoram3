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


def render(app: Dash) -> html.Div:
    @app.callback(
        Output("box_hrs_worked", "children"),
        [Input("day_dropdown", "value")],
    )
    def update_first_graph(option_slctd) -> html.Div:
        dff = hp.get_hrs_worked()
        if option_slctd != "Weekly overview":
            dff = dff[dff["day"] == option_slctd]

            fig = px.box(dff, y="total_shift")
            fig.update_layout(autosize=False, width=500, height=500)
            mean_value = round(dff["total_shift"].mean(), 2)
            fig.add_annotation(
                text=f"Mean nr hrs worked: {mean_value}",
                showarrow=False,
                xanchor="left",
                x=-1,
                y=-0.12,
            )

            return html.Div(dcc.Graph(figure=fig), id="box_hrs_worked")
        else:
            fig = px.box(dff, y="total_shift")
            fig.update_layout(autosize=False, width=500, height=500)
            mean_value = round(dff["total_shift"].mean(), 2)
            fig.add_annotation(
                text=f"Mean nr hrs worked: {mean_value}",
                showarrow=False,
                xanchor="left",
                x=-1,
                y=-0.12,
            )
            return html.Div(dcc.Graph(figure=fig), id="box_hrs_worked")

    return html.Div(id="box_hrs_worked")
