import json
import dash_bootstrap_components as dbc
from dash import html, dcc

from .MetricCard import MetricCard
from .FigureCard import FigureCard

dashboard = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(MetricCard("Totalt i dag", id="consumed-count"), lg=4, md=6, sm=12, width=12),
                        dbc.Col(MetricCard("Måltider i dag", id="meals-count"), lg=4, md=6, sm=12, width=12),
                        dbc.Col(MetricCard("Største måltid", id="largest-count"), lg=4, md=6, sm=12, width=12),
                        dbc.Col(MetricCard("Sist måltid", id="last-meal"), lg=4, md=6, sm=12, width=12),
                        dbc.Col(MetricCard("Tid siden måltid", id="delta-last-meal"), lg=4, md=6, sm=12, width=12),
                        dbc.Col(MetricCard("I bleien", id="pee-poo"), lg=4, md=6, sm=12, width=12),
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
                            lg=7, md=12, sm=12, width=12,
                        ),
                        dbc.Col(
                            FigureCard(
                                "Historisk",
                                id="history-graph",
                                description="Summert konsummert morsmelkerstatning per dag.",
                            ),
                            lg=5, md=12, sm=12, width=12,
                        ),
                    ],
                    className="dashboard-row",
                ),
            ],
        )
    ],
    id="dashboard",
)