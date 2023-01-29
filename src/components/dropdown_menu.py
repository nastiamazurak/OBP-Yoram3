import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash

# from IPython.core.display_functions import display
from dash import html, callback, dcc
from dash import html
from dash.dependencies import Input, Output, State
from utils import helpers as hp

# local imports

dropdown_menu = html.Div(id="dropdown-menu")

# Input("submit-inputs", "n_clicks")


@callback(Output("dropdown-menu", "children"), Input("stored-data", "children"))
def show_menu(stored_data):
    if stored_data is not None:
        return dcc.Dropdown(
            id="day_dropdown",
            options=[
                # {"label": "Weekly Overview", "value": "Weekly Overview"},
                {"label": "Monday", "value": "monday"},
                {"label": "Tuesday", "value": "tuesday"},
                {"label": "Wednesday", "value": "wednesday"},
                {"label": "Thursday", "value": "thursday"},
                {"label": "Friday", "value": "friday"},
                {"label": "Saturday", "value": "saturday"},
                {"label": "Sunday", "value": "sunday"},
                {"label": "Weekly overview", "value": "Weekly overview"},
            ],
            multi=False,  # whether you can choose multiple options or not
            value="Weekly overview",
            style={"width": "40%"},
        )


@callback(
    Output("day_dropdown", "children"),
    Input("slct_day", "value"),
)
def update_output(input_value):
    return input_value


# def render(app: dash.Dash) -> html.Div:
#     @app.callback(
#         Output(component_id="day_dropdown", component_property="children"),
#         Input(button_id, "n_clicks"),
#         State(component_id="slct_day", component_property="value"),
#     )
#     def update_output(input_value, n_clicks):
#         if n_clicks is None:
#             return input_value
#         else:


# return html.Div(
#     children=[
#         html.H6("Select:"),
#         dcc.Dropdown(
#             id="day_dropdown",
#             options=[
#                 # {"label": "Weekly Overview", "value": "Weekly Overview"},
#                 {"label": "Monday", "value": "monday"},
#                 {"label": "Tuesday", "value": "tuesday"},
#                 {"label": "Wednesday", "value": "wednesday"},
#                 {"label": "Thursday", "value": "thursday"},
#                 {"label": "Friday", "value": "friday"},
#                 {"label": "Saturday", "value": "saturday"},
#                 {"label": "Sunday", "value": "sunday"},
#                 {"label": "Weekly overview", "value": "Weekly overview"},
#             ],
#             multi=False,  # whether you can choose multiple options or not
#             value="Weekly overview",
#             style={"width": "40%"},
#         )
#         # use dcc to make graph
#     ]
# )


# connect the Plotly graphs with Dash Components


# def render(app: Dash) -> html.Div:
#     @app.callback(
#        [Output(component_id='output_container', component_property='children')],
#         #[Output(component_id="my_first_barchart", component_property='figure')],
#         [Input(component_id='slct_day', component_property='value')]
#     ),
#     return html.Div([html.H1("Web Application to Show Client-Based Care", style={'text-align': 'center'}),
#             dcc.Dropdown(id="slct_day",
#                  options=[
#                     #{"label": "Weekly Overview", "value": "Weekly Overview"},
#                      {"label": "Monday", "value": "monday"},
#                      {"label": "Tuesday", "value": "tuesday"},
#                      {"label": "Wednesday", "value": "wednesday"},
#                      {"label": "Thursday", "value": "thursday"},
#                     {"label": "Friday", "value": "friday"},
#                     {"label": "Saturday", "value": "saturday"},
#                     {"label": "Sunday", "value": "sunday"},
#                      #{"label": "Weekly overview", "value": "Weekly overview"},
#                  ],
#                  multi=False, #whether you can choose multiple options or not
#                  value="Monday",
#                  style={'width': "40%"}
#                  ),
#                     ],)
