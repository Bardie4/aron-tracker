import dash
from dash import html, dcc, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from dataclasses import dataclass

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
        current_date = datetime.now()
        last_entry_datetime = datetime.combine(last_entry_date, last_entry_time)
        time_difference = current_date - last_entry_datetime
        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_difference_formatted = f"{hours:02d}:{minutes:02d}"
        return time_difference_formatted

    def feeds_for_day(self, date):
        # Format as dict of time: amount
        feeds = self._df[self._df["Dato"] == date].set_index("Tid")["Flaske"].to_dict()
        return feeds
    
URL = "https://docs.google.com/spreadsheets/d/1-NblbDmCxDEi5_BCSeVwzzMxZza1Mdbbv8HIPz8XXBI/export?format=csv"
df = pd.DataFrame()
total_stats = TotalStats(df)


def sort_dates(dates):
    dates_as_datetime = [datetime.strptime(date, "%d.%m.%Y") for date in dates]
    dates_as_datetime.sort()
    return [datetime.strftime(date, "%d.%m.%Y") for date in dates_as_datetime]

app = dash.Dash(__name__)
server = app.server

def serve_layout():
    # Fetch the data when layout is called
    df = pd.read_csv(URL)
    
    # Generate the dropdown options
    unique_dates = sort_dates(df["Dato"].unique())
    dropdown_options = [{"label": date, "value": date} for date in unique_dates]
    dropdown_value = unique_dates[-1] if unique_dates else None
    
    # Store the DataFrame in dcc.Store for access by the callback
    return html.Div(
        [
            dcc.Store(id='data-store', data=df.to_dict('records')),
            html.H1("👶🏼 Aron 🍼-tracker"),
            html.H2("Statistikk"),
            html.Div(id="stats-container"),
            html.H2("Velg dato"),
            dcc.Dropdown(
                id="date-dropdown",
                options=dropdown_options,
                value=dropdown_value,
            ),
            html.Div(id="graph-container"),
            html.H2("Mat per dag"),
            html.Div(id="bar-chart-container"),
        ]
    )


# Set the app.layout to the serve_layout function
app.layout = serve_layout

# === STATS ===
@app.callback(
    Output("stats-container", "children"),
    [Input("date-dropdown", "value"),
     Input("data-store", "data")]
)
def render_stats(selected_date, data):
    df = pd.DataFrame(data)
    total_stats = TotalStats(df)
    return html.Div(
        [
            html.P(f"Totalt i dag: {total_stats.total_today}"),
            html.P(f"Tid siden forrige måltid: {total_stats.time_since_last_feed}"),
        ]
    )

# === BAR CHART ===
@app.callback(
    Output("bar-chart-container", "children"),
    [Input("data-store", "data")]
)
def render_bar_chart(data):
    df = pd.DataFrame(data)
    total_stats = TotalStats(df)

    # Create the bar chart from the total stats
    bar_chart_fig = px.bar(
        x=list(total_stats.total_per_day.keys()),
        y=list(total_stats.total_per_day.values()),
        title="Sum of Flaske per Day",
        labels={"Flaske": "Sum of Flaske", "Dato": "Date"},
    )

    # Update the layout of the bar chart if necessary
    bar_chart_fig.update_layout(
        xaxis_title="Dato",
        yaxis_title="Konsumert melk (ml)",
        xaxis={"type": "category"},  # Treat 'Dato' as a categorical variable
        yaxis={"type": "linear"},  # Ensure 'Flaske' is treated as a linear scale
    )

    return dcc.Graph(figure=bar_chart_fig)


# === DATE DROPDOWN ===
@app.callback(
    Output("date-dropdown", "options"),
    Output("date-dropdown", "value"),
    [Input("date-dropdown", "value"),
     Input("data-store", "data")]
)
def set_dropdown_options(selected_date, data):
    df = pd.DataFrame(data)
    unique_dates = sort_dates(df["Dato"].unique())
    options = [{"label": date, "value": date} for date in unique_dates]
    value = unique_dates[-1] if selected_date is None else selected_date
    return options, value

# === GRAPH ===
@app.callback(
    Output("graph-container", "children"),
    [Input("date-dropdown", "value"),
     Input("data-store", "data")]
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
        y=600,
        line_color="red",
        line_width=3,
        annotation_text="600 ml",
        annotation_position="bottom right",
    )

    # Update layout for 'Tid' axis to treat as a datetime
    fig.update_xaxes(
        tickformat="%H:%M",  # Format the ticks as hours and minutes
        tickmode="auto",  # Use automatic tick mode for datetime data
    )

    return dcc.Graph(figure=fig)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
