import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objects as go

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define frequency range (log scale)
frequencies = np.logspace(-2, 6, num=1000)
omega = 2 * np.pi * frequencies

# Function to calculate impedance
def randles_impedance(R_s, R_ct, C_dl, sigma):
    Z_w = sigma / np.sqrt(omega) * (1 - 1j)  # Warburg impedance
    Z_ct = 1 / (1 / R_ct + 1j * omega * C_dl)  # Charge transfer + capacitor
    Z_total = R_s + Z_ct + Z_w  # Total impedance
    return Z_total

# Layout: Sidebar on the left, graphs on the right
app.layout = dbc.Container([
    dbc.Row([
        # Sidebar for controls
        dbc.Col([
            html.H4("Randles Circuit Parameters"),
            
            html.Label("Solution Resistance (R_s) [Ω]"),
            dcc.Slider(id='Rs', min=0, max=100, step=1, value=50,
                       marks={0: '0', 100: '100'}),

            html.Label("Charge Transfer Resistance (R_ct) [Ω]"),
            dcc.Slider(id='Rct', min=0, max=1000, step=10, value=200,
                       marks={0: '0', 1000: '1000'}),

            html.Label("Double Layer Capacitance (C_dl) [F]"),
            dcc.Slider(id='Cdl', min=1e-6, max=1e-3, step=1e-6, value=1e-5,
                       marks={1e-6: '1μF', 1e-3: '1mF'}),

            html.Label("Warburg Coefficient (σ)"),
            dcc.Slider(id='sigma', min=0, max=50, step=1, value=10,
                       marks={0: '0', 50: '50'}),

        ], width=3, style={'background-color': '#f8f9fa', 'padding': '20px', 'border-right': '1px solid #ddd'}),

        # Graphs on the right
        dbc.Col([
            dbc.Row([
                dcc.Graph(id='nyquist-plot', style={'height': '45vh'})
            ]),
            dbc.Row([
                dcc.Graph(id='bode-plot', style={'height': '45vh'})
            ])
        ], width=9)
    ])
], fluid=True)

# Define callback to update plots
@app.callback(
    [Output('nyquist-plot', 'figure'), Output('bode-plot', 'figure')],
    [Input('Rs', 'value'), Input('Rct', 'value'), Input('Cdl', 'value'), Input('sigma', 'value')]
)
def update_plots(Rs, Rct, Cdl, sigma):
    Z = randles_impedance(Rs, Rct, Cdl, sigma)
    
    # Nyquist Plot (Scatter)
    fig_nyquist = go.Figure()
    fig_nyquist.add_trace(go.Scatter(x=Z.real, y=-Z.imag, mode='markers', name='Nyquist Plot'))
    fig_nyquist.update_layout(title="Nyquist Diagram", xaxis_title="Z' [Ω]", yaxis_title="-Z'' [Ω]")

    # Bode Plot (Magnitude and Phase vs Frequency, Scatter)
    fig_bode = go.Figure()
    fig_bode.add_trace(go.Scatter(x=frequencies, y=20*np.log10(abs(Z)), mode='markers', name='Magnitude'))
    fig_bode.add_trace(go.Scatter(x=frequencies, y=np.angle(Z, deg=True), mode='markers', name='Phase'))
    fig_bode.update_layout(title="Bode Diagram", xaxis_title="Frequency [Hz]", 
                           yaxis_title="Magnitude [dB] / Phase [°]", xaxis_type="log")

    return fig_nyquist, fig_bode

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use Render's port or default to 10000
    app.run_server(debug=True, host='0.0.0.0', port=port)