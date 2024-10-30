import dash
import dash_bootstrap_components as dbc
from dash import html, dcc


class FigureCard(dbc.Card):
    def __init__(self, title, id, description=None):
        super().__init__(
            children=[
                html.Div(
                    [
                        html.H5(title, className="m-0 align-center"),
                    ],
                    className="d-flex justify-content-between align-center p-3",
                ),
                dbc.Spinner(
                    dcc.Graph(
                        id={"type": "graph", "index": id},
                        responsive=True,
                        style={"height": "450px"},
                    ),
                    size="lg",
                    color="dark",
                    delay_show=2000,
                ),
            ],
            className="mb-3 figure-card shadow",
        )