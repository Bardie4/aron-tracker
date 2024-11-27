import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from dataclasses import dataclass
from layout.dashboard import dashboard
from datetime import datetime
from zoneinfo import ZoneInfo
import dash_daq as daq


@dataclass
class TotalStats:
    _df: pd.DataFrame

    def _get_last_day(self):
        return self._df.iloc[-1]["Dato"]

    def _get_last_entry(self, column, value):
        return self._df[self._df[column] == value].iloc[-1]

    def _calculate_time_difference(self, last_time):
        norway_timezone = ZoneInfo("Europe/Oslo")
        current_date = datetime.now(norway_timezone)
        time_difference = current_date - last_time
        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"

    @property
    def total_per_day(self) -> dict:
        total = self._df.groupby("Dato")["Flaske"].sum().to_dict()
        return dict(
            sorted(total.items(), key=lambda x: datetime.strptime(x[0], "%d.%m.%Y"))
        )

    @property
    def total_today(self) -> int:
        return self.total_per_day[list(self.total_per_day.keys())[-1]]

    @property
    def last_meal_time(self) -> datetime:
        last_entry = self._df.iloc[-1]
        last_entry_date = datetime.strptime(last_entry["Dato"], "%d.%m.%Y").date()
        last_entry_time = datetime.strptime(last_entry["Tid"], "%H:%M").time()
        norway_timezone = ZoneInfo("Europe/Oslo")
        return datetime.combine(
            last_entry_date, last_entry_time, tzinfo=norway_timezone
        )

    @property
    def last_poo_time(self) -> datetime:
        last_entry = self._get_last_entry("Avføring", "A")
        last_entry_date = datetime.strptime(last_entry["Dato"], "%d.%m.%Y").date()
        last_entry_time = datetime.strptime(last_entry["Tid"], "%H:%M").time()
        norway_timezone = ZoneInfo("Europe/Oslo")
        return datetime.combine(
            last_entry_date, last_entry_time, tzinfo=norway_timezone
        )

    @property
    def time_since_last_feed(self) -> str:
        return self._calculate_time_difference(self.last_meal_time)

    @property
    def time_since_last_poo(self) -> str:
        return self._calculate_time_difference(self.last_poo_time)

    @property
    def df_last_day(self) -> pd.DataFrame:
        last_day = self._get_last_day()
        return self._df[self._df["Dato"] == last_day]

    @property
    def n_feeds_today(self) -> int:
        return len(self.df_last_day)

    @property
    def n_pee_today(self) -> int:
        return len(self.df_last_day[self.df_last_day["Urin"] == "U"])

    @property
    def n_poo_today(self) -> int:
        return len(self.df_last_day[self.df_last_day["Avføring"] == "A"])

    @property
    def largest_meal(self) -> int:
        daily_sum = self._df.groupby("Dato")["Flaske"].sum()
        max_day = daily_sum.idxmax()
        return daily_sum[max_day]

    @property
    def ideal_now(self) -> int:
        last_entry_time = self.last_meal_time
        start_of_day = datetime.combine(
            last_entry_time.date(), datetime.min.time(), tzinfo=ZoneInfo("Europe/Oslo")
        )
        end_of_day = datetime.combine(
            last_entry_time.date(), datetime.max.time(), tzinfo=ZoneInfo("Europe/Oslo")
        )
        fraction_of_day_passed = (last_entry_time - start_of_day) / (
            end_of_day - start_of_day
        )
        return int(self.largest_meal * fraction_of_day_passed)

    @property
    def suggested_meal(self):
        time_difference = datetime.now(ZoneInfo("Europe/Oslo")) - self.last_meal_time
        return int(
            self.largest_meal * (time_difference.total_seconds() / (60 * 60 * 24))
        )

    def feeds_for_day(self, date):
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
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",
    ],
)
server = app.server


def serve_layout():
    df = pd.read_csv(URL)
    df.dropna(subset=["Tid", "Flaske"], inplace=True)
    unique_dates = sort_dates(df["Dato"].unique())
    dropdown_options = [{"label": date, "value": date} for date in unique_dates]
    dropdown_value = unique_dates[-1] if unique_dates else None

    return html.Div(
        [
            dcc.Store(id="store", data=df.to_dict("records")),
            dbc.Container(
                dbc.Stack(
                    [
                        html.Div(
                            [
                                html.H1("👩‍🍼 Aron tracker", style={"flex": "1"}),
                                daq.ToggleSwitch(
                                    id="dark-mode-toggle",
                                    label="Dark Mode",
                                    value=False,
                                    style={"marginBottom": "20px"},
                                ),
                            ],
                            className="header-container",
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
        className="light-mode",
    )


app.layout = serve_layout


def create_metric_callback(output_index, data_func):
    @app.callback(
        Output({"type": "metric-value", "index": output_index}, "children"),
        Input("store", "data"),
    )
    def callback(data):
        total_stats = TotalStats(pd.DataFrame(data))
        return data_func(total_stats)

    return callback


create_metric_callback(
    "consumed-count", lambda ts: f"{ts.total_today} ({ts.ideal_now}) ml"
)
create_metric_callback("meals-count", lambda ts: f"{ts.n_feeds_today} stk")
create_metric_callback("largest-count", lambda ts: f"{ts.largest_meal} ml")
create_metric_callback(
    "last-meal",
    lambda ts: f"{ts.last_meal_time.hour:02d}:{ts.last_meal_time.minute:02d}",
)
create_metric_callback(
    "delta-last-meal",
    lambda ts: f"{ts.time_since_last_feed.split(':')[0]}h {ts.time_since_last_feed.split(':')[1]}m",
)
create_metric_callback(
    "pee-poo", lambda ts: f"{ts.n_pee_today} 🟡 / {ts.n_poo_today} 🟤"
)
create_metric_callback("suggested-meal", lambda ts: f"{ts.suggested_meal} ml")
create_metric_callback(
    "delta-last-poo",
    lambda ts: f"{ts.time_since_last_poo.split(':')[0]}h {ts.time_since_last_poo.split(':')[1]}m",
)


def delta_last_poo(data):
    total_stats = TotalStats(pd.DataFrame(data))
    h, m = total_stats.time_since_last_poo.split(":")
    return f"{int(h)}h {int(m)}m"


# Figure callbacks
@app.callback(
    Output({"type": "graph", "index": "today-graph"}, "figure"),
    [Input("date-dropdown", "value"), Input("store", "data")],
)
def render_graph(selected_date, data):
    df = pd.DataFrame(data)
    total_stats = TotalStats(df)
    filtered_df = df[df["Dato"] == selected_date].copy()

    filtered_df["Flaske"] = pd.to_numeric(filtered_df["Flaske"], errors="coerce")
    filtered_df["Dato"] = pd.to_datetime(filtered_df["Dato"], format="%d.%m.%Y")
    filtered_df["Cumulative_flaske"] = filtered_df.groupby("Dato")["Flaske"].cumsum()
    filtered_df["Tid"] = pd.to_datetime(filtered_df["Tid"], format="%H:%M")

    fig = px.bar(
        filtered_df,
        x="Tid",
        y="Flaske",
        text="Flaske",
        color_discrete_sequence=["gray"],
        opacity=0.25,
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")

    traces = [
        go.Scatter(
            x=filtered_df["Tid"],
            y=filtered_df["Cumulative_flaske"],
            mode="lines+markers",
            name="Kumulativ",
            line=dict(color="blue", width=3),
        ),
        go.Scatter(
            x=filtered_df[filtered_df["Avføring"] == "A"]["Tid"],
            y=filtered_df[filtered_df["Avføring"] == "A"]["Cumulative_flaske"],
            mode="markers",
            name="Bæsj",
            marker=dict(symbol="diamond", size=16, color="orange"),
        ),
        go.Scatter(
            x=filtered_df[filtered_df["Urin"] == "U"]["Tid"],
            y=filtered_df[filtered_df["Urin"] == "U"]["Cumulative_flaske"],
            mode="markers",
            name="Tiss",
            marker=dict(symbol="star", size=12, color="palegoldenrod"),
        ),
        go.Scatter(
            x=["1900-01-01 00:00:00.0000", "1900-01-01 23:59:59.0000"],
            y=[0, total_stats.largest_meal],
            mode="lines",
            name="Daily Goal",
            opacity=0.25,
            line=dict(color="gray", width=2, dash="dash"),
        ),
    ]

    for trace in traces:
        fig.add_trace(trace)

    fig.add_hline(
        y=total_stats.largest_meal,
        line_color="red",
        line_width=3,
        annotation_text="Største måltid",
        annotation_position="bottom right",
    )

    fig.update_xaxes(tickformat="%H:%M", tickmode="auto")
    fig.update_layout(xaxis_title="Tid", yaxis_title="ml", showlegend=False)

    return fig


@app.callback(
    Output({"type": "graph", "index": "history-graph"}, "figure"),
    Input("store", "data"),
)
def summary(data):
    df = pd.DataFrame(data)
    df["Dato"] = pd.to_datetime(df["Dato"], dayfirst=True)
    daily_totals = df.groupby("Dato")["Flaske"].sum().reset_index()
    daily_totals["7_day_avg"] = (
        daily_totals["Flaske"].rolling(window=7, min_periods=1).mean()
    )
    daily_totals["Dato"] = daily_totals["Dato"].dt.strftime("%d-%m-%y")

    fig = px.bar(
        daily_totals, x="Dato", y="Flaske", labels={"y": "Sum of Flaske", "x": "Date"}
    )
    fig.add_trace(
        go.Scatter(
            x=daily_totals[:-1]["Dato"],
            y=daily_totals[:-1]["7_day_avg"],
            mode="lines",
            name="7 Day Average",
        )
    )
    fig.update_layout(
        xaxis_title="Dato",
        yaxis_title="ml",
        xaxis={"type": "category"},
        yaxis={"type": "linear"},
        showlegend=False,
    )
    return fig


@app.callback(
    [Output("selected-day-table", "data"), Output("selected-day-table", "columns")],
    [Input("date-dropdown", "value"), Input("store", "data")],
)
def last_day_table(selected_date, data):
    if selected_date is None or not data:
        # Return empty data and columns if no date selected or no data
        return [], []

    # Convert data to DataFrame and filter for selected date
    df = pd.DataFrame(data)
    selected_columns = ["Tid", "Flaske", "Notat"]
    filtered_df = df.loc[df["Dato"] == selected_date, selected_columns]

    # Create column definitions for DataTable
    columns = [{"name": col, "id": col} for col in selected_columns]

    return filtered_df.to_dict("records"), columns


@app.callback(
    Output("page", "className"),
    Input("dark-mode-toggle", "value"),
)
def toggle_dark_mode(is_checked):
    if is_checked:
        return "dark-mode"
    return "light-mode"


if __name__ == "__main__":
    app.run(debug=True)
