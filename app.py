import dash
from dash import html, dcc, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Define the URL of the Google Sheets CSV export
url = "https://docs.google.com/spreadsheets/d/1-NblbDmCxDEi5_BCSeVwzzMxZza1Mdbbv8HIPz8XXBI/export?format=csv"

# Read the CSV file directly from the URL into a pandas DataFrame
df = pd.read_csv(url)

# Ensure that 'Flaske' is numeric
df["Flaske"] = pd.to_numeric(df["Flaske"], errors="coerce")

# Calculate the cumulative sum of 'Flaske' for each 'Dato'
df["Cumulative_flaske"] = df.groupby("Dato")["Flaske"].cumsum()


# Define a custom sorting function for dates in the format DD.MM.YYYY
def sort_dates(dates):
    return sorted(
        dates, key=lambda x: (x.split(".")[1], x.split(".")[0], x.split(".")[2])
    )


# Get the unique dates for the dropdown options and sort them using the custom function
unique_dates = sort_dates(df["Dato"].unique())

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout of the app
app.layout = html.Div(
    [
        html.H1("👶🏼 Aron 🍼-tracker"),
        dcc.Dropdown(
            id="date-dropdown",
            options=[{"label": date, "value": date} for date in unique_dates],
            value=unique_dates[-1],  # Set the default value to the last date
        ),
        html.Div(id="table-container"),
        html.Div(id="graph-container"),
    ]
)


# Callback to update the table and graph based on the selected date
@app.callback(
    [Output("table-container", "children"), Output("graph-container", "children")],
    [Input("date-dropdown", "value")],
)
def update_output(selected_date):
    # Filter the DataFrame for the selected date
    filtered_df = df[
        df["Dato"] == selected_date
    ].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Convert 'Tid' to a datetime format assuming the format is HH:MM
    filtered_df["Tid"] = pd.to_datetime(filtered_df["Tid"], format="%H:%M")

    # Create the table for the selected date
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        data=filtered_df.to_dict("records"),
        style_table={"overflowX": "auto"},
    )

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

    return table, graph


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
