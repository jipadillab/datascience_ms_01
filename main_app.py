import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuración General ---
st.set_page_config(page_title="Plataforma Multisectorial de Datos", layout="wide", page_icon="📊")

st.title("📊 Plataforma de Análisis de Datos Multisectorial")
st.markdown("""
Esta herramienta detecta automáticamente el tipo de conjunto de datos cargado y genera un tablero de control específico.
**Formatos soportados:** Energía Renovable, Monitoreo Ambiental, Agro Colombia.
""")

# --- Funciones de Análisis por Sector ---

def analizar_energia(df):
    st.subheader("⚡ Dashboard de Energía Renovable")
    
    # Preprocesamiento
    if 'Fecha_Entrada_Operacion' in df.columns:
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])

    # Sidebar
    st.sidebar.header("Filtros Energía")
    operador = st.sidebar.multiselect("Operador", df['Operador'].unique(), default=df['Operador'].unique())
    tecnologia = st.sidebar.multiselect("Tecnología", df['Tecnologia'].unique(), default=df['Tecnologia'].unique())
    
    df_filtrado = df.query("Operador == @operador & Tecnologia == @tecnologia")
    
    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proyectos", len(df_filtrado))
    c2.metric("Capacidad Total (MW)", f"{df_filtrado['Capacidad_Instalada_MW'].sum():,.2f}")
    c3.metric("Generación Diaria (MWh)", f"{df_filtrado['Generacion_Diaria_MWh'].sum():,.2f}")
    c4.metric("Inversión (MUSD)", f"{df_filtrado['Inversion_Inicial_MUSD'].sum():,.2f}")

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df_filtrado, x='Tecnologia', y='Capacidad_Instalada_MW', color='Operador', 
                     title="Capacidad Instalada por Tecnología y Operador")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(df_filtrado, x='Capacidad_Instalada_MW', y='Generacion_Diaria_MWh', 
                         color='Tecnologia', size='Inversion_Inicial_MUSD',
                         title="Eficiencia: Capacidad vs Generación (Tamaño = Inversión)")
        st.plotly_chart(fig, use_container_width=True)

def analizar_ambiental(df):
    st.subheader("🍃 Dashboard de Monitoreo Ambiental")

    # Sidebar
    st.sidebar.header("Filtros Ambiental")
    ciudad = st.sidebar.multiselect("Ciudad", df['Ciudad'].unique(), default=df['Ciudad'].unique())
    tipo_zona = st.sidebar.multiselect("Zona", df['Tipo_Zona'].unique(), default=df['Tipo_Zona'].unique())
    
    df_filtrado = df.query("Ciudad == @ciudad & Tipo_Zona == @tipo_zona")

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Sensores Activos", len(df_filtrado))
    c2.metric("Promedio PM2.5", f"{df_filtrado['PM2_5_Ug_m3'].mean():.2f} µg/m³")
    c3.metric("Temp. Promedio", f"{df_filtrado['Temperatura_C'].mean():.1f} °C")

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        # Boxplot para ver la dispersión de contaminación
        fig = px.box(df_filtrado, x='Ciudad', y='PM2_5_Ug_m3', color='Tipo_Zona',
                     title="Distribución de Material Particulado (PM2.5) por Ciudad")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Heatmap de correlación simple o Scatter
        fig = px.scatter(df_filtrado, x='Temperatura_C', y='Humedad_Relativa_Pct', 
                         color='Indice_Calidad_Aire_ICA',
                         title="Relación Temperatura vs Humedad (Color = Calidad Aire)")
        st.plotly_chart(fig, use_container_width=True)

def analizar_agro(df):
    st.subheader("🚜 Dashboard Agropecuario Colombia")

    # Sidebar
    st.sidebar.header("Filtros Agro")
    departamento = st.sidebar.multiselect("Departamento", df['Departamento'].unique(), default=df['Departamento'].unique())
    cultivo = st.sidebar.multiselect("Cultivo", df['Tipo_Cultivo'].unique(), default=df['Tipo_Cultivo'].unique())
    
    df_filtrado = df.query("Departamento == @departamento & Tipo_Cultivo == @cultivo")

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Fincas Auditadas", len(df_filtrado))
    c2.metric("Área Total (Ha)", f"{df_filtrado['Area_Hectareas'].sum():,.0f}")
    c3.metric("Producción Total (Ton)", f"{df_filtrado['Produccion_Anual_Ton'].sum():,.0f}")

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        fig = px.sunburst(df_filtrado, path=['Departamento', 'Tipo_Cultivo'], values='Produccion_Anual_Ton',
                          title="Distribución de Producción (Sunburst)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(df_filtrado, x='Area_Hectareas', y='Produccion_Anual_Ton', 
                         color='Nivel_Tecnificacion', hover_data=['Tipo_Suelo'],
                         title="Productividad: Área vs Producción")
        st.plotly_chart(fig, use_container_width=True)

# --- Main App Logic ---

uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo CSV (Energía, Ambiental o Agro)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        columns = set(df.columns)
        
        # --- Lógica de Detección Automática ---
        
        # 1. Definir las firmas de columnas esperadas (sets para comparación rápida)
        cols_energia = {'ID_Proyecto', 'Tecnologia', 'Capacidad_Instalada_MW'}
        cols_ambiental = {'ID_Sensor', 'PM2_5_Ug_m3', 'Indice_Calidad_Aire_ICA'}
        cols_agro = {'ID_Finca', 'Tipo_Cultivo', 'Produccion_Anual_Ton'}

        # 2. Verificar intersección
        if cols_energia.issubset(columns):
            st.success("✅ Archivo identificado: Datos de ENERGÍA RENOVABLE")
            analizar_energia(df)
            
        elif cols_ambiental.issubset(columns):
            st.success("✅ Archivo identificado: Datos de MONITOREO AMBIENTAL")
            analizar_ambiental(df)
            
        elif cols_agro.issubset(columns):
            st.success("✅ Archivo identificado: Datos del SECTOR AGROPECUARIO")
            analizar_agro(df)
            
        else:
            st.error("⚠️ El archivo cargado no coincide con ninguno de los esquemas conocidos (Energía, Ambiental, Agro).")
            st.write("Por favor verifica que las columnas sean correctas.")
            with st.expander("Ver columnas detectadas"):
                st.write(list(columns))

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("👆 Esperando archivo. Por favor carga un CSV en la barra lateral.")
