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
import jsonpickle


def render(app: Dash) -> html.Div:
    @app.callback(
        Output("box_hrs_worked", "children"),
        [Input("day_dropdown", "value"), Input("stored-data", "children")],
    )
    def update_first_graph(option_slctd, stored_data) -> html.Div:
        if stored_data is not None:
            data = jsonpickle.decode(stored_data)
            sol = data["sol"]
            nurses = data["nurses"]
            schedule = data["schedule"]
            print("Not none!!!!")
            dff = hp.get_hrs_worked(sol, nurses, schedule)
            if option_slctd != "Weekly overview":
                dff = dff[dff["day"] == option_slctd]

                fig = px.box(dff, y="total_shift", title="Nurse Work Time Distribution")
                fig.update_layout(
                    autosize=False, width=500, height=500, yaxis_title="Hours worked"
                )
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
                fig = px.box(
                    dff,
                    y="total_shift",
                    title="Nurse Work Time Distribution",
                )
                fig.update_layout(
                    autosize=False, width=500, height=500, yaxis_title="Hours worked"
                )
                mean_value = round(dff["total_shift"].mean(), 2)
                fig.add_annotation(
                    text=f"Mean nr hrs worked: {mean_value}",
                    showarrow=False,
                    xanchor="left",
                    x=-1,
                    y=-0.12,
                )
                return html.Div(dcc.Graph(figure=fig), id="box_hrs_worked")

    return html.Div(
        id="box_hrs_worked", style={"width": "100%", "display": "inline-block"}
    )
