import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Marte: Sentido Real", layout="wide")

st.title("🔭 Sincronía Orbital: Tierra y Marte")
st.write("Simulación corregida: Ambos planetas orbitan en sentido antihorario (visto desde el polo norte eclíptico).")

if 'dias' not in st.session_state:
    st.session_state.dias = 0
if 'ejecutando' not in st.session_state:
    st.session_state.ejecutando = False

# --- CONTROLES ---
col1, col2, col3, _ = st.columns([1, 1, 1, 4])
with col1:
    if st.button("▶️ Iniciar"): st.session_state.ejecutando = True
with col2:
    if st.button("⏸️ Pausar"): st.session_state.ejecutando = False
with col3:
    if st.button("🔄 Reinicio"):
        st.session_state.dias = 0
        st.session_state.ejecutando = False
        st.rerun()

# --- DATOS TÉCNICOS ---
planets = {
    'Tierra': {'a': 1.0, 'e': 0.0167, 'i': 0.0, 'Omega': 0.0, 'w': 102.9, 'n': 0.9856, 'color': '#00BFFF'},
    'Marte': {'a': 1.523, 'e': 0.0934, 'i': 1.85, 'Omega': 49.5, 'w': 286.5, 'n': 0.5240, 'color': '#FF4500'}
}

def solve_kepler(M, e):
    E = M
    for _ in range(10):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E

def get_3d_pos(p_name, t):
    p = planets[p_name]
    a, e, i, Om, w = p['a'], p['e'], np.radians(p['i']), np.radians(p['Omega']), np.radians(p['w'])
    
    # M aumenta con t, asegurando sentido antihorario
    M = np.radians(p['n'] * t) 
    E = solve_kepler(M, e)
    
    # Posición en el plano de la elipse
    x_elipse = a * (np.cos(E) - e)
    y_elipse = a * (np.sqrt(1 - e**2) * np.sin(E))
    
    # Aplicación de las rotaciones de Euler para llevar al espacio 3D (Eclíptica)
    # Esta es la parte crítica para que el sentido sea el correcto en los 3 ejes
    X = (np.cos(Om) * np.cos(w + E) - np.sin(Om) * np.sin(w + E) * np.cos(i)) * a * (1 - e * np.cos(E))
    Y = (np.sin(Om) * np.cos(w + E) + np.cos(Om) * np.sin(w + E) * np.cos(i)) * a * (1 - e * np.cos(E))
    Z = (np.sin(w + E) * np.sin(i)) * a * (1 - e * np.cos(E))
    
    return X, Y, Z

def crear_figura(t_actual):
    fig = go.Figure()
    
    # El Sol
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                               marker=dict(size=14, color='yellow', symbol='diamond'), name="Sol"))

    for name, data in planets.items():
        # Órbita
        orbit_days = np.linspace(0, 700, 400)
        pts = np.array([get_3d_pos(name, d) for d in orbit_days])
        fig.add_trace(go.Scatter3d(x=pts[:,0], y=pts[:,1], z=pts[:,2], 
                                   mode='lines', line=dict(color=data['color'], width=4), name=f"Órbita {name}"))
        
        # Planeta
        px, py, pz = get_3d_pos(name, t_actual)
        fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode='markers', 
                                   marker=dict(size=12, color=data['color']), name=name))

    fig.update_layout(
        scene=dict(
            aspectmode='data', bgcolor="black",
            xaxis=dict(range=[-2, 2], title="X (UA)"),
            yaxis=dict(range=[-2, 2], title="Y (UA)"),
            zaxis=dict(range=[-0.5, 0.5], title="Z (UA)"),
            camera=dict(eye=dict(x=0, y=0, z=2.5)) # Vista cenital para confirmar sentido
        ),
        paper_bgcolor="black", font=dict(color="white"),
        legend=dict(font=dict(size=16), bgcolor="rgba(0,0,0,0.5)")
    )
    return fig

# --- BUCLE DE ANIMACIÓN ---
placeholder = st.empty()

if st.session_state.ejecutando:
    while st.session_state.ejecutando:
        st.session_state.dias += 2 # Velocidad moderada
        fig = crear_figura(st.session_state.dias)
        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(0.05)
else:
    fig = crear_figura(st.session_state.dias)
    placeholder.plotly_chart(fig, use_container_width=True)

st.write(f"📅 Tiempo: {int(st.session_state.dias)} días")
