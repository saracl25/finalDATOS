import streamlit as st
import pandas as pd
import os
import subprocess
import time

# Configuración de página con apariencia Premium
st.set_page_config(
    page_title="Dashboard de Ventas PySpark",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para una estética visualmente espectacular (Glassmorphism + Gradientes)
st.markdown("""
<style>
    /* Estilo general */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Título principal con gradiente */
    .title-gradient {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        padding-top: 1rem;
    }
    
    /* Subtítulos estilizados */
    .subtitle-text {
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }
    
    /* Contenedores tipo Tarjeta (Glassmorphic Card) */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    /* Texto dentro de las tarjetas métricas */
    .metric-title {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 0.25rem;
    }
    
    /* Indicador de estado de procesamiento */
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .status-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Función para ejecutar el script de PySpark
def run_pyspark_pipeline():
    with st.spinner("Iniciando motor de PySpark y procesando CSV..."):
        try:
            # Ejecutar el script procesar_ventas.py
            result = subprocess.run(["python", "procesar_ventas.py"], capture_output=True, text=True, check=True)
            st.success("¡Pipeline de PySpark completado con éxito!")
            with st.expander("Ver bitácora de ejecución de PySpark"):
                st.code(result.stdout)
            # Esperar un momento para asegurar la actualización de archivos
            time.sleep(1)
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"Error al ejecutar el script de PySpark.")
            st.info("💡 Asegúrate de tener instalado PySpark y Java JDK. Ejecuta: `pip install pyspark`")
            with st.expander("Detalles del Error"):
                st.code(e.stderr if e.stderr else e.stdout)
            return False

# Ruta del archivo Parquet procesado
PARQUET_DIR = "ventas_procesadas.parquet"

# --- SIDEBAR / BARRA LATERAL ---
st.sidebar.markdown("<h2 style='text-align: center; color: #818cf8;'>⚙️ Panel de Control</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("### 🛠️ Flujo de Datos")
st.sidebar.markdown(
    "Este panel permite disparar el procesamiento distribuido de **PySpark** para calcular el total de ventas."
)

if st.sidebar.button("🚀 Ejecutar Pipeline PySpark", use_container_width=True):
    if run_pyspark_pipeline():
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Información del Proyecto")
st.sidebar.info(
    "**Pregunta 7 - Ingeniería de Datos**\n\n"
    "• **Tecnologías:** PySpark, Parquet, Streamlit, Pandas, PyArrow.\n"
    "• **Procesamiento:** Carga de CSV → Cálculo de `total_venta` → Conversión a Parquet."
)

# --- PANEL PRINCIPAL ---
st.markdown("<h1 class='title-gradient'>Dashboard de Ventas Inteligente</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Visualización en tiempo real de los datos de ventas procesados con PySpark y almacenados en Parquet.</p>", unsafe_allow_html=True)

# Verificar si el archivo parquet existe
if not os.path.exists(PARQUET_DIR):
    # Caso en que no se han procesado aún los datos
    st.markdown(f"""
    <div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #ef4444; margin-top:0;">⚠️ Datos de Ventas No Disponibles</h3>
        <p style="color: #cbd5e1; font-size:1.1rem;">La carpeta <b>{PARQUET_DIR}</b> no fue detectada. Esto significa que el script de PySpark aún no ha sido ejecutado o no ha completado la generación del archivo Parquet.</p>
        <p style="color: #94a3b8; font-size:0.95rem;">Por favor, haz clic en el botón <b>"Ejecutar Pipeline PySpark"</b> en el panel izquierdo para procesar los datos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar una previsualización del CSV original si existe
    if os.path.exists("ventas.csv"):
        st.markdown("### 📄 Datos Originales Recibidos (CSV)")
        df_original = pd.read_csv("ventas.csv")
        st.dataframe(df_original.style.highlight_max(axis=0, color="#1e293b"), width="stretch")
else:
    # Cargar los datos desde Parquet usando pandas
    try:
        df = pd.read_parquet(PARQUET_DIR)
        
        # --- TARJETAS MÉTRICAS (Efecto Premium) ---
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        total_ventas_val = df["total_venta"].sum()
        total_cant_val = df["cantidad"].sum()
        total_trans_val = len(df)
        ticket_prom_val = df["total_venta"].mean()
        
        with metric_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">💰 Ventas Totales</div>
                <div class="metric-value">${total_ventas_val:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📦 Unidades Vendidas</div>
                <div class="metric-value">{total_cant_val:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🤝 Transacciones</div>
                <div class="metric-value">{total_trans_val}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🎫 Ticket Promedio</div>
                <div class="metric-value">${ticket_prom_val:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- CUERPO PRINCIPAL ---
        col_tab, col_graph = st.columns([4, 5])
        
        with col_tab:
            st.markdown("### 📋 Detalle de Ventas Procesadas")
            st.markdown("Los datos cargados de manera óptima desde el archivo Parquet:")
            # Mostrar tabla interactiva elegante
            st.dataframe(
                df.style.format({
                    "precio": "${:,.2f}",
                    "total_venta": "${:,.2f}"
                }).background_gradient(cmap="Blues", subset=["total_venta"]), 
                width="stretch",
                height=250
            )
            
            # Badge de Estado
            st.markdown(
                "**Estado del Almacenamiento:** "
                "<span class='status-badge status-success'>⚡ Parquet Optimizado</span>", 
                unsafe_allow_html=True
            )
            
        with col_graph:
            st.markdown("### 📊 Ventas por Producto")
            st.markdown("Gráfico comparativo del total generado por cada tipo de producto:")
            
            # Crear un dataframe resumido para el gráfico
            chart_data = df.groupby("producto")["total_venta"].sum().reset_index()
            # Ordenar para mejor visualización
            chart_data = chart_data.sort_values(by="total_venta", ascending=False)
            
            # Gráfico de barras de Streamlit
            st.bar_chart(
                data=chart_data,
                x="producto",
                y="total_venta",
                color="#6366f1",
                width="stretch"
            )
            
        # --- DESCRIPCIÓN DEL PROCESAMIENTO ---
        st.markdown("---")
        st.markdown("### 🔬 Arquitectura del Procesamiento")
        
        col_arch1, col_arch2 = st.columns(2)
        with col_arch1:
            st.markdown("""
            **1. Carga Distribuida (PySpark):**
            * SparkSession inicializada para computación distribuida.
            * Carga diferida (lazy evaluation) del archivo `ventas.csv`.
            * Inferencia automática de tipos de datos.
            
            **2. Cálculo Escalable:**
            * Generación de la columna `total_venta` de forma vectorizada: `df.withColumn("total_venta", col("cantidad") * col("precio"))`.
            """)
        with col_arch2:
            st.markdown("""
            **3. Persistencia Eficiente (Parquet):**
            * Almacenamiento columnar altamente comprimido.
            * Ideal para analítica sobre grandes volúmenes de datos (Big Data).
            
            **4. Visualización Ágil (Streamlit):**
            * Aplicación web reactiva.
            * Lectura nativa y ultra veloz del formato Parquet mediante PyArrow.
            """)
            
    except Exception as e:
        st.error(f"Error al leer el archivo Parquet procesado: {e}")
        st.info("Asegúrate de que el pipeline de PySpark se haya ejecutado correctamente.")
