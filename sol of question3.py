import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load the CSV file with semicolon delimiter
re_simulation_path = 'Export Resemulation.csv'
re_simulation_df = pd.read_csv(re_simulation_path, delimiter=';')

# Clean column names by removing extra quotation marks and whitespace
re_simulation_df.columns = re_simulation_df.columns.str.replace('"', '').str.strip()

# Convert WEEKLY_REPRICING_DATE to datetime
re_simulation_df['WEEKLY_REPRICING_DATE'] = pd.to_datetime(re_simulation_df['WEEKLY_REPRICING_DATE'], format='%d/%m/%Y')

# Function to parse yield curve data with error handling
def parse_yield_curve(yield_curve_str):
    yield_curve_pairs = yield_curve_str.split()
    yield_curve_dict = {}
    for pair in yield_curve_pairs:
        if ':' not in pair:
            continue
        term, value = pair.split(':')
        try:
            term = int(term.strip().replace('"', '').replace("'", ""))
            value = float(value.strip().replace(',', '.').replace('"', '').replace("'", ""))
            yield_curve_dict[term] = value
        except ValueError:
            continue
    return yield_curve_dict

# Apply the parsing function and handle missing data
re_simulation_df['Parsed_Yield_Curve'] = re_simulation_df['YIELD_CURVE'].apply(parse_yield_curve)
parsed_yield_curves_df = pd.DataFrame(re_simulation_df['Parsed_Yield_Curve'].tolist(), index=re_simulation_df.index)

# Convert day terms to weekly terms
def convert_to_weekly(yield_curve_dict):
    weekly_curve = {}
    for day, value in yield_curve_dict.items():
        week = round(day / 7)+1
        if week not in weekly_curve:
            weekly_curve[week] = []
        weekly_curve[week].append(value)
    # Average the values for each week
    for week in weekly_curve:
        weekly_curve[week] = sum(weekly_curve[week]) / len(weekly_curve[week])
    return weekly_curve

re_simulation_df['Weekly_Yield_Curve'] = re_simulation_df['Parsed_Yield_Curve'].apply(convert_to_weekly)
weekly_yield_curves_df = pd.DataFrame(re_simulation_df['Weekly_Yield_Curve'].tolist(), index=re_simulation_df.index)

# Aggregate data by week
weekly_yield_curves_df = weekly_yield_curves_df.groupby(re_simulation_df['WEEKLY_REPRICING_DATE']).mean()

# Calculate the discounted UWR
re_simulation_df['DISCOUNTED_EXTERNAL_EXPENSES'] = re_simulation_df['DISCOUNTED_EXTERNAL_EXPENSES'].str.replace(',', '.').astype(float)
re_simulation_df['DISCOUNTED_EXP_LOSS'] = re_simulation_df['DISCOUNTED_EXP_LOSS'].str.replace(',', '.').astype(float)
re_simulation_df['EXP_PREMIUM'] = re_simulation_df['EXP_PREMIUM'].str.replace(',', '.').astype(float)
re_simulation_df['DISCOUNTED_EXP_PREMIUM'] = re_simulation_df['DISCOUNTED_EXP_PREMIUM'].str.replace(',', '.').astype(float)

re_simulation_df['Discounted_UWR'] = (
    re_simulation_df['DISCOUNTED_EXTERNAL_EXPENSES'] +
    re_simulation_df['DISCOUNTED_EXP_LOSS'] +
    re_simulation_df['EXP_PREMIUM'] -
    re_simulation_df['DISCOUNTED_EXP_PREMIUM']
) / re_simulation_df['EXP_PREMIUM']

discounted_uwr_df = re_simulation_df.groupby('WEEKLY_REPRICING_DATE')['Discounted_UWR'].mean()

# Align the Discounted UWR with the yield curve dates
#discounted_uwr_df = discounted_uwr_df.reindex(weekly_yield_curves_df.index, method='nearest')

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#print (discounted_uwr_df.head(10))
# Layout of the app
app.layout = dbc.Container([
    dbc.Row(
            [
                dbc.Col(html.Img(src='/assets/scor-logo.png', style={'height':'50px'}), align="start"),
                dbc.Col(html.H3('Yield Curves and Discounted UWR Over Time', style={'color': '#006080'}), align="center"),
                dbc.Col(html.H1('', style={'color': '#006080'}), align="end"),
            ]
        ),
    html.Hr(),
     dbc.Row([
        dbc.Col(html.H6("Select the week terms from the dropdown list :"), className="mb-2")
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='terms-dropdown',
            options=[{'label': f'{term} Weeks', 'value': term} for term in weekly_yield_curves_df.columns],
            value=[term for term in list(weekly_yield_curves_df.columns)[:5]],  # First 5 terms by default
            multi=True
        ), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='yield-curve-graph'), width=12)
    ])
], fluid=True)

# Callback to update the graph based on selected terms
@app.callback(
    Output('yield-curve-graph', 'figure'),
    [Input('terms-dropdown', 'value')]
)
def update_graph(selected_terms):
    fig = go.Figure()
    for term in selected_terms:
        if term in weekly_yield_curves_df.columns:
            fig.add_trace(go.Scatter(
                x=weekly_yield_curves_df.index,
                y=weekly_yield_curves_df[term],
                mode='lines+markers',
                name=f'{term} Weeks'
            ))
    fig.add_trace(go.Scatter(
        x=discounted_uwr_df.index,
        y=discounted_uwr_df,
        mode='lines+markers',
        name='Discounted UWR',
        yaxis='y2'
    ))
    fig.update_layout(
        title='Yield Curves and Discounted UWR Over Time',
        xaxis_title='Date',
        yaxis_title='Yield',
        yaxis2=dict(
            title='Discounted UWR',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
