import base64
import io
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://fonts.googleapis.com/icon?family=Material+Icons']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

gradient_bg = "linear-gradient(to top left, #753682 0%, #bf2e34 100%)"

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '40px', 'background': gradient_bg}, children=[
    html.H1('Emotional Expressions in Videos: Analysis Platform', style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '30px'}),
    html.H2('Data Upload', style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '30px'}),
    
    # CSV File Uploader
    html.Div([
        dcc.Upload(
            id='upload-csv',
            children=html.Div([
                html.I('cloud_upload', className='material-icons', style={'fontSize': '48px', 'color': '#4CAF50'}),
                ' Drag and Drop or ',
                html.A('Select a CSV File', style={'textDecoration': 'underline', 'color': '#4CAF50'})
            ]),
            style={
                'width': '100%', 'height': '70px', 'lineHeight': '70px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '20px 0', 'cursor': 'pointer', 'backgroundColor': '#FFFFFFAA'
            },
            multiple=False
        ),
        html.Div(id='output-upload-csv-status'),
        html.Button('Analyse CSV Data', id='analyse-csv-button', n_clicks=0, style={
            'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'padding': '10px 20px', 'cursor': 'pointer',
        }),
        
        # Hidden Div to store DataFrame
        html.Div(id='intermediate-value', style={'display': 'none'})
    ], style={'boxShadow': '0 8px 16px rgba(0, 0, 0, 0.1)', 'padding': '20px', 'borderRadius': '10px', 'backgroundColor': '#FFFFFFAA'}),
    
    # Video File Uploader
html.Div([
        dcc.Upload(
            id='upload-video',
            children=html.Div([
                html.I('videocam', className='material-icons', style={'fontSize': '48px', 'color': '#2196F3'}),
                ' Drag and Drop or ',
                html.A('Select a Video', style={'textDecoration': 'underline', 'color': '#2196F3'})
            ]),
            style={
                'width': '100%', 'height': '70px', 'lineHeight': '70px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '20px 0', 'cursor': 'pointer', 'backgroundColor': '#FFFFFFAA'
            },
            accept='video/mp4',  # Restrict to .mp4 videos
            multiple=False
        ),
        html.Div(id='output-upload-video-status'),
        html.Button('Analyse Video', id='analyse-video-button', n_clicks=0, style={
            'backgroundColor': '#2196F3', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'padding': '10px 20px', 'cursor': 'pointer',
        }),
    ], style={'boxShadow': '0 8px 16px rgba(0, 0, 0, 0.1)', 'padding': '20px', 'borderRadius': '10px', 'backgroundColor': '#FFFFFFAA'}),

    
    html.Hr(style={'borderColor': '#ddd', 'marginTop': '40px'}),
    
    html.H2('Visualization Dashboard', style={'textAlign': 'center', 'color': '#FFFFFF'}),
    
    # Dropdown, Pie Chart, and Line Graph
    html.Div(id='graphs-container', children=[
        dcc.Dropdown(
            id='emotion-dropdown',
            multi=True,
            style={'marginBottom': '20px'}
        ),
        dcc.Graph(id='pie-chart'),
        dcc.Graph(id='line-graph')
    ], style={'boxShadow': '0 8px 16px rgba(0, 0, 0, 0.1)', 'padding': '20px', 'borderRadius': '10px', 'backgroundColor': '#FFFFFFAA'}),
    
    # Video Display Area
    html.Div(id='video-display-area', style={'marginTop': '40px'})
])

@app.callback(
    [Output('output-upload-csv-status', 'children'),
     Output('intermediate-value', 'children'),
     Output('emotion-dropdown', 'options')],
    Input('upload-csv', 'contents')
)
def update_csv_output(content):
    if content is None:
        return 'Awaiting CSV file...', None, []
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df.columns = df.columns.str.lower()
        options = [{'label': col, 'value': col} for col in df.columns if col != 'approx_time']
        return [html.Span([html.I('check_circle', className='material-icons', style={'color': '#4CAF50'}), ' CSV file uploaded successfully!'], style={'color': '#4CAF50'}), df.to_json(date_format='iso', orient='split'), options]
    except Exception as e:
        return [html.Span([html.I('error', className='material-icons', style={'color': 'red'}), f' Error: {e}'], style={'color': 'red'}), None, []]

@app.callback(
    Output('pie-chart', 'figure'),
    [Input('emotion-dropdown', 'value'),
     State('intermediate-value', 'children')]
)
def update_pie_chart(selected_emotions, jsonified_df):
    if not selected_emotions or not jsonified_df:
        return dash.no_update
    dynamic_df = pd.read_json(jsonified_df, orient='split')
    data = dynamic_df[selected_emotions].sum()
    fig = px.pie(values=data, names=selected_emotions, title='Pie Chart of Emotion Sums')
    fig.update_traces(textinfo='percent+label', insidetextorientation='radial')
    return fig

@app.callback(
    Output('line-graph', 'figure'),
    [Input('emotion-dropdown', 'value'),
     State('intermediate-value', 'children')]
)
def update_line_chart(selected_emotions, jsonified_df):
    if not selected_emotions or not jsonified_df:
        return dash.no_update
    dynamic_df = pd.read_json(jsonified_df, orient='split')
    fig = px.line(dynamic_df, x='approx_time', y=selected_emotions, title='Line Chart of Emotion Over Time')
    fig.update_xaxes(title_text='Approx. Time')
    fig.update_yaxes(title_text='Emotion Value')
    return fig
@app.callback(
    [Output('output-upload-video-status', 'children'),
     Output('video-display-area', 'children')],
    Input('upload-video', 'contents')
)
def upload_video_callback(video_content):
    if video_content is None:
        return 'Awaiting video file...', dash.no_update

    content_type, content_string = video_content.split(',')
    
    # Ensure the uploaded content is of video type.
    if "video" in content_type:
        video_tag = html.Video(
            controls=True,
            src=f"data:{content_type};base64,{content_string}",
            style={'width': '100%', 'height': 'auto'}
        )
        return [html.Span([html.I('check_circle', className='material-icons', style={'color': '#2196F3'}), ' Video uploaded successfully!'], style={'color': '#2196F3'}), video_tag]
    else:
        return [html.Span([html.I('error', className='material-icons', style={'color': 'red'}), ' Uploaded file is not a video.'], style={'color': 'red'}), dash.no_update]

if __name__ == '__main__':
    app.run_server(debug=True)
