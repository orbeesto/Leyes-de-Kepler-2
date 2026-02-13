import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Marte: Sentido Antihorario", layout="wide")

st.title("🔭 Órbitas en Sentido Antihorario")
st.write("Simulación corregida: Los planetas ahora avanzan de derecha a izquierda por el frente (sentido real).")

# --- 1. GESTIÓN DEL ESTADO ---
if 'dias' not in st.session_state:
    st.session_state.dias = 0
if 'ejecutando' not in st.session_state:
    st.session_state.ejecutando = False

# --- 2. CONTROLES ---
col1, col2, col3, _ = st.columns([1, 1, 1, 4])
with col1:
    if st.button("▶️ Iniciar"): st.session_state.ejecutando = True
with col2:
    if st.button("⏸️ Pausar"): st.session_state.ejecutando = False
with col3:
    if st.button("🔄 Reiniciar"):
        st.session_state.dias = 0
        st.session_state.ejecutando = False
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

def get_3d_pos(p_name, t):
    p = planets[p_name]
    a, e, i, Om, w = p['a'], p['e'], np.radians(p['i']), np.radians(p['Omega']), np.radians(p['w'])
    
    # IMPORTANTE: M aumenta positivamente para giro antihorario
    M = np.radians(p['n'] * t) 
    E = solve_kepler(M, e)
    
    # Coordenadas en plano orbital
    x_o = a * (np.cos(E) - e)
    y_o = a * (np.sqrt(1 - e**2) * np.sin(E))
    
    # Matrices de rotación (Conversión a coordenadas eclípticas)
    X = x_o*(np.cos(Om)*np.cos(w) - np.sin(Om)*np.sin(w)*np.cos(i)) - y_o*(np.cos(Om)*np.sin(w) + np.sin(Om)*np.cos(w)*np.cos(i))
    Y = x_o*(np.sin(Om)*np.cos(w) + np.cos(Om)*np.sin(w)*np.cos(i)) + y_o*(np.sin(Om)*np.sin(w) - np.cos(Om)*np.cos(w)*np.cos(i))
    Z = x_o*(np.sin(w)*np.sin(i)) + y_o*(np.cos(w)*np.sin(i))
    return X, Y, Z

# --- 4. RENDERIZADO ---
def crear_figura(t_actual):
    fig = go.Figure()
    
    # Sol
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                               marker=dict(size=15, color='yellow', symbol='diamond'), name="Sol"))

    for name, data in planets.items():
        # Órbita (trayectoria)
        orbit_pts = np.array([get_3d_pos(name, d) for d in np.linspace(0, 700, 300)])
        fig.add_trace(go.Scatter3d(x=orbit_pts[:,0], y=orbit_pts[:,1], z=orbit_pts[:,2], 
                                   mode='lines', line=dict(color=data['color'], width=3), name=f"Órbita {name}"))
        
        # Planeta actual
        px, py, pz = get_3d_pos(name, t_actual)
        fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode='markers', 
                                   marker=dict(size=12, color=data['color']), name=name))

    fig.update_layout(
        scene=dict(
            aspectmode='data', bgcolor="black",
            # Aseguramos que la vista inicial sea desde "arriba" para notar el giro
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.5)),
            xaxis=dict(range=[-2, 2], title="X (UA)"),
            yaxis=dict(range=[-2, 2], title="Y (UA)"),
            zaxis=dict(range=[-0.5, 0.5], title="Z (UA)")
        ),
        paper_bgcolor="black", font=dict(color="white"),
        legend=dict(font=dict(size=16), bgcolor="rgba(0,0,0,0.5)")
    )
    return fig

espacio_grafico = st.empty()

if st.session_state.ejecutando:
    while st.session_state.ejecutando:
        st.session_state.dias += 3 # Velocidad del tiempo
        figura = crear_figura(st.session_state.dias)
        espacio_grafico.plotly_chart(figura, use_container_width=True)
        time.sleep(0.04) 
else:
    figura = crear_figura(st.session_state.dias)
    espacio_grafico.plotly_chart(figura, use_container_width=True)

st.write(f"📅 Días desde inicio: {int(st.session_state.dias)}")
