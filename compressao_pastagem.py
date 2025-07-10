

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Simulador de Compressão e Avaliação de Pastagens")

st.markdown("""
Este modelo estima:
- **Compressão da vegetação** com base no peso do prato e rigidez da pastagem;
- **Biomassa seca (kg MS/ha)** e **proteína bruta (%)** com base em NDVI e compressão.

Os coeficientes podem ser ajustados manualmente. Valores iniciais foram calibrados com base na literatura:
- Biomassa: Calvão & Palmeirim (2004)
- Proteína: Garroutte et al. (2016)
""")

# Entradas básicas
peso = st.slider("Peso do prato (kgf)", 0.5, 3.0, 1.5, step=0.1)
rigidez_selecionada = st.selectbox(
    "Tipo de pastagem / rigidez (N/cm)",
    options=[
        ("Pastagem muito jovem (0.5 N/cm)", 0.5),
        ("Pastagem jovem (0.75 N/cm)", 0.75),
        ("Pastagem média (1.5 N/cm)", 1.5),
        ("Pastagem densa (3.0 N/cm)", 3.0)
    ],
    format_func=lambda x: x[0]
)[1]
ndvi = st.slider("NDVI medido", 0.2, 0.9, 0.65, step=0.01)

# Coeficientes personalizáveis
st.subheader("Coeficientes do Modelo")

col1, col2, col3 = st.columns(3)
a = col1.number_input("a (NDVI ×)", value=6000)
b = col2.number_input("b (Compressão ×)", value=150)
c = col3.number_input("c (Constante)", value=500)

col4, col5 = st.columns(2)
d = col4.number_input("d (NDVI ×)", value=8.0)
e = col5.number_input("e (Constante)", value=4.0)

st.caption("Fontes:")
st.markdown("- **Biomassa:** Calvão & Palmeirim (2004), *Mapping Mediterranean scrub with satellite imagery: biomass estimation and spectral behaviour* (https://doi.org/10.1080/01431160310001654978)")
st.markdown("- **Proteína Bruta:** Garroutte et al. (2016), *Using NDVI and EVI to Map Spatiotemporal Variation in the Biomass and Quality of Forage for Migratory Elk in the Greater Yellowstone Ecosystem* (https://www.mdpi.com/2072-4292/8/5/404)")

# Cálculos
forca_n = peso * 9.81
compressao_cm = forca_n / rigidez_selecionada
biomassa = a * ndvi + b * compressao_cm + c
proteina = d * ndvi + e

st.subheader("Resultados Estimados")
col1, col2, col3 = st.columns(3)
col1.metric("Compressão (cm)", f"{compressao_cm:.2f}")
col2.metric("Biomassa (kg MS/ha)", f"{biomassa:.0f}")
col3.metric("Proteína bruta (%)", f"{proteina:.2f}")

# Gráfico 1: Compressão vs Peso
st.subheader("Gráfico 1 – Compressão vs Peso para diferentes tipos de pastagem")
pesos = np.linspace(0.5, 3.0, 100)
rigidezes = {
    "Muito jovem (0.5)": 0.5,
    "Jovem (0.75)": 0.75,
    "Média (1.5)": 1.5,
    "Densa (3.0)": 3.0
}
fig1 = go.Figure()
for nome, k in rigidezes.items():
    compressao = (pesos * 9.81) / k
    fig1.add_trace(go.Scatter(x=pesos, y=compressao, mode='lines', name=nome))

fig1.update_layout(
    title="Compressão estimada por tipo de pastagem",
    xaxis_title="Peso (kgf)",
    yaxis_title="Compressão (cm)",
    hovermode="x unified"
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: NDVI x Compressão -> Biomassa e Proteína
st.subheader("Gráfico 2 – Biomassa e Proteína por NDVI e Compressão")

ndvi_vals = np.linspace(0.0, 1.0, 50)
comp_vals = np.linspace(0.5, 8.0, 50)
NDVI_grid, COMP_grid = np.meshgrid(ndvi_vals, comp_vals)
BIOM_grid = a * NDVI_grid + b * COMP_grid + c
PROT_grid = d * NDVI_grid + e

fig2 = go.Figure()
fig2.add_trace(go.Surface(z=BIOM_grid, x=NDVI_grid, y=COMP_grid, colorscale='Greens', name='Biomassa'))
fig2.add_trace(go.Surface(z=PROT_grid, x=NDVI_grid, y=COMP_grid, colorscale='Blues', showscale=False, name='Proteína'))

fig2.update_layout(
    title="Superfícies de Biomassa e Proteína em função de NDVI e Compressão",
    scene=dict(
        xaxis_title='NDVI',
        yaxis_title='Compressão (cm)',
        zaxis=dict(title='Valor estimado', range=[0, 8000])  # ← aqui defines a altura
    )
)
st.plotly_chart(fig2, use_container_width=True)
