import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="EDA Energía Renovable", layout="wide")

st.title("⚡ Análisis de Energía Renovable")

# --- 1. Carga de Datos Externa ---
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV aquí", type=["csv"])

# Lógica principal
if uploaded_file is not None:
    try:
        # --- 2. Lectura y Preprocesamiento (Dentro del Try) ---
        df = pd.read_csv(uploaded_file)

        # Verificamos columnas necesarias para evitar errores posteriores
        required_columns = ["Fecha_Entrada_Operacion", "Operador", "Tecnologia", 
                            "Capacidad_Instalada_MW", "Generacion_Diaria_MWh", "Inversion_Inicial_MUSD"]
        
        # Validar si las columnas existen en el archivo subido
        if not all(col in df.columns for col in required_columns):
            st.error(f"El archivo no tiene las columnas requeridas: {required_columns}")
        else:
            # Procesar fechas
            df['Fecha_Entrada_Operacion'] = pd.to_datetime(df['Fecha_Entrada_Operacion'])

            # --- 3. Filtros en Sidebar ---
            st.sidebar.header("Filtros")
            operadores_disponibles = df["Operador"].unique()
            operador = st.sidebar.multiselect(
                "Selecciona Operador:",
                options=operadores_disponibles,
                default=operadores_disponibles
            )
            
            # Filtrar DataFrame
            df_selection = df.query("Operador == @operador")

            # --- 4. Métricas y Visualizaciones ---
            if df_selection.empty:
                st.warning("No hay datos para los filtros seleccionados.")
            else:
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
                    hover_data=df_selection.columns, # Muestra info extra al pasar el mouse
                    title="Relación Capacidad vs Generación Diaria"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        # --- 5. Manejo de Errores ---
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
        st.info("Asegúrate de que el archivo sea un CSV válido y tenga el formato correcto.")

else:
    # Mensaje de bienvenida cuando no hay archivo
    st.info("👆 Por favor, carga un archivo CSV en el panel lateral para comenzar el análisis.")
