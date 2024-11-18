import dash_bootstrap_components as dbc
from dash import html, dash_table


class DataCard(dbc.Card):
    def __init__(self, title, id, description=None):
        super().__init__(
            children=[
                html.Div(
                    [
                        html.H2(title, className="m-0 align-center"),
                    ],
                    className="d-flex justify-content-between align-center p-3",
                ),
                dbc.Spinner(
                    dash_table.DataTable(
                        id=id,
                        columns=[],  # Initialize with no columns
                        data=[],  # Initialize with no data
                        style_cell={"fontSize": 12},
                    ),
                    size="s",
                    color="dark",
                    delay_show=750,
                ),
            ],
            className="mb-3 figure-card shadow-sm small",
        )
