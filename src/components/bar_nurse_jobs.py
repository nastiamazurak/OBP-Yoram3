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
import jsonpickle


def render(app: Dash) -> html.Div:
    @app.callback(
        Output("my_first_barchart", "children"),
        [Input("day_dropdown", "value"), Input("stored-data", "children")],
    )
    def update_first_graph(option_slctd, stored_data) -> html.Div:
        if stored_data is not None:
            data = jsonpickle.decode(stored_data)
            sol = data["sol"]
            nurses = data["nurses"]
            schedule = data["schedule"]
            print("Not none!!!!")
            dff = hp.get_nurse_shifts(sol, nurses, schedule)
            dff2 = hp.get_nurse_jobs(sol, nurses)

            if option_slctd == "Weekly overview":
                weekly = dff.groupby(["client_id"])["nurse id"].nunique().reset_index()

                weekly["client_id"] = weekly["client_id"].astype(str)
                fig = px.bar(weekly, x="client_id", y="nurse id")
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=500,
                    title="Number of unique health professionals per client",
                    yaxis_title="Health professionals",
                    xaxis_title="Client id",
                )
                mean_val = round(weekly["nurse id"].mean(), 2)
                fig.add_annotation(
                    text=f"Mean nr of unique nurses: {mean_val}",
                    showarrow=False,
                    xanchor="left",
                    x=-1,
                    y=-0.12,
                )
                fig.update_layout(xaxis=dict(tickmode="linear"))

                return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

            else:
                dff2["day"] = dff2["day"].str.rstrip(")")
                dff2["client_id"] = dff2["client_id"].astype(str)
                dff2 = dff2[dff2["day"] == option_slctd]
                fig = px.bar(dff2, x="client_id", y="Nurses")
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=500,
                    title="Number of unique health professionals per client",
                    yaxis_title="Health professionals",
                    xaxis_title="Client id",
                )
                fig.update_layout(xaxis=dict(tickmode="linear"))

                mean_value = round(dff2["Nurses"].mean(), 2)
                fig.add_annotation(
                    text=f"Mean nr of unique nurses: {mean_value}",
                    showarrow=False,
                    xanchor="left",
                    x=-1,
                    y=-0.12,
                )
                return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

    return html.Div(id="my_first_barchart")
