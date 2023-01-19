import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    [html.H1("Client-centered care-EDA")],
                    width=9,
                ),
            ]
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(port=8051)
