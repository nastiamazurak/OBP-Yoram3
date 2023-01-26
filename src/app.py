import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc

# local imports
from components import sidebar as sb
from components import dropdown_menu as dm
from components import bar_nurse_jobs as bnj


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(sb.sidebar, width=3),
                dbc.Col(
                    [html.H1("Client-centered care"), dm.dropdown_menu],
                    width=9,
                ),
            ]
        ),
        dbc.Row([dbc.Col()]),
        # bnj.bar_nurse_jobs
    ]
)


if __name__ == "__main__":
    app.run_server(port=8052)
