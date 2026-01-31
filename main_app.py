import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq  # Importamos la librería de Groq

# --- Configuración General ---
st.set_page_config(page_title="Plataforma Multisectorial AI", layout="wide", page_icon="🤖")

st.title("📊 Plataforma de Análisis con Asistente IA")
st.markdown("""
Sube tus datos (Energía, Ambiental, Agro) y obtén gráficos automáticos + **Análisis Inteligente con Llama 3**.
""")

# --- Funciones de Visualización (Las mismas de antes) ---
def analizar_energia(df):
    st.subheader("⚡ Dashboard de Energía Renovable")
    if 'Fecha_Entrada_Operacion' in df.columns:
        df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Proyectos", len(df))
    c2.metric("Capacidad MW", f"{df['Capacidad_Instalada_MW'].sum():,.2f}")
    c3.metric("Inversión MUSD", f"{df['Inversion_Inicial_MUSD'].sum():,.2f}")
    
    fig = px.bar(df, x='Tecnologia', y='Capacidad_Instalada_MW', color='Operador', title="Capacidad por Tecnología")
    st.plotly_chart(fig, use_container_width=True)

def analizar_ambiental(df):
    st.subheader("🍃 Dashboard de Monitoreo Ambiental")
    c1, c2 = st.columns(2)
    c1.metric("Sensores", len(df))
    c2.metric("Promedio PM2.5", f"{df['PM2_5_Ug_m3'].mean():.2f}")
    
    fig = px.box(df, x='Ciudad', y='PM2_5_Ug_m3', color='Tipo_Zona', title="Contaminación por Ciudad")
    st.plotly_chart(fig, use_container_width=True)

def analizar_agro(df):
    st.subheader("🚜 Dashboard Agropecuario")
    c1, c2 = st.columns(2)
    c1.metric("Fincas", len(df))
    c2.metric("Producción Ton", f"{df['Produccion_Anual_Ton'].sum():,.0f}")
    
    fig = px.sunburst(df, path=['Departamento', 'Tipo_Cultivo'], values='Produccion_Anual_Ton', title="Producción por Región")
    st.plotly_chart(fig, use_container_width=True)

# --- FUNCIÓN: Generar Análisis con LLM ---
def generar_analisis_ia(df, api_key, tipo_datos):
    """
    Envía un resumen estadístico de los datos a Groq para obtener insights.
    """
    try:
        client = Groq(api_key=api_key)
        
        # Crear un resumen de los datos para no enviar todo el CSV (ahorro de tokens)
        resumen_estadistico = df.describe().to_string()
        muestra_datos = df.head(5).to_string()
        columnas = list(df.columns)
        
        # Construcción del Prompt
        prompt = f"""
        Actúa como un Científico de Datos experto. Estás analizando un conjunto de datos de: {tipo_datos}.
        
        Aquí tienes un resumen de los datos:
        1. Columnas disponibles: {columnas}
        2. Muestra de las primeras 5 filas:
        {muestra_datos}
        3. Estadísticas descriptivas:
        {resumen_estadistico}

        TAREA:
        Por favor, realiza un Análisis Exploratorio de Datos (EDA) textual breve.
        1. Identifica posibles tendencias o anomalías visibles en las estadísticas.
        2. Sugiere 3 preguntas de negocio que estos datos podrían responder.
        3. Dame una conclusión general sobre la calidad o estado de los datos.
        
        Responde en formato Markdown, claro y conciso en Español.
        """

        with st.spinner('🤖 Llama 3 está analizando tus datos...'):
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=1024,
            )
            
        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"❌ Error al conectar con Groq: {str(e)}"

# --- Main App Logic ---

# 1. Sidebar: Carga de archivo y API Key
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("📂 Sube CSV (Energía, Ambiental, Agro)", type=["csv"])
st.sidebar.markdown("---")
groq_api_key = st.sidebar.text_input("🔑 Tu Groq API Key", type="password", help="Obtén tu key en console.groq.com")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        columns = set(df.columns)
        
        # Definición de huellas de columnas
        cols_energia = {'ID_Proyecto', 'Tecnologia', 'Capacidad_Instalada_MW'}
        cols_ambiental = {'ID_Sensor', 'PM2_5_Ug_m3', 'Indice_Calidad_Aire_ICA'}
        cols_agro = {'ID_Finca', 'Tipo_Cultivo', 'Produccion_Anual_Ton'}

        tipo_detectado = ""
        
        # Detección y Visualización
        if cols_energia.issubset(columns):
            tipo_detectado = "Energía Renovable"
            st.success(f"✅ Archivo identificado: {tipo_detectado}")
            analizar_energia(df)
            
        elif cols_ambiental.issubset(columns):
            tipo_detectado = "Monitoreo Ambiental"
            st.success(f"✅ Archivo identificado: {tipo_detectado}")
            analizar_ambiental(df)
            
        elif cols_agro.issubset(columns):
            tipo_detectado = "Sector Agropecuario"
            st.success(f"✅ Archivo identificado: {tipo_detectado}")
            analizar_agro(df)
            
        else:
            st.error("⚠️ Formato de archivo no reconocido.")
            st.stop()

        # --- SECCIÓN: Asistente de IA ---
        st.markdown("---")
        st.subheader("🤖 Asistente de Análisis Inteligente")
        
        if not groq_api_key:
            st.warning("⚠️ Para usar el asistente IA, por favor ingresa tu API Key de Groq en la barra lateral.")
        else:
            col_ia_1, col_ia_2 = st.columns([1, 3])
            
            with col_ia_1:
                st.info("El modelo analizará estadísticas descriptivas y una muestra de tus datos.")
                if st.button("🧠 Generar Análisis con Llama 3", type="primary"):
                    analisis = generar_analisis_ia(df, groq_api_key, tipo_detectado)
                    st.session_state['analisis_resultado'] = analisis

            with col_ia_2:
                if 'analisis_resultado' in st.session_state:
                    st.markdown(st.session_state['analisis_resultado'])

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("👆 Esperando archivo...")
