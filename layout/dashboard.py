import dash_bootstrap_components as dbc
from dash import dash_table
from .MetricCard import MetricCard
from .FigureCard import FigureCard

lg, md, sm, width = 2, 2, 4, 6

dashboard = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            MetricCard("I dag/Ideal", id="consumed-count"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("Måltider i dag", id="meals-count"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("Største måltid", id="largest-count"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("Sist måltid", id="last-meal"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("Tid siden måltid", id="delta-last-meal"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("I bleien", id="pee-poo"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("Foreslått måltid", id="suggested-meal"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
                        dbc.Col(
                            MetricCard("Tid siden 🟤", id="delta-last-poo"),
                            lg=lg,
                            md=md,
                            sm=sm,
                            width=width,
                        ),
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
                            lg=7,
                            md=12,
                            sm=12,
                            width=12,
                        ),
                        dbc.Col(
                            FigureCard(
                                "Historisk",
                                id="history-graph",
                                description="Summert konsummert morsmelkerstatning per dag.",
                            ),
                            lg=5,
                            md=12,
                            sm=12,
                            width=12,
                        ),
                    ],
                    className="dashboard-row",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dash_table.DataTable(
                                id="selected-day-table",
                                columns=[],  # Initialize with no columns
                                data=[],  # Initialize with no data
                            ),
                        )
                    ]
                ),
            ],
        )
    ],
    id="dashboard",
)
