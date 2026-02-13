import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Marte: Alta Visibilidad", layout="wide")

# Título con estilo
st.markdown("<h1 style='text-align: center; color: white;'>🔭 Laboratorio de Mecánica Celeste</h1>", unsafe_allow_html=True)

# --- 1. ESTADO DE SESIÓN ---
if 'dias' not in st.session_state:
    st.session_state.dias = 0.0
if 'ejecutando' not in st.session_state:
    st.session_state.ejecutando = False

# --- 2. CONTROLES Y MÉTRICA (En la misma fila para visibilidad) ---
col_ctrl, col_met1, col_met2 = st.columns([2, 2, 2])

with col_ctrl:
    c1, c2, c3 = st.columns(3)
    if c1.button("▶️ Inicio"): st.session_state.ejecutando = True
    if c2.button("⏸️ Pausa"): st.session_state.ejecutando = False
    if c3.button("🔄 Reset"):
        st.session_state.dias = 0.0
        st.session_state.ejecutando = False
        st.rerun()

with col_met1:
    # MÉTRICA DE TIEMPO CON LETRA GRANDE
    st.metric(label="TIEMPO TRANSCURRIDO", value=f"{int(st.session_state.dias)} Días")

# --- 3. DATOS TÉCNICOS ---
planets = {
    'Tierra': {'a': 1.0, 'e': 0.0167, 'i': 0.0, 'Omega': 0.0, 'w': 102.9, 'n': 0.9856, 'color': '#00BFFF'},
    'Marte': {'a': 1.523, 'e': 0.0934, 'i': 1.85, 'Omega': 49.5, 'w': 286.5, 'n': 0.5240, 'color': '#FF4500'}
}

def solve_kepler(M, e):
    E = M
    for _ in range(6):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E

def get_3d_pos(p_name, t):
    p = planets[p_name]
    a, e, i, Om, w = p['a'], p['e'], np.radians(p['i']), np.radians(p['Omega']), np.radians(p['w'])
    M = np.radians(p['n'] * t)
    E = solve_kepler(M, e)
    X = (np.cos(Om)*np.cos(w+E) - np.sin(Om)*np.sin(w+E)*np.cos(i)) * a*(1-e*np.cos(E))
    Y = (np.sin(Om)*np.cos(w+E) + np.cos(Om)*np.sin(w+E)*np.cos(i)) * a*(1-e*np.cos(E))
    Z = (np.sin(w+E)*np.sin(i)) * a*(1-e*np.cos(E))
    return X, Y, Z

# --- 4. RENDERIZADO CON ETIQUETAS GRANDES ---
def crear_figura(t_actual):
    fig = go.Figure()
    
    # SOL con etiqueta
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers+text', 
                               marker=dict(size=15, color='yellow'),
                               text=["SOL"], textposition="top center",
                               textfont=dict(size=24, color="yellow"), name="Sol"))

    for name, data in planets.items():
        # Órbita
        orbit_days = np.linspace(0, 700, 150)
        pts = np.array([get_3d_pos(name, d) for d in orbit_days])
        fig.add_trace(go.Scatter3d(x=pts[:,0], y=pts[:,1], z=pts[:,2], 
                                   mode='lines', line=dict(color=data['color'], width=4), 
                                   hoverinfo='none', showlegend=False))
        
        # PLANETA con etiqueta dinámica
        px, py, pz = get_3d_pos(name, t_actual)
        fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode='markers+text', 
                                   marker=dict(size=12, color=data['color']),
                                   text=[name.upper()], textposition="top center",
                                   textfont=dict(size=22, color=data['color']), name=name))

    fig.update_layout(
        scene=dict(aspectmode='data', bgcolor="black",
                   xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                   camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))),
        paper_bgcolor="black", margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# --- 5. BUCLE DE ANIMACIÓN ---
placeholder = st.empty()

if st.session_state.ejecutando:
    while st.session_state.ejecutando:
        st.session_state.dias += 1.0 # Paso de tiempo suave
        fig = crear_figura(st.session_state.dias)
        placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        time.sleep(0.02)
        # Forzamos la actualización de la métrica de tiempo
        st.rerun() 
else:
    fig = crear_figura(st.session_state.dias)
    placeholder.plotly_chart(fig, use_container_width=True)
