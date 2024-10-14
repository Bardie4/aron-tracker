import dash
from dash import html, dcc, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime

# Define the URL of the Google Sheets CSV export
URL = "https://docs.google.com/spreadsheets/d/1-NblbDmCxDEi5_BCSeVwzzMxZza1Mdbbv8HIPz8XXBI/export?format=csv"


# Define a custom sorting function for dates in the format DD.MM.YYYY
def sort_dates(dates):
    # Convert string dates to datetime objects
    dates_as_datetime = [datetime.strptime(date, "%d.%m.%Y") for date in dates]
    # Sort the datetime objects
    dates_as_datetime.sort()
    # Convert back to strings
    sorted_dates_as_strings = [
        datetime.strftime(date, "%d.%m.%Y") for date in dates_as_datetime
    ]
    return sorted_dates_as_strings


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout of the app
app.layout = html.Div(
    [
        html.H1("👶🏼 Aron 🍼-tracker"),
        dcc.Dropdown(
            id="date-dropdown",
            options=[],  # Options will be populated by the callback
            value=None,  # Default value will be set by the callback
        ),
        html.Div(id="table-container"),
        html.Div(id="graph-container"),
        html.Div(id="bar-chart-container"),  # Container for the bar chart
    ]
)


# Callback to populate the dropdown options and set the default value
@app.callback(
    Output("date-dropdown", "options"),
    Output("date-dropdown", "value"),
    Input("date-dropdown", "value"),
)
def set_dropdown_options(selected_date):
    df = pd.read_csv(URL)
    unique_dates = sort_dates(df["Dato"].unique())
    options = [{"label": date, "value": date} for date in unique_dates]
    value = unique_dates[-1] if selected_date is None else selected_date
    return options, value


# Callback to update the table and graph based on the selected date
@app.callback(
    [
        Output("table-container", "children"),
        Output("graph-container", "children"),
        Output("bar-chart-container", "children"),
    ],  # Output for the bar chart
    [Input("date-dropdown", "value")],
)
def update_output(selected_date):
    df = pd.read_csv(URL)

    # Ensure that 'Flaske' is numeric
    df["Flaske"] = pd.to_numeric(df["Flaske"], errors="coerce")
    # Sort the DataFrame by 'Dato' using the custom sort_dates function
    df["Dato"] = pd.to_datetime(df["Dato"], format="%d.%m.%Y")
    # Calculate the cumulative sum of 'Flaske' for each 'Dato'
    df["Cumulative_flaske"] = df.groupby("Dato")["Flaske"].cumsum()

    # Filter the DataFrame for the selected date
    filtered_df = df[
        df["Dato"] == selected_date
    ].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Convert 'Tid' to a datetime format assuming the format is HH:MM
    filtered_df["Tid"] = pd.to_datetime(filtered_df["Tid"], format="%H:%M")

    # Create the graph for the selected date
    fig = px.line(
        filtered_df,
        x="Tid",
        y="Cumulative_flaske",
        title=f"Kumulativ melk for {selected_date}",
        markers=True,
    )
    # Add diamond markers where 'Avføring' is 'A'
    avforing_df = filtered_df[filtered_df["Avføring"] == "A"]
    fig.add_trace(
        go.Scatter(
            x=avforing_df["Tid"],
            y=avforing_df["Cumulative_flaske"],
            mode="markers",
            marker=dict(symbol="diamond", size=16, color="orange"),
            name="Avføring",
        )
    )
    # Add star markers where 'Urin' is 'U'
    urin_df = filtered_df[filtered_df["Urin"] == "U"]
    fig.add_trace(
        go.Scatter(
            x=urin_df["Tid"],
            y=urin_df["Cumulative_flaske"],
            mode="markers",
            marker=dict(symbol="star", size=12, color="blue"),
            name="Urin",
        )
    )

    # Add a horizontal red line at y=600
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

    graph = dcc.Graph(figure=fig)

    # Create the bar chart for the sum of 'Flaske' for each day
    sum_flaske_per_day = df.groupby("Dato")["Flaske"].sum().reset_index()
    sum_flaske_per_day.sort_values(by="Dato", inplace=True)
    sum_flaske_per_day["Dato"] = sum_flaske_per_day["Dato"].dt.strftime("%d.%m.%Y")

    # Create the bar chart for the sum of 'Flaske' for each day
    bar_chart_fig = px.bar(
        sum_flaske_per_day,
        x="Dato",
        y="Flaske",
        title="Sum of Flaske per Day",
        labels={"Flaske": "Sum of Flaske", "Dato": "Date"},
    )

    # Update the layout of the bar chart if necessary
    bar_chart_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sum of Flaske",
        xaxis={"type": "category"},  # Treat 'Dato' as a categorical variable
        yaxis={"type": "linear"},  # Ensure 'Flaske' is treated as a linear scale
    )

    bar_chart = dcc.Graph(figure=bar_chart_fig)

    # Create the table for the selected date
    filtered_df["Tid"] = filtered_df["Tid"].dt.strftime(
        "%H:%M"
    )  # Format 'Tid' as HH:MM
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        data=filtered_df.to_dict("records"),
        style_table={"overflowX": "auto"},
    )

    return table, graph, bar_chart


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
