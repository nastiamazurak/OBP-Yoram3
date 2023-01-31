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
                fig = px.bar(weekly, x="client_id", y="nurse id")
                fig.update_layout(autosize=False, width=1000, height=500)

                return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

            else:
                dff2["day"] = dff2["day"].str.rstrip(")")
                dff2 = dff2[dff2["day"] == option_slctd]
                fig = px.bar(dff2, x="client_id", y="Nurses")
                fig.update_layout(autosize=False, width=1000, height=500)
                return html.Div(dcc.Graph(figure=fig), id="my_first_barchart")

    return html.Div(id="my_first_barchart")
