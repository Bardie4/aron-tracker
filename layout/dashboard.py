import dash_bootstrap_components as dbc
from dash import dash_table
from .MetricCard import MetricCard
from .FigureCard import FigureCard
from .DataCard import DataCard

from dataclasses import dataclass

lg, md, sm, width = 2, 2, 4, 6


@dataclass
class MetricCardConfig:
    title: str
    id: str


@dataclass
class FigureCardConfig:
    title: str
    id: str
    description: str
    lg_size: int


metric_cards = [
    MetricCardConfig("I dag/Ideal", "consumed-count"),
    MetricCardConfig("Måltider i dag", "meals-count"),
    MetricCardConfig("Største måltid", "largest-count"),
    MetricCardConfig("Sist måltid", "last-meal"),
    MetricCardConfig("Tid siden måltid", "delta-last-meal"),
    MetricCardConfig("I bleien", "pee-poo"),
    MetricCardConfig("Foreslått måltid", "suggested-meal"),
    MetricCardConfig("Tid siden 🟤", "delta-last-poo"),
]

figure_cards = [
    FigureCardConfig(
        "Valgt dag", "today-graph", "Akkumulert konsummert morsmelkerstatning i dag.", 7
    ),
    FigureCardConfig(
        "Historisk",
        "history-graph",
        "Summert konsummert morsmelkerstatning per dag.",
        5,
    ),
]

dashboard = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            MetricCard(card.title, id=card.id),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        )
                        for card in metric_cards
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            FigureCard(
                                card.title, id=card.id, description=card.description
                            ),
                            lg=card.lg_size,
                            md=12,
                            sm=12,
                            width=12,
                        )
                        for card in figure_cards
                    ],
                    className="dashboard-row",
                ),
                dbc.Row([dbc.Col(DataCard("Data", id="selected-day-table"))]),
            ]
        )
    ],
    id="dashboard",
)
