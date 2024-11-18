import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, dash_table
from dataclasses import dataclass
from layout.dashboard import dashboard
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class TotalStats:
    _df: pd.DataFrame

    @property
    def total_per_day(self) -> dict:
        # format as dict of date: total
        total = self._df.groupby("Dato")["Flaske"].sum().to_dict()
        # Sort the dictionary by date
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
        last_entry = self._df[self._df["Avføring"] == "A"].iloc[-1]
        last_entry_date = datetime.strptime(last_entry["Dato"], "%d.%m.%Y").date()
        last_entry_time = datetime.strptime(last_entry["Tid"], "%H:%M").time()
        norway_timezone = ZoneInfo("Europe/Oslo")
        return datetime.combine(
            last_entry_date, last_entry_time, tzinfo=norway_timezone
        )

    @property
    def current_time(self) -> datetime:
        # Get the current time in UTC
        current_utc_time = datetime.utcnow()
        # Define the Norway timezone
        norway_timezone = ZoneInfo("Europe/Oslo")
        # Convert the current UTC time to Norway time
        current_oslo_time = current_utc_time.astimezone(norway_timezone)
        return current_oslo_time

    @property
    def time_since_last_feed(self) -> str:
        norway_timezone = ZoneInfo("Europe/Oslo")
        current_date = datetime.now(norway_timezone)
        time_difference = current_date - self.last_meal_time
        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_difference_formatted = f"{hours:02d}:{minutes:02d}"
        return time_difference_formatted

    @property
    def time_since_last_poo(self) -> str:
        norway_timezone = ZoneInfo("Europe/Oslo")
        current_date = datetime.now(norway_timezone)
        time_difference = current_date - self.last_poo_time
        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_difference_formatted = f"{hours:02d}:{minutes:02d}"
        return time_difference_formatted

    @property
    def df_last_day(self) -> pd.DataFrame:
        last_day = self._df.iloc[-1]["Dato"]
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
        norway_timezone = ZoneInfo("Europe/Oslo")
        # Get the time of the last entry
        last_entry_time = self.last_meal_time

        # Calculate the start of the day for the last entry
        start_of_day = datetime.combine(
            last_entry_time.date(), datetime.min.time(), tzinfo=norway_timezone
        )
        end_of_day = datetime.combine(
            last_entry_time.date(), datetime.max.time(), tzinfo=norway_timezone
        )

        # Calculate the fraction of the day that has passed up to the last entry
        fraction_of_day_passed = (last_entry_time - start_of_day) / (
            end_of_day - start_of_day
        )

        # Calculate the ideal intake up to the time of the last entry
        ideal_intake_now = self.largest_meal * fraction_of_day_passed

        return int(ideal_intake_now)

    @property
    def suggested_meal(self):
        norway_timezone = ZoneInfo("Europe/Oslo")
        current_date = datetime.now(norway_timezone)
        time_difference = current_date - self.last_meal_time

        return int(
            self.largest_meal * (time_difference.total_seconds() / (60 * 60 * 24))
        )

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
            dcc.Store(id="store", data=df.to_dict("records")),
            dbc.Container(
                dbc.Stack(
                    [
                        html.H1("👩‍🍼 Aron tracker"),
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
    return f"{total_stats.total_today} ({total_stats.ideal_now}) ml"


@app.callback(
    Output({"type": "metric-value", "index": "meals-count"}, "children"),
    Input("store", "data"),
)
def meals_count(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return f"{total_stats.n_feeds_today} stk"


@app.callback(
    Output({"type": "metric-value", "index": "largest-count"}, "children"),
    Input("store", "data"),
)
def largest_meal(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return f"{total_stats.largest_meal} ml"


@app.callback(
    Output({"type": "metric-value", "index": "last-meal"}, "children"),
    Input("store", "data"),
)
def last_meal_time(data):
    total_stats = TotalStats(pd.DataFrame(data))
    hh = f"{total_stats.last_meal_time.hour:02d}"
    mm = f"{total_stats.last_meal_time.minute:02d}"
    return f"{hh}:{mm}"


@app.callback(
    Output({"type": "metric-value", "index": "delta-last-meal"}, "children"),
    Input("store", "data"),
)
def delta_last_meal(data):
    total_stats = TotalStats(pd.DataFrame(data))
    h, m = total_stats.time_since_last_feed.split(":")
    return f"{int(h)}h {int(m)}m"


@app.callback(
    Output({"type": "metric-value", "index": "pee-poo"}, "children"),
    Input("store", "data"),
)
def pee_poo(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return f"{total_stats.n_pee_today} 🟡 / {total_stats.n_poo_today} 🟤"


@app.callback(
    Output({"type": "metric-value", "index": "suggested-meal"}, "children"),
    Input("store", "data"),
)
def suggested_meal(data):
    total_stats = TotalStats(pd.DataFrame(data))
    return f"{total_stats.suggested_meal} ml"


@app.callback(
    Output({"type": "metric-value", "index": "delta-last-poo"}, "children"),
    Input("store", "data"),
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

    # Create the graph for the selected date
    fig = px.bar(
        filtered_df,
        x="Tid",
        y="Flaske",
        text="Flaske",
        color_discrete_sequence=["gray"],  # Set the bar color to gray
        opacity=0.25,  # Set the opacity to 1.0 for fully opaque bars
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")

    # Add the cumulative line trace
    fig.add_trace(
        go.Scatter(
            x=filtered_df["Tid"],
            y=filtered_df["Cumulative_flaske"],
            mode="lines+markers",
            name="Kumulativ",
            line=dict(color="blue", width=3),
        )
    )

    # Bæsj
    avforing_df = filtered_df[filtered_df["Avføring"] == "A"]
    fig.add_trace(
        go.Scatter(
            x=avforing_df["Tid"],
            y=avforing_df["Cumulative_flaske"],
            mode="markers",
            marker=dict(symbol="diamond", size=16, color="orange"),
            name="Bæsj",
        )
    )

    # Tiss
    urin_df = filtered_df[filtered_df["Urin"] == "U"]
    fig.add_trace(
        go.Scatter(
            x=urin_df["Tid"],
            y=urin_df["Cumulative_flaske"],
            mode="markers",
            marker=dict(symbol="star", size=12, color="palegoldenrod"),
            name="Tiss",
        )
    )

    # Mål
    fig.add_hline(
        y=total_stats.largest_meal,
        line_color="red",
        line_width=3,
        annotation_text="Største måltid",
        annotation_position="bottom right",
    )

    # Ideallinje
    fig.add_trace(
        go.Scatter(
            x=["1900-01-01 00:00:00.0000", "1900-01-01 23:59:59.0000"],
            y=[0, total_stats.largest_meal],
            mode="lines",
            name="Daily Goal",
            opacity=0.25,
            line=dict(color="gray", width=2, dash="dash"),
        )
    )

    # Update layout for 'Tid' axis to treat as a datetime
    fig.update_xaxes(
        tickformat="%H:%M",  # Format the ticks as hours and minutes
        tickmode="auto",  # Use automatic tick mode for datetime data
    )

    fig.update_layout(xaxis_title="Tid", yaxis_title="ml", showlegend=False)

    return fig


@app.callback(
    Output({"type": "graph", "index": "history-graph"}, "figure"),
    Input("store", "data"),
)
def summary(data):
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)
    df["Dato"] = pd.to_datetime(
        df["Dato"], dayfirst=True
    )  # Ensure 'Dato' is a datetime object

    # Group by 'Dato' and sum the 'Flaske' values for each date
    daily_totals = df.groupby("Dato")["Flaske"].sum().reset_index()
    daily_totals["7_day_avg"] = (
        daily_totals["Flaske"].rolling(window=7, min_periods=1).mean()
    )
    daily_totals["Dato"] = daily_totals["Dato"].dt.strftime("%d-%m-%y")

    # Exclude the last day from the 7-day average series
    average_data = daily_totals[:-1]

    # Create the bar chart from the daily totals
    fig = px.bar(
        daily_totals,
        x="Dato",
        y="Flaske",
        labels={"y": "Sum of Flaske", "x": "Date"},
    )

    # Add the 7-day average line to the bar chart, excluding the last day
    fig.add_trace(
        go.Scatter(
            x=average_data["Dato"],
            y=average_data["7_day_avg"],
            mode="lines",
            name="7 Day Average",
        )
    )

    # Update the layout of the bar chart if necessary
    fig.update_layout(
        xaxis_title="Dato",
        yaxis_title="ml",
        xaxis={"type": "category"},  # Treat 'Dato' as a categorical variable
        yaxis={"type": "linear"},  # Ensure 'Flaske' is treated as a linear scale
        showlegend=False,
    )

    return fig


@app.callback(
    [Output("selected-day-table", "data"), Output("selected-day-table", "columns")],
    [Input("date-dropdown", "value"), Input("store", "data")],
)
def last_day_table(selected_date, data):
    if selected_date is None or not data:
        # If no date is selected or there is no data, return an empty list
        return []

    # Convert the data to a DataFrame
    df = pd.DataFrame(data)
    # Filter the DataFrame for the selected date
    filtered_df = df[df["Dato"] == selected_date]
    filtered_df = filtered_df[["Tid", "Flaske", "Notat"]]

    columns = [{"name": i, "id": i} for i in filtered_df.columns]

    # Convert the filtered DataFrame to a dictionary for the DataTable
    return filtered_df.to_dict("records"), columns


if __name__ == "__main__":
    app.run(debug=True)
