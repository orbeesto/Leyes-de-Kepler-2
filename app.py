import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Marte: Órbita Continua", layout="wide")

st.title("🔭 Órbita Continua: Tierra y Marte")
st.write("Animación suavizada con intervalos de tiempo reducidos para mayor realismo.")

# --- 1. ESTADO DE SESIÓN ---
if 'dias' not in st.session_state:
    st.session_state.dias = 0.0
if 'ejecutando' not in st.session_state:
    st.session_state.ejecutando = False

# --- 2. CONTROLES ---
col1, col2, col3, _ = st.columns([1, 1, 1, 4])
with col1:
    if st.button("▶️ Inicio"): st.session_state.ejecutando = True
with col2:
    if st.button("⏸️ Pausa"): st.session_state.ejecutando = False
with col3:
    if st.button("🔄 Reinicio"):
        st.session_state.dias = 0.0
        st.session_state.ejecutando = False
        st.rerun()

# --- 3. DATOS TÉCNICOS ---
planets = {
    'Tierra': {'a': 1.0, 'e': 0.0167, 'i': 0.0, 'Omega': 0.0, 'w': 102.9, 'n': 0.9856, 'color': '#00BFFF'},
    'Marte': {'a': 1.523, 'e': 0.0934, 'i': 1.85, 'Omega': 49.5, 'w': 286.5, 'n': 0.5240, 'color': '#FF4500'}
}

def solve_kepler(M, e):
    E = M
    for _ in range(6): # Reducido a 6 iteraciones para velocidad; suficiente precisión visual
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E

def get_3d_pos(p_name, t):
    p = planets[p_name]
    a, e, i, Om, w = p['a'], p['e'], np.radians(p['i']), np.radians(p['Omega']), np.radians(p['w'])
    M = np.radians(p['n'] * t)
    E = solve_kepler(M, e)
    
    # Ecuaciones de posición estándar
    x_e = a * (np.cos(E) - e)
    y_e = a * (np.sqrt(1 - e**2) * np.sin(E))
    
    # Rotaciones 3D
    X = (np.cos(Om)*np.cos(w+E) - np.sin(Om)*np.sin(w+E)*np.cos(i)) * a*(1-e*np.cos(E))
    Y = (np.sin(Om)*np.cos(w+E) + np.cos(Om)*np.sin(w+E)*np.cos(i)) * a*(1-e*np.cos(E))
    Z = (np.sin(w+E)*np.sin(i)) * a*(1-e*np.cos(E))
    return X, Y, Z

# --- 4. RENDERIZADO OPTIMIZADO ---
def crear_figura(t_actual):
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                               marker=dict(size=12, color='yellow'), name="Sol"))

    for name, data in planets.items():
        # Órbita con menos puntos para ganar FPS
        orbit_days = np.linspace(0, 687 if name=='Marte' else 365, 150)
        pts = np.array([get_3d_pos(name, d) for d in orbit_days])
        fig.add_trace(go.Scatter3d(x=pts[:,0], y=pts[:,1], z=pts[:,2], 
                                   mode='lines', line=dict(color=data['color'], width=3), 
                                   hoverinfo='none', showlegend=True, name=name))
        
        # Planeta
        px, py, pz = get_3d_pos(name, t_actual)
        fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode='markers', 
                                   marker=dict(size=10, color=data['color']), showlegend=False))

    fig.update_layout(
        scene=dict(aspectmode='data', bgcolor="black",
                   xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                   camera=dict(eye=dict(x=1.3, y=1.3, z=1.3))),
        paper_bgcolor="black", margin=dict(l=0, r=0, b=0, t=0), showlegend=True,
        legend=dict(font=dict(color="white", size=14))
    )
    return fig

# --- 5. BUCLE DE ALTA VELOCIDAD ---
placeholder = st.empty()

if st.session_state.ejecutando:
    while st.session_state.ejecutando:
        st.session_state.dias += 0.8  # Paso de tiempo pequeño = Movimiento suave
        fig = crear_figura(st.session_state.dias)
        # El parámetro 'config' ayuda a desactivar barras de herramientas pesadas
        placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        time.sleep(0.01) # Pausa mínima para fluidez
else:
    fig = crear_figura(st.session_state.dias)
    placeholder.plotly_chart(fig, use_container_width=True)

st.write(f"⏱️ Tiempo transcurrido: {int(st.session_state.dias)} días")
