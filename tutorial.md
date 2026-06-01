# Guía Tutorial: Procesamiento de Datos con PySpark y Despliegue con Streamlit

Este tutorial está diseñado como material didáctico paso a paso para comprender el flujo completo de ingeniería de datos: desde la ingesta de un archivo CSV plano, el procesamiento distribuido en memoria usando **PySpark**, la persistencia eficiente en almacenamiento columnar **Parquet**, hasta el despliegue interactivo con **Streamlit**.

---

## 📖 1. Fundamentos Teóricos

### ¿Qué es Apache Spark y PySpark?
**Apache Spark** es un motor de análisis unificado de código abierto diseñado para procesar Big Data a gran escala de forma ultra-rápida mediante computación distribuidora en memoria.
**PySpark** es la API de Python para Spark, lo que nos permite combinar el poder de procesamiento distribuido de Spark con la facilidad y sintaxis amigable de Python.

### ¿Por qué utilizar el formato Parquet?
En lugar de almacenar datos procesados en CSV o bases de datos relacionales tradicionales, la ingeniería de datos moderna utiliza **Parquet**. Sus ventajas clave son:
1. **Almacenamiento Columnar:** A diferencia de CSV (orientado a filas), Parquet organiza los datos por columnas. Si solo necesitas consultar dos columnas de cien en un DataFrame gigante, Spark solo leerá esas dos columnas del disco, reduciendo drásticamente las operaciones I/O.
2. **Compresión Eficiente:** Admite compresión de alta calidad (como Snappy o Gzip) optimizada para los patrones de datos repetitivos dentro de cada columna, reduciendo el espacio en disco hasta en un 75%.
3. **Metadatos e Inferencia de Esquemas:** Almacena de forma nativa los tipos de datos (enteros, flotantes, strings) y estadísticas de columnas (mínimos, máximos), eliminando la necesidad de re-analizar o inferir esquemas en cada lectura.

---

## 🛠️ 2. Paso a Paso del Procesamiento con PySpark (`procesar_ventas.py`)

A continuación, analizamos línea por línea el script desarrollado para procesar los datos de ventas.

### Paso 2.1: Importación de Módulos
```python
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
```
* **`SparkSession`**: Es el punto de entrada principal a la funcionalidad de Spark en modo DataFrame.
* **`col`**: Es una función de PySpark de gran utilidad para hacer referencia directa a las columnas de un DataFrame de forma limpia y realizar operaciones matemáticas con ellas.

### Paso 2.2: Inicializar la Sesión de Spark
```python
spark = SparkSession.builder \
    .appName("Procesamiento de Ventas de Empresa") \
    .config("spark.sql.shuffle.partitions", "5") \
    .getOrCreate()
```
* **`builder`**: Inicia el patrón constructor de la sesión.
* **`appName("...")`**: Asigna un nombre a la aplicación, visible en la interfaz web de Spark (Spark UI).
* **`config("spark.sql.shuffle.partitions", "5")`**: Configura el número de particiones a usar al barajar datos. Para entornos locales y datasets pequeños, reducir este valor desde su valor por defecto (200) acelera sustancialmente la velocidad de procesamiento.
* **`getOrCreate()`**: Devuelve una sesión existente o crea una nueva si no la hay.

### Paso 2.3: Ingesta del Archivo CSV
```python
df_ventas = spark.read.csv(
    csv_path, 
    header=True, 
    inferSchema=True
)
```
* **`header=True`**: Le indica a Spark que la primera fila del CSV contiene los nombres de las columnas.
* **`inferSchema=True`**: Le pide a Spark que lea una muestra inicial para detectar automáticamente los tipos de datos (por ejemplo, detectar que `id_venta` y `cantidad` son enteros).

### Paso 2.4: Casteo y Limpieza de Esquema
```python
df_ventas = df_ventas.withColumn("cantidad", col("cantidad").cast("int")) \
                     .withColumn("precio", col("precio").cast("double"))
```
* Aunque `inferSchema` es preciso, es una **buena práctica** en ingeniería de datos asegurar explícitamente los tipos numéricos utilizando `.cast()`. Esto evita fallos matemáticos derivados de caracteres extraños o espacios en blanco leídos como texto.

### Paso 2.5: Cálculo de la Nueva Columna (`total_venta`)
```python
df_resultado = df_ventas.withColumn("total_venta", col("cantidad") * col("precio"))
```
* **`withColumn("nombre", operacion)`**: Es la función fundamental para crear o reemplazar una columna.
* En este caso, multiplica las columnas `cantidad` y `precio` de manera vectorizada y optimizada.

### Paso 2.6: Mostrar Resultados en Consola
```python
df_resultado.show()
```
* Dado que Spark utiliza **evaluación perezosa** (lazy evaluation), ningún cálculo se ejecuta realmente hasta que se invoca una acción como `.show()` o se guardan los archivos. Esta función muestra por pantalla las primeras 20 filas del dataset resultante.

### Paso 2.7: Persistencia en Parquet
```python
df_resultado.write.mode("overwrite").parquet(parquet_path)
```
* **`write`**: Prepara el escritor del DataFrame.
* **`mode("overwrite")`**: Configura que, si ya existe una carpeta con ese nombre, sobrescriba los datos en lugar de lanzar una excepción de archivo ya existente.
* **`parquet(...)`**: Escribe el archivo en formato columnar optimizado Parquet.

### Paso 2.8: Liberación de Recursos
```python
spark.stop()
```
* Cierra la sesión activa de Spark. Esto libera la memoria RAM y el núcleo de Java (JVM) en ejecución en la máquina.

---

## 🎨 3. Construcción del Dashboard Interactivo (`app.py`)

Streamlit convierte scripts de Python en interfaces web interactivas en minutos. El archivo `app.py` integra el procesamiento de datos con una visualización web moderna.

### Características Clave de la App:
1. **Configuración de Página Premium:** Usando `st.set_page_config` se expande a pantalla ancha y se establece un icono.
2. **Inyección de CSS (Estilo Glassmorphism):** Creamos fondos oscuros, gradientes de color modernos (`linear-gradient`) y bordes difusos para simular un estilo visual sofisticado y premium.
3. **Métricas en Tarjetas de Datos:** Implementado a través de HTML inyectado en Streamlit, mostrando los KPIs clave sin sobrecargar la UI de elementos aburridos.
4. **Gráficos Dinámicos:** Muestra visualizaciones reactivas automáticas a través de `st.bar_chart` utilizando los datos cargados desde el archivo Parquet.
5. **Carga Inteligente con Pandas:**
   ```python
   df = pd.read_parquet("ventas_procesadas.parquet")
   ```
   Pandas y PyArrow se encargan de leer el archivo Parquet procesado por PySpark de manera casi instantánea en memoria para la app.
6. **Ejecución Integrada del Pipeline:**
   Si los datos de Parquet no existen, la app alerta al usuario. Pero en lugar de obligarlo a ir a la terminal, el botón lateral ejecuta el script en segundo plano:
   ```python
   subprocess.run(["python", "procesar_ventas.py"], capture_output=True, text=True, check=True)
   ```

---

## 🚀 4. Guía de Despliegue Local Paso a Paso

Sigue estas sencillas instrucciones para probar todo el flujo de trabajo en tu máquina local:

### Paso 1: Clonar/Preparar tu entorno
Asegúrate de que estás en la carpeta del proyecto. Crea un entorno virtual si lo prefieres para mantener limpias tus librerías:
```bash
python -m venv venv
venv\Scripts\activate
```

### Paso 2: Instalación de las Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Ejecución y Generación de Datos
Ejecuta el script PySpark para procesar el CSV original y generar los archivos Parquet optimizados:
```bash
python procesar_ventas.py
```
Observarás la siguiente salida en consola:
```text
Iniciando sesión de Spark...
Cargando archivo CSV desde: ventas.csv...
...
+--------+--------+--------+------+-----------+
|id_venta|producto|cantidad|precio|total_venta|
+--------+--------+--------+------+-----------+
|       1|  Laptop|       2|2500.0|     5000.0|
|       2|   Mouse|       5|  50.0|      250.0|
|       3| Teclado|       3| 120.0|      360.0|
+--------+--------+--------+------+-----------+
Guardando datos procesados en formato Parquet...
¡Proceso completado exitosamente!
Deteniendo sesión de Spark...
```

### Paso 4: Despliegue de la Aplicación Web
Una vez generada la carpeta `ventas_procesadas.parquet`, despliega el dashboard con Streamlit:
```bash
streamlit run app.py
```
Esto lanzará un servidor local y abrirá la pestaña en tu navegador. Puedes interactuar con los datos, ver los gráficos y refrescar los cálculos en cualquier momento.
