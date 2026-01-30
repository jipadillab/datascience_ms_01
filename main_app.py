import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="EDA Energía Renovable", layout="wide")

st.title("⚡ Análisis de Energía Renovable")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("energia_renovable.csv")
    # Convertir fecha a datetime
    df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
    return df

try:
    df = load_data()
    
    # Sidebar con filtros
    st.sidebar.header("Filtros")
    operador = st.sidebar.multiselect(
        "Selecciona Operador:",
        options=df["Operador"].unique(),
        default=df["Operador"].unique()
    )
    
    df_selection = df.query("Operador == @operador")

    # Mostrar métricas básicas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Proyectos", len(df_selection))
    col2.metric("Capacidad Total (MW)", round(df_selection["Capacidad_Instalada_MW"].sum(), 2))
    col3.metric("Inversión Total (MUSD)", round(df_selection["Inversion_Inicial_MUSD"].sum(), 2))

    # Vista previa de datos
    with st.expander("Ver Datos Crudos"):
        st.dataframe(df_selection)

    # Gráficos
    st.subheader("Distribución por Tecnología")
    fig_tech = px.bar(
        df_selection.groupby("Tecnologia").size().reset_index(name="Conteo"),
        x="Tecnologia", y="Conteo", color="Tecnologia",
        title="Número de Proyectos por Tecnología"
    )
    st.plotly_chart(fig_tech, use_container_width=True)

    st.subheader("Capacidad vs Generación")
    fig_scatter = px.scatter(
        df_selection,
        x="Capacidad_Instalada_MW",
        y="Generacion_Diaria_MWh",
        color="Tecnologia",
        size="Inversion_Inicial_MUSD",
        hover_data=["ID_Proyecto"],
        title="Relación Capacidad vs Generación Diaria"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

except FileNotFoundError:
    st.error("El archivo 'energia_renovable.csv' no se encontró. Asegúrate de que esté en la misma carpeta.")
