import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import json
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, MATCH, ALL
from sqlalchemy import create_engine
from dataclasses import dataclass
from layout.dashboard import dashboard
from datetime import datetime, timezone

@dataclass
class TotalStats:
    _df: pd.DataFrame

    @property
    def total_per_day(self):
        # format as dict of date: total
        total = self._df.groupby("Dato")["Flaske"].sum().to_dict()
        # Sort the dictionary by date
        return dict(sorted(total.items(), key=lambda x: datetime.strptime(x[0], "%d.%m.%Y")))

    @property
    def total_today(self):
        return self.total_per_day[list(self.total_per_day.keys())[-1]]

    @property
    def time_since_last_feed(self):
        last_entry = self._df.iloc[-1]
        last_entry_date = datetime.strptime(last_entry["Dato"], "%d.%m.%Y").date()
        last_entry_time = datetime.strptime(last_entry["Tid"], "%H:%M").time()
        norway_timezone = ZoneInfo("Europe/Oslo")
        last_entry_datetime = datetime.combine(last_entry_date, last_entry_time, tzinfo=norway_timezone)
        current_date = datetime.now(norway_timezone)
        time_difference = current_date - last_entry_datetime
        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_difference_formatted = f"{hours:02d}:{minutes:02d}"
        return time_difference_formatted

    @property
    def n_feeds_today(self):
        last_day = self._df.iloc[-1]["Dato"]
        return len(self._df[self._df["Dato"] == last_day])

    @property
    def largest_meal(self):
        daily_sum = self._df.groupby("Dato")["Flaske"].sum()
        max_day = daily_sum.idxmax()
        return daily_sum[max_day]

    def feeds_for_day(self, date):
        # Format as dict of time: amount
        feeds = self._df[self._df["Dato"] == date].set_index("Tid")["Flaske"].to_dict()
        return feeds

def sort_dates(dates):
    dates_as_datetime = [datetime.strptime(date, "%d.%m.%Y") for date in dates]
    dates_as_datetime.sort()
    return [datetime.strftime(date, "%d.%m.%Y") for date in dates_as_datetime]

URL = "https://docs.google.com/spreadsheets/d/1-NblbDmCxDEi5_BCSeVwzzMxZza1Mdbbv8HIPz8XXBI/export?format=csv"
df = pd.DataFrame()
total_stats = TotalStats(df)

app = Dash(
    __name__,
    title="Streaming Metrics",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",  # Icons
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",  # Font
    ],
)
server = app.server

def serve_layout():
    # Fetch the data when layout is called
    df = pd.read_csv(URL)
    df.dropna(subset=["Tid", "Flaske"], inplace=True)
    
    # Generate the dropdown options
    unique_dates = sort_dates(df["Dato"].unique())
    dropdown_options = [{"label": date, "value": date} for date in unique_dates]
    dropdown_value = unique_dates[-1] if unique_dates else None
    
    # Store the DataFrame in dcc.Store for access by the callback
    return html.Div(
        [
            dcc.Store(
                id="store",
                data=df.to_dict('records')
            ),
            dbc.Container(
                dbc.Stack(
                    [
                        html.H1(
                            "Aron tracker"
                        ),
                        dcc.Dropdown(
                            id="date-dropdown",
                            options=dropdown_options,
                            value=dropdown_value,
                        ),
                        dashboard,
                    ],
                    gap=3,
                ),
                id="content",
                className="p-3",
            ),
        ],
        id="page",
    )

app.layout = serve_layout



# Metric card callbacks
@app.callback(
    Output({"type": "metric-value", "index": "consumed-count"}, "children"),
    Input("store", "data"),
)
def consumed_count(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return total_stats.total_today


@app.callback(
    Output({"type": "metric-value", "index": "meals-count"}, "children"),
    Input("store", "data"),
)
def meals_count(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return total_stats.n_feeds_today


@app.callback(
    Output({"type": "metric-value", "index": "largest-count"}, "children"),
    Input("store", "data"),
)
def largest_count(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return total_stats.largest_meal


# Figure callbacks
@app.callback(
    Output({"type": "graph", "index": "today-graph"}, "figure"),
    [Input("date-dropdown", "value"), Input("store", "data")]
)
def render_graph(selected_date, data):
    df = pd.DataFrame(data)
    total_stats = TotalStats(df)

    filtered_df = df[
        df["Dato"] == selected_date
    ].copy()

    filtered_df["Flaske"] = pd.to_numeric(filtered_df["Flaske"], errors="coerce")
    filtered_df["Dato"] = pd.to_datetime(filtered_df["Dato"], format="%d.%m.%Y")
    filtered_df["Cumulative_flaske"] = filtered_df.groupby("Dato")["Flaske"].cumsum()

    filtered_df["Tid"] = pd.to_datetime(filtered_df["Tid"], format="%H:%M")

    # Create the graph for the selected date
    fig = px.line(
        filtered_df,
        x="Tid",
        y="Cumulative_flaske",
        title=f"Kumulativ melk for {selected_date}",
        markers=True,
    )

    # Bæsj
    # avforing_df = filtered_df[filtered_df["Avføring"] == "A"]
    # fig.add_trace(
    #     go.Scatter(
    #         x=avforing_df["Tid"],
    #         y=avforing_df["Cumulative_flaske"],
    #         mode="markers",
    #         marker=dict(symbol="diamond", size=16, color="orange"),
    #         name="Bæsj",
    #     )
    # )

    # Tiss
    # urin_df = filtered_df[filtered_df["Urin"] == "U"]
    # fig.add_trace(
    #     go.Scatter(
    #         x=urin_df["Tid"],
    #         y=urin_df["Cumulative_flaske"],
    #         mode="markers",
    #         marker=dict(symbol="star", size=12, color="palegoldenrod"),
    #         name="Tiss",
    #     )
    # )

    # Mål
    # fig.add_hline(
    #     y=total_stats.largest_meal,
    #     line_color="red",
    #     line_width=3,
    #     annotation_text="Største måltid",
    #     annotation_position="bottom right",
    # )

    # Ideallinje
    # fig.add_trace(
    #     go.Scatter(
    #         x=["1900-01-01 00:00:00.0000", "1900-01-01 23:59:59.0000"],
    #         y=[0, total_stats.largest_meal],
    #         mode='lines',
    #         name='Daily Goal',
    #         opacity=0.25,
    #         line=dict(color='gray', width=2, dash='dash'),
    #     )
    # )

    # Update layout for 'Tid' axis to treat as a datetime
    # fig.update_xaxes(
    #     tickformat="%H:%M",  # Format the ticks as hours and minutes
    #     tickmode="auto",  # Use automatic tick mode for datetime data
    # )

    return fig


@app.callback(
    Output({"type": "graph", "index": "history-graph"}, "figure"),
    Input("store", "data"),
)
def summary_figure(data):
    total_stats = TotalStats(pd.DataFrame(data))

    # Create the bar chart from the total stats
    fig = px.bar(
        x=list(total_stats.total_per_day.keys()),
        y=list(total_stats.total_per_day.values()),
        title="Sum of Flaske per Day",
        labels={"Flaske": "Sum of Flaske", "Dato": "Date"},
    )

    # Update the layout of the bar chart if necessary
    fig.update_layout(
        xaxis_title="Dato",
        yaxis_title="Konsumert melk (ml)",
        xaxis={"type": "category"},  # Treat 'Dato' as a categorical variable
        yaxis={"type": "linear"},  # Ensure 'Flaske' is treated as a linear scale
    )

    return fig



# @app.callback(
#     Output({"type": "graph", "index": "growth"}, "figure"),
#     Input("filters-store", "data"),
# )
# def recent_content_figure(filters):
#     data = data_connector.get_change_data(filters)
#     platform_order = [
#         i for i in data_connector.platform_order if i in set(data.platform)
#     ]

#     platforms = pd.Series(platform_order)
#     data.set_index('platform', inplace=True)

#     figure = go.Figure(
#         data=[
#             go.Bar(
#                 x=platforms,
#                 y=platforms.apply(lambda x: data.loc[x, 'net_change'] if x in data.index else 0),
#                 marker={'color' : 'white', 'opacity' : 0},
#                 name='Net Change',
#                 hovertemplate='<b>Net Change: %{y}</b><extra></extra>'
#             ),
#             go.Bar(
#                 x=platforms,
#                 y=platforms.apply(lambda x: data.loc[x, 'movie_gained'] if x in data.index else 0),
#                 width=0.4,
#                 offset=-0.4,
#                 name='Movies Gained',
#                 marker={'color' : px.colors.sequential.dense[4]}
#             ),
#             go.Bar(
#                 x=platforms,
#                 y=platforms.apply(lambda x: data.loc[x, 'movie_lost'] if x in data.index else 0),
#                 width=0.4,
#                 offset=-0.4,
#                 name='Movies Lost',
#                 marker={'color' : px.colors.sequential.dense[2]}
#             ),
#             go.Bar(
#                 x=platforms,
#                 y=platforms.apply(lambda x: data.loc[x, 'tv_gained'] if x in data.index else 0),
#                 width=0.4,
#                 offset=0,
#                 name='TV Gained',
#                 marker={'color' : px.colors.sequential.dense[-5]}
#             ),
#             go.Bar(
#                 x=platforms,
#                 y=platforms.apply(lambda x: data.loc[x, 'tv_lost'] if x in data.index else 0),
#                 width=0.4,
#                 offset=0,
#                 name='TV Lost',
#                 marker={'color' : px.colors.sequential.dense[-3]}
#             ), 
#         ],
#         layout=go.Layout(
#             showlegend=False,
#             xaxis={
#                 'title' : 'Platform',
#                 'ticktext' : platforms,
#                 'tickangle' : 45
#             },
#             yaxis={
#                 'title' : 'Title Count'
#             },
#             template='plotly_white',
#             hovermode='x unified',
#         )
#     )

#     return figure


if __name__ == "__main__":
    if os.environ.get("environment") == "heroku":
        app.run(debug=False)
    else:
        app.run(debug=True)