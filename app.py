import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Configuración de la página
st.set_page_config(page_title="Simulador Marte: Animación Automática", layout="wide")

st.title("🔭 Simulador Astronómico: Tierra y Marte en Movimiento")
st.write("Controla la animación con los botones de abajo para observar la mecánica orbital en tiempo real.")

# --- 1. GESTIÓN DEL ESTADO (Session State) ---
# Necesitamos esto para que Streamlit recuerde el día y si debe estar animando
if 'dias' not in st.session_state:
    st.session_state.dias = 0
if 'ejecutando' not in st.session_state:
    st.session_state.ejecutando = False

# --- 2. BOTONES DE CONTROL ---
col1, col2, col3, _ = st.columns([1, 1, 1, 4])

with col1:
    if st.button("▶️ Iniciar"):
        st.session_state.ejecutando = True
with col2:
    if st.button("⏸️ Pausar"):
        st.session_state.ejecutando = False
with col3:
    if st.button("🔄 Reiniciar"):
        st.session_state.dias = 0
        st.session_state.ejecutando = False
        st.rerun()

# --- 3. PARÁMETROS ORBITALES ---
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
    M = np.radians(p['n'] * t)
    E = solve_kepler(M, e)
    
    # Coordenadas en plano orbital
    x_o = a * (np.cos(E) - e)
    y_o = a * (np.sqrt(1 - e**2) * np.sin(E))
    
    # Rotación al sistema 3D
    X = x_o*(np.cos(Om)*np.cos(w) - np.sin(Om)*np.sin(w)*np.cos(i)) - y_o*(np.cos(Om)*np.sin(w) + np.sin(Om)*np.cos(w)*np.cos(i))
    Y = x_o*(np.sin(Om)*np.cos(w) + np.cos(Om)*np.sin(w)*np.cos(i)) + y_o*(np.sin(Om)*np.sin(w) - np.cos(Om)*np.cos(w)*np.cos(i))
    Z = x_o*(np.sin(w)*np.sin(i)) + y_o*(np.cos(w)*np.sin(i))
    return X, Y, Z

# --- 4. FUNCIÓN PARA GENERAR EL GRÁFICO ---
def crear_figura(t_actual):
    fig = go.Figure()
    
    # Sol
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', 
                               marker=dict(size=15, color='yellow', symbol='diamond'), name="Sol"))

    for name, data in planets.items():
        # Órbita completa (referencia)
        orbit_pts = np.array([get_3d_pos(name, d) for d in np.linspace(0, 700, 300)])
        fig.add_trace(go.Scatter3d(x=orbit_pts[:,0], y=orbit_pts[:,1], z=orbit_pts[:,2], 
                                   mode='lines', line=dict(color=data['color'], width=4), name=f"Órbita {name}"))
        # Planeta en posición T
        px, py, pz = get_3d_pos(name, t_actual)
        fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode='markers', 
                                   marker=dict(size=12, color=data['color']), name=name))

    fig.update_layout(
        scene=dict(
            aspectmode='data', bgcolor="black",
            xaxis=dict(range=[-2, 2], title="X (UA)"),
            yaxis=dict(range=[-2, 2], title="Y (UA)"),
            zaxis=dict(range=[-0.2, 0.2], title="Z (UA)")
        ),
        paper_bgcolor="black", font=dict(color="white"),
        margin=dict(l=0, r=0, b=0, t=0),
        legend=dict(font=dict(size=16), bgcolor="rgba(0,0,0,0.5)")
    )
    return fig

# --- 5. BUCLE DE RENDERIZADO ---
# Usamos un contenedor vacío para que el gráfico se actualice en el mismo lugar
espacio_grafico = st.empty()

if st.session_state.ejecutando:
    # Mientras el estado sea 'ejecutando', el bucle actualiza el tiempo y el dibujo
    while st.session_state.ejecutando:
        st.session_state.dias += 5  # Incremento de tiempo por cada cuadro
        figura = crear_figura(st.session_state.dias)
        espacio_grafico.plotly_chart(figura, use_container_width=True)
        time.sleep(0.05)  # Breve pausa para controlar la velocidad
else:
    # Si está en pausa, solo dibuja el estado actual
    figura = crear_figura(st.session_state.dias)
    espacio_grafico.plotly_chart(figura, use_container_width=True)

st.write(f"**Día de la simulación:** {st.session_state.dias}")
