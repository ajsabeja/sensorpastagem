import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Simulador de Compressão e Avaliação de Pastagens")

st.markdown("""
Modelo:
- **Compressão da vegetação** com base no peso do prato e rigidez da pastagem;
- **Biomassa seca (kg MS/ha)** e **proteína bruta (%)** com base em NDVI e compressão.

Os coeficientes podem ser ajustados manualmente. Valores iniciais foram calibrados com base na literatura
""")

st.markdown("""Biomassa:** Calvão & Palmeirim (2004),
            Mapping Mediterranean scrub with satellite imagery: biomass estimation and spectral behaviour
            (https://doi.org/10.1080/01431160310001654978)""")
st.markdown("""Proteína Bruta:** Garroutte et al. (2016), 
            Using NDVI and EVI to Map Spatiotemporal Variation in the Biomass and Quality of Forage for Migratory Elk in the Greater Yellowstone Ecosystem,
            (https://www.mdpi.com/2072-4292/8/5/404)""")

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

col1, col2, col3 = st.columns(3)
a = col1.number_input("a (NDVI ×)", value=6000)
b = col2.number_input("b (Compressão ×)", value=150)
c = col3.number_input("c (Constante)", value=500)

col4, col5 = st.columns(2)
d = col4.number_input("d (NDVI ×)", value=8.0)
e = col5.number_input("e (Constante)", value=4.0)

forca_n = peso * 9.81
compressao_cm = forca_n / rigidez_selecionada
biomassa = a * ndvi + b * compressao_cm + c
proteina = d * ndvi + e

st.subheader("Resultados Estimados")
col1, col2, col3 = st.columns(3)
col1.metric("Compressão (cm)", f"{compressao_cm:.2f}")
col2.metric("Biomassa (kg MS/ha)", f"{biomassa:.0f}")
col3.metric("Proteína bruta (%)", f"{proteina:.2f}")

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

st.subheader("Gráfico 2A – Biomassa por NDVI em diferentes compressões")
ndvi_vals = np.linspace(0.0, 1.0, 100)
comp_range = [0.5, 2.0, 4.0, 6.0, 8.0]
fig_biom = go.Figure()
for comp in comp_range:
    biomassa_vals = a * ndvi_vals + b * comp + c
    fig_biom.add_trace(go.Scatter(x=ndvi_vals, y=biomassa_vals, mode='lines', name=f"{comp} cm"))

fig_biom.update_layout(
    xaxis_title="NDVI",
    yaxis_title="Biomassa (kg MS/ha)",
    title="Biomassa estimada por NDVI",
    hovermode="x unified"
)
st.plotly_chart(fig_biom, use_container_width=True)

st.subheader("Gráfico 2B – Proteína por NDVI")
proteina_vals = d * ndvi_vals + e
fig_prot = go.Figure()
fig_prot.add_trace(go.Scatter(x=ndvi_vals, y=proteina_vals, mode='lines+markers', name="Proteína"))

fig_prot.update_layout(
    xaxis_title="NDVI",
    yaxis_title="Proteína Bruta (%)",
    title="Proteína estimada por NDVI",
    hovermode="x unified"
)
st.plotly_chart(fig_prot, use_container_width=True)
