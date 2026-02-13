import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Marte: Animación Pro", layout="wide")

st.title("🔭 Simulador Astronómico Profesional: Tierra y Marte")
st.write("Usa los botones para controlar el flujo del tiempo astronómico.")

# --- 1. LÓGICA DE ESTADO DE SESIÓN ---
if 'dias' not in st.session_state:
    st.session_state.dias = 0
if 'corriendo' not in st.session_state:
    st.session_state.corriendo = False

# --- 2. CONTROLES ---
col1, col2, col3, _ = st.columns([1, 1, 1, 3])

with col1:
    if st.button("▶️ Inicio"):
        st.session_state.corriendo = True
with col2:
    if st.button("⏸️ Pausa"):
        st.session_state.corriendo = False
with col3:
    if st.button("🔄 Reinicio"):
        st.session_state.dias = 0
        st.session_state.corriendo = False
        st.rerun()

# --- 3. DATOS TÉCNICOS ---
planets = {
    'Tierra': {'a': 1.0, 'e': 0.0167, 'i': 0.0, 'Omega': 0.0, 'w': 102.9, 'n': 0.9856, 'color': '#00BFFF'},
    'Marte': {'a': 1.523, 'e': 0.0934, 'i': 1.85, 'Omega': 49.5, 'w': 286.5, 'n': 0.5240, 'color': '#FF4500'}
}

def solve_kepler(M, e):
    E = M
    for _ in range(10):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E

def get_3d_pos(p_name, angle_deg, is_mean_anomaly=True):
    p = planets[p_name]
    a, e, i, Om, w = p['a'], p['e'], np.radians(p['i']), np.radians(p['Omega']), np.radians(p['w'])
    if is_mean_anomaly:
        M = np.radians(angle_deg)
        E = solve_kepler(M, e)
    else:
        E = angle_deg 
    x_o = a * (np.cos(E) - e)
    y_o = a * (np.sqrt(1 - e**2) * np.sin(E))
    X = x_o*(np.cos(Om)*np.cos(w) - np.sin(Om)*np.sin(w)*np.cos(i)) - y_o*(np.cos(Om)*np.sin(w) + np.sin(Om)*np.cos(w)*np.cos(i))
    Y = x_o*(np.sin(Om)*np.cos(w) + np.cos(Om)*np.sin(w)*np.cos(i)) + y_o*(np.sin(Om)*np.sin(w) - np.cos(Om)*np.cos(w)*np.cos(i))
    Z = x_o*(np.sin(w)*np.sin(i)) + y_o*(np.cos(w)*np.sin(i))
    return X, Y, Z

# --- 4. FUNCIÓN DE DIBUJO ---
def dibujar_escena(t):
    fig = go.Figure()
    
    # Sol
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                               marker=dict(size=12, color='yellow', symbol='diamond'), name="Sol"))

    for name, data in planets.items():
        # Órbita
        orbit_days = np.linspace(0, 700, 300)
        pts = np.array([get_3d_pos(name, d * data['n']) for d in orbit_days])
        fig.add_trace(go.Scatter3d(x=pts[:,0], y=pts[:,1], z=pts[:,2], mode='lines', 
                                   line=dict(color=data['color'], width=4), name=f"Órbita {name}"))
        # Planeta
        cx, cy, cz = get_3d_pos(name, t * data['n'])
        fig.add_trace(go.Scatter3d(x=[cx], y=[cy], z=[cz], mode='markers', 
                                   marker=dict(size=10, color=data['color']), name=name))

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            bgcolor="black",
            xaxis=dict(range=[-2, 2], title="X (UA)"),
            yaxis=dict(range=[-2, 2], title="Y (UA)"),
            zaxis=dict(range=[-0.5, 0.5], title="Z (UA)")
        ),
        paper_bgcolor="black",
        font=dict(color="white"),
        margin=dict(l=0, r=0, b=0, t=0),
        # CORRECCIÓN AQUÍ: El tamaño de la fuente debe ir dentro de 'font'
        legend=dict(font=dict(size=16)) 
    )
    return fig

# --- 5. RENDERIZADO Y ANIMACIÓN ---
placeholder = st.empty()

if st.session_state.corriendo:
    while st.session_state.corriendo:
        st.session_state.dias += 4
        fig = dibujar_escena(st.session_state.dias)
        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)
else:
    fig = dibujar_escena(st.session_state.dias)
    placeholder.plotly_chart(fig, use_container_width=True)

st.sidebar.metric("Días transcurridos", int(st.session_state.dias))
