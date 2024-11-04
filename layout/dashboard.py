import json
import dash_bootstrap_components as dbc
from dash import html, dcc

from .MetricCard import MetricCard
from .FigureCard import FigureCard

lg, md, sm = 2, 2, 4

dashboard = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(MetricCard("Totalt i dag", id="consumed-count"), lg=lg, md=md, sm=sm, width=6),
                        dbc.Col(MetricCard("Måltider i dag", id="meals-count"), lg=lg, md=md, sm=sm, width=6),
                        dbc.Col(MetricCard("Måltid ideal", id="largest-count"), lg=lg, md=md, sm=sm, width=6),
                        dbc.Col(MetricCard("Sist måltid", id="last-meal"), lg=lg, md=md, sm=sm, width=6),
                        dbc.Col(MetricCard("Tid siden måltid", id="delta-last-meal"), lg=lg, md=md, sm=sm, width=6),
                        dbc.Col(MetricCard("I bleien", id="pee-poo"), lg=lg, md=md, sm=sm, width=6),
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