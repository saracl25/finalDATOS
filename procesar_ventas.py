import os
import sys
import urllib.request

def setup_windows_hadoop():
    """
    Configura de forma local HADOOP_HOME y descarga winutils.exe y hadoop.dll
    si se está ejecutando en Windows y no están presentes.
    Esto soluciona el clásico error: 'HADOOP_HOME and hadoop.home.dir are unset'
    """
    if os.name == 'nt': # Verificar si es Windows
        print("Entorno Windows detectado. Configurando entorno Hadoop local...")
        hadoop_dir = os.path.abspath("hadoop")
        bin_dir = os.path.join(hadoop_dir, "bin")
        
        # Crear directorios si no existen
        os.makedirs(bin_dir, exist_ok=True)
        
        # URLs de descarga corregidas para los binarios de Hadoop 3.3.6
        winutils_url = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin/winutils.exe"
        hadoop_dll_url = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin/hadoop.dll"
        
        winutils_path = os.path.join(bin_dir, "winutils.exe")
        hadoop_dll_path = os.path.join(bin_dir, "hadoop.dll")
        
        # Descargar winutils.exe si no existe
        if not os.path.exists(winutils_path):
            print(f"Descargando winutils.exe desde GitHub (Hadoop 3.3.6)...")
            try:
                # Usar un User-Agent genérico por seguridad contra bloqueos de descarga
                req = urllib.request.Request(
                    winutils_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response, open(winutils_path, 'wb') as out_file:
                    out_file.write(response.read())
                print("winutils.exe descargado exitosamente.")
            except Exception as e:
                print(f"Error al descargar winutils.exe: {e}")
                
        # Descargar hadoop.dll si no existe
        if not os.path.exists(hadoop_dll_path):
            print(f"Descargando hadoop.dll desde GitHub (Hadoop 3.3.6)...")
            try:
                req = urllib.request.Request(
                    hadoop_dll_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response, open(hadoop_dll_path, 'wb') as out_file:
                    out_file.write(response.read())
                print("hadoop.dll descargado exitosamente.")
            except Exception as e:
                print(f"Error al descargar hadoop.dll: {e}")
        
        # Configurar variables de entorno de forma local para este proceso
        os.environ["HADOOP_HOME"] = hadoop_dir
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
        print(f"HADOOP_HOME configurado localmente en: {hadoop_dir}")

# EJECUTAR LA CONFIGURACIÓN ANTES DE CUALQUIER IMPORTACIÓN DE PYSPARK
setup_windows_hadoop()

# Ahora sí importamos las librerías de PySpark de forma segura
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col
except ModuleNotFoundError:
    print("=" * 70)
    print("ERROR: No se encontró el módulo 'pyspark'.")
    print("")
    print("PySpark no está instalado en este entorno. Para instalarlo ejecuta:")
    print("    pip install pyspark")
    print("")
    print("Requisito adicional: PySpark necesita Java (JDK 8/11/17).")
    print("  - Descarga: https://adoptium.net/")
    print("  - Configura la variable de entorno JAVA_HOME")
    print("=" * 70)
    sys.exit(1)

def main():
    # 1. Crear o inicializar la sesión de Spark
    print("\nIniciando sesión de Spark...")
    spark = SparkSession.builder \
        .appName("Procesamiento de Ventas de Empresa") \
        .config("spark.sql.shuffle.partitions", "5") \
        .getOrCreate()
    
    # Ruta del archivo CSV de entrada y salida
    csv_path = "ventas.csv"
    parquet_path = "ventas_procesadas.parquet"
    
    try:
        # 1. Cargar el archivo CSV
        print(f"Cargando archivo CSV desde: {csv_path}...")
        df_ventas = spark.read.csv(
            csv_path, 
            header=True, 
            inferSchema=True
        )
        
        # Validar el esquema cargado
        print("\n--- Esquema Inicial de los Datos ---")
        df_ventas.printSchema()
        
        # Asegurar tipos numéricos para cantidad y precio por seguridad
        df_ventas = df_ventas.withColumn("cantidad", col("cantidad").cast("int")) \
                             .withColumn("precio", col("precio").cast("double"))
        
        # 2. Calcular la nueva columna total_venta (cantidad * precio)
        print("Calculando la columna 'total_venta'...")
        df_resultado = df_ventas.withColumn("total_venta", col("cantidad") * col("precio"))
        
        # 3. Mostrar el resultado final
        print("\n--- Resultado Final del Procesamiento ---")
        df_resultado.show()
        
        # 4. Guardar los datos procesados en formato Parquet
        print(f"Guardando datos procesados en formato Parquet en: {parquet_path}...")
        df_resultado.write.mode("overwrite").parquet(parquet_path)
        print("¡Proceso completado exitosamente y datos guardados!")
        
    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")
        
    finally:
        # Detener la sesión de Spark para liberar recursos
        print("Deteniendo sesión de Spark...")
        spark.stop()

if __name__ == "__main__":
    main()
