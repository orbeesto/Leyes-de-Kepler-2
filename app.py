import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Marte-Tierra Pro", layout="wide")

st.title("🔭 Órbita 3D: La inclinación de Marte")
st.write("Nota cómo Marte 'perfora' el plano de la Tierra (la Eclíptica) debido a sus 1.85° de inclinación.")

# --- DATOS TÉCNICOS ---
planets = {
    'Tierra': {'a': 1.0, 'e': 0.0167, 'i': 0.0, 'Omega': 0.0, 'w': 102.9, 'n': 0.9856, 'color': '#1f77b4'},
    'Marte': {'a': 1.523, 'e': 0.0934, 'i': 1.85, 'Omega': 49.5, 'w': 286.5, 'n': 0.5240, 'color': '#ff7f0e'}
}

def solve_kepler(M, e):
    E = M
    for _ in range(10):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E

def get_3d_pos(p_name, days):
    p = planets[p_name]
    a, e, i, Om, w = p['a'], p['e'], np.radians(p['i']), np.radians(p['Omega']), np.radians(p['w'])
    M = np.radians(p['n'] * days)
    E = solve_kepler(M, e)
    
    x_o = a * (np.cos(E) - e)
    y_o = a * (np.sqrt(1 - e**2) * np.sin(E))
    
    # Transformación completa
    X = x_o*(np.cos(Om)*np.cos(w) - np.sin(Om)*np.sin(w)*np.cos(i)) - y_o*(np.cos(Om)*np.sin(w) + np.sin(Om)*np.cos(w)*np.cos(i))
    Y = x_o*(np.sin(Om)*np.cos(w) + np.cos(Om)*np.sin(w)*np.cos(i)) + y_o*(np.sin(Om)*np.sin(w) - np.cos(Om)*np.cos(w)*np.cos(i))
    Z = x_o*(np.sin(w)*np.sin(i)) + y_o*(np.cos(w)*np.sin(i))
    return X, Y, Z

dias = st.sidebar.slider("Días transcurridos", 0, 1000, 0)

fig = go.Figure()

# 1. DIBUJAR EL PLANO DE LA ECLÍPTICA (Referencia Z=0)
grid_range = np.linspace(-2, 2, 10)
x_grid, y_grid = np.meshgrid(grid_range, grid_range)
z_grid = np.zeros_like(x_grid)
fig.add_trace(go.Surface(x=x_grid, y=y_grid, z=z_grid, opacity=0.1, showscale=False, name="Eclíptica (Tierra)"))

# 2. DIBUJAR SOL Y PLANETAS
fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=12, color='yellow', symbol='diamond'), name="Sol"))

for name, data in planets.items():
    orbit_days = np.linspace(0, 700, 400)
    pts = np.array([get_3d_pos(name, d) for d in orbit_days])
    
    # Órbita
    fig.add_trace(go.Scatter3d(x=pts[:,0], y=pts[:,1], z=pts[:,2], mode='lines', line=dict(color=data['color'], width=4), name=f"Órbita {name}"))
    
    # Planeta actual
    cx, cy, cz = get_3d_pos(name, dias)
    fig.add_trace(go.Scatter3d(x=[cx], y=[cy], z=[cz], mode='markers', 
                               marker=dict(size=8, color=data['color']), 
                               hovertext=f"Z: {cz:.4f} UA", # Muestra la altura exacta
                               name=name))

# 3. CONFIGURACIÓN CRÍTICA: ESCALA IGUAL
fig.update_layout(
    scene=dict(
        aspectmode='data', # ESTO HACE QUE 1 UA EN Z SE VEA IGUAL A 1 UA EN X/Y
        xaxis=dict(range=[-2, 2], backgroundcolor="black"),
        yaxis=dict(range=[-2, 2], backgroundcolor="black"),
        zaxis=dict(range=[-0.5, 0.5], backgroundcolor="black"), # Enfocamos el eje Z
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.5)) # Ángulo inicial inclinado para ver el relieve
    ),
    paper_bgcolor="black",
    font=dict(color="white"),
    margin=dict(l=0, r=0, b=0, t=0)
)

st.plotly_chart(fig, use_container_width=True)
