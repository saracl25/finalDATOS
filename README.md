# Pregunta 7: Procesamiento de Ventas con PySpark y Streamlit

Este proyecto contiene la solución completa a la **Pregunta 7**, diseñada para cargar un archivo diario de ventas en formato CSV, procesar los datos utilizando **PySpark** para calcular una nueva columna `total_venta` (cantidad * precio), guardar los resultados en formato optimizado **Parquet**, y finalmente visualizar los resultados en una aplicación web interactiva desarrollada con **Streamlit**.

---

## 📁 Estructura del Proyecto

El espacio de trabajo está organizado de la siguiente manera:

* **`ventas.csv`**: Archivo de entrada con los datos diarios de ventas.
* **`procesar_ventas.py`**: Script en PySpark que realiza la carga de datos, procesamiento (cálculo de `total_venta`) y persistencia en formato Parquet.
* **`app.py`**: Aplicación de Streamlit que lee los datos del archivo Parquet y presenta un dashboard premium con KPIs, gráficos interactivos y control de ejecución del pipeline.
* **`requirements.txt`**: Lista de dependencias de Python necesarias para el funcionamiento del proyecto.
* **`tutorial.md`**: Tutorial paso a paso detallado que explica la teoría de PySpark, el código implementado y el despliegue del proyecto.

---

## 🛠️ Requisitos Previos

Para ejecutar el procesamiento de PySpark de forma local, necesitas tener instalado:
1. **Python 3.8+**
2. **Java Development Kit (JDK) 8 o 11** (requerido por Apache Spark).
3. Configurar la variable de entorno `JAVA_HOME` apuntando al JDK.

---

## 🚀 Guía de Instalación y Ejecución

### 1. Instalar Dependencias
Instala todas las bibliotecas de Python especificadas en `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el Script de PySpark
Para realizar el procesamiento inicial de datos y generar los archivos Parquet:
```bash
python procesar_ventas.py
```
Esto mostrará los resultados en la terminal y creará una carpeta llamada `ventas_procesadas.parquet`.

### 3. Ejecutar la Aplicación Streamlit
Para ver el dashboard interactivo y premium de ventas:
```bash
streamlit run app.py
```
La aplicación web se abrirá automáticamente en tu navegador (típicamente en `http://localhost:8501`).

---

## 📈 Dashboard de Streamlit
El dashboard incluye:
* **Métricas Principales (KPIs):** Ventas totales, cantidad de unidades vendidas, número total de transacciones y ticket promedio.
* **Tabla Interactiva:** Visualización ordenada de las ventas procesadas con gradientes de color.
* **Gráficos Dinámicos:** Ventas por producto en barras.
* **Control Remoto:** Botón integrado en la barra lateral para disparar y re-ejecutar el script PySpark directamente desde la interfaz web sin tocar la consola.
