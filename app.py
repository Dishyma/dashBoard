import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

# Estilos CSS personalizados
BUTTON_STYLE = {
    'backgroundColor': '#4CAF50',
    'color': 'white',
    'padding': '10px 20px',
    'border': 'none',
    'borderRadius': '4px',
    'cursor': 'pointer',
    'marginRight': '10px',
    'fontSize': '14px',
    'transition': 'background-color 0.3s'
}

DROPDOWN_STYLE = {
    'width': '200px',
    'marginBottom': '20px',
    'marginTop': '10px'
}

CONTAINER_STYLE = {
    'backgroundColor': '#f8f9fa',
    'padding': '20px',
    'borderRadius': '8px',
    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
    'marginBottom': '20px'
}

# Función para cargar datos
def load_data(filename):
    try:
        return pd.read_csv(f'./{filename}.csv')
    except:
        return pd.DataFrame()

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout
app.layout = html.Div([
    # Título principal
    html.H1('Análisis de Datos de Boxeo', 
            style={
                'textAlign': 'center',
                'marginBottom': '30px',
                'color': '#2c3e50',
                'fontFamily': 'Arial, sans-serif'
            }),
    
    # Contenedor para los controles
    html.Div([
        # Selector de archivo
        html.Div([
            html.Label('Selecciona el archivo de datos:',
                      style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='file-selector',
                options=[
                    {'label': 'Golpe 1', 'value': 'golpe1'},
                    {'label': 'Golpe 2', 'value': 'golpe2'}
                ],
                value='golpe2',
                style=DROPDOWN_STYLE
            )
        ], style=CONTAINER_STYLE),

        # Panel principal
        html.Div([
            # Contenedor izquierdo para checklist y botones
            html.Div([
                html.Label('Variables a graficar:',
                          style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.Div(
                    id='checklist-container',
                    style={'marginBottom': '20px', 'maxHeight': '400px', 'overflowY': 'auto'}
                ),
                # Botones con hover effect
                html.Div([
                    html.Button(
                        'Seleccionar Todo', 
                        id='select-all', 
                        n_clicks=0,
                        style=BUTTON_STYLE
                    ),
                    html.Button(
                        'Deseleccionar Todo', 
                        id='deselect-all', 
                        n_clicks=0,
                        style={
                            **BUTTON_STYLE,
                            'backgroundColor': '#f44336'
                        }
                    ),
                ], style={'marginTop': '10px'})
            ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            # Contenedor derecho para la gráfica
            html.Div([
                dcc.Graph(id='main-graph')
            ], style={'width': '80%', 'display': 'inline-block'})
        ], style={'display': 'flex'})
    ], style={'margin': '20px'})
])

# Callback para actualizar el checklist cuando cambia el archivo
@app.callback(
    Output('checklist-container', 'children'),
    Input('file-selector', 'value')
)
def update_checklist_options(selected_file):
    df = load_data(selected_file)
    if df.empty:
        return html.Div("Error: Archivo no encontrado")
    
    columns_to_plot = [col for col in df.columns if col != 't']
    return dcc.Checklist(
        id='variables-checklist',
        options=[{'label': ' ' + col, 'value': col} for col in columns_to_plot],
        value=columns_to_plot[:3],
        style={'marginBottom': '20px'}
    )

# Callback para los botones de selección
@app.callback(
    Output('variables-checklist', 'value'),
    [Input('select-all', 'n_clicks'),
     Input('deselect-all', 'n_clicks'),
     Input('file-selector', 'value')],
    State('variables-checklist', 'options'),
    prevent_initial_call=True
)
def update_checklist(select_clicks, deselect_clicks, selected_file, options):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'select-all':
        return [option['value'] for option in options]  # Select all options
    elif button_id == 'deselect-all':
        return []  # Deselect all options
    return dash.no_update

# Callback para actualizar la gráfica
@app.callback(
    Output('main-graph', 'figure'),
    [Input('variables-checklist', 'value'),
     Input('file-selector', 'value')]
)
def update_graph(selected_variables, selected_file):
    if not selected_variables:
        return go.Figure()
    
    df = load_data(selected_file)
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    for col in selected_variables:
        fig.add_trace(
            go.Scatter(
                x=df['t'],
                y=df[col],
                name=col,
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=6)
            )
        )
    
    fig.update_layout(
        title={
            'text': f'Variables vs Tiempo - {selected_file.capitalize()}',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Tiempo (s)',
        yaxis_title='Valor',
        template="plotly_white",
        height=700,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# Agregar hover effects para los botones
app.clientside_callback(
    """
    function(n_clicks) {
        document.querySelector('#select-all').onmouseover = function() {
            this.style.backgroundColor = '#45a049';
        }
        document.querySelector('#select-all').onmouseout = function() {
            this.style.backgroundColor = '#4CAF50';
        }
        document.querySelector('#deselect-all').onmouseover = function() {
            this.style.backgroundColor = '#da190b';
        }
        document.querySelector('#deselect-all').onmouseout = function() {
            this.style.backgroundColor = '#f44336';
        }
        return '';
    }
    """,
    Output('select-all', 'style'),
    Input('select-all', 'n_clicks')
)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8000, debug=True)