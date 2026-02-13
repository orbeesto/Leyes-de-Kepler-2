import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Laboratorio de Marte", layout="wide")

# 1. TÍTULO Y DESLIZADOR EN EL CUERPO PRINCIPAL
st.title("🔭 Mecánica Celeste: Nodos Orbitales")
st.write("Mueve el deslizador para ver cómo Marte y la Tierra avanzan en sus órbitas.")

# Colocamos el slider aquí para que sea visible siempre en tu blog
dias = st.slider("Días transcurridos (Control de Tiempo)", 0, 2000, 0, help="Desliza para mover los planetas")

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

fig = go.Figure()

# 2. PLANO DE REFERENCIA
grid = np.linspace(-2, 2, 10)
x_g, y_g = np.meshgrid(grid, grid)
fig.add_trace(go.Surface(x=x_g, y=y_g, z=np.zeros_like(x_g), opacity=0.15, showscale=False, name="Plano Eclíptico"))

# 3. CÁLCULO DE NODOS
node1 = get_3d_pos('Marte', -planets['Marte']['w'], is_mean_anomaly=False)
node2 = get_3d_pos('Marte', 180-planets['Marte']['w'], is_mean_anomaly=False)

fig.add_trace(go.Scatter3d(x=[node1[0], node2[0]], y=[node1[1], node2[1]], z=[node1[2], node2[2]],
                         mode='lines+markers', line=dict(color='white', width=6, dash='dash'), 
                         marker=dict(size=7, color='white'), name="Línea de Nodos"))

# 4. ÓRBITAS Y PLANETAS
for name, data in planets.items():
    pts = np.array([get_3d_pos(name, d * data['n']) for d in np.linspace(0, 700, 500)])
    fig.add_trace(go.Scatter3d(x=pts[:,0], y=pts[:,1], z=pts[:,2], mode='lines', 
                               line=dict(color=data['color'], width=5), name=f"Órbita {name}"))
    
    cx, cy, cz = get_3d_pos(name, dias * data['n'])
    fig.add_trace(go.Scatter3d(x=[cx], y=[cy], z=[cz], mode='markers', 
                               marker=dict(size=12, color=data['color']), name=name))

# 5. AJUSTES FINALES
fig.update_layout(
    scene=dict(aspectmode='data', bgcolor="black",
               xaxis=dict(title="X (UA)", color="yellow"),
               yaxis=dict(title="Y (UA)", color="yellow"),
               zaxis=dict(title="Z (UA)", color="yellow")),
    paper_bgcolor="black",
    legend=dict(font=dict(size=18, color="white"), bgcolor="rgba(0,0,0,0.5)"),
    margin=dict(l=0, r=0, b=0, t=0)
)

st.plotly_chart(fig, use_container_width=True)
