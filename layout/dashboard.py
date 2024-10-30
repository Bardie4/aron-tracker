import json
import dash_bootstrap_components as dbc
from dash import html, dcc

from .MetricCard import MetricCard
from .FigureCard import FigureCard

dashboard = dbc.Row(
    dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(MetricCard("Totalt i dag", id="consumed-count"), width=4),
                    dbc.Col(MetricCard("Måltider i dag", id="meals-count"), width=4),
                    dbc.Col(MetricCard("Største måltid", id="largest-count"), width=4),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        FigureCard(
                            "Valgt dag",
                            id="today-graph",
                            description="Akkumulert konsummert morsmelkerstatning i dag.",
                        ),
                        sm=12,
                        md=7,
                    ),
                    dbc.Col(
                        FigureCard(
                            "Historisk",
                            id="history-graph",
                            description="Summert konsummert morsmelkerstatning per dag.",
                        ),
                        sm=12,
                        md=5,
                    ),
                ],
                className="dashboard-row",
            ),
        ],
    ),
    id="dashboard",
)