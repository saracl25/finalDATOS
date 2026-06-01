import os
import sys
import pandas as pd
import numpy as np
import tempfile
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_ventas_csv_exists():
    """Verifica que el archivo CSV de entrada exista y tenga datos."""
    path = os.path.join(PROJECT_DIR, "ventas.csv")
    assert os.path.exists(path), "No se encuentra ventas.csv"
    df = pd.read_csv(path)
    assert len(df) > 0, "El CSV está vacío"
    required_cols = {"id_venta", "producto", "cantidad", "precio"}
    assert required_cols.issubset(df.columns), f"Faltan columnas: {required_cols - set(df.columns)}"


def test_ventas_csv_data_types():
    """Verifica tipos de datos en ventas.csv."""
    df = pd.read_csv(os.path.join(PROJECT_DIR, "ventas.csv"))
    assert df["id_venta"].dtype in (np.int64, np.int32), "id_venta debe ser numérico"
    assert df["cantidad"].dtype in (np.int64, np.int32), "cantidad debe ser entero"
    assert df["precio"].dtype in (np.float64, np.float32, np.int64), "precio debe ser numérico"
    assert pd.api.types.is_string_dtype(df["producto"].dtype), "producto debe ser texto"


def test_ventas_csv_no_negatives():
    """Verifica que no haya valores negativos en cantidad o precio."""
    df = pd.read_csv(os.path.join(PROJECT_DIR, "ventas.csv"))
    assert (df["cantidad"] > 0).all(), "Hay cantidades <= 0"
    assert (df["precio"] > 0).all(), "Hay precios <= 0"


def test_parquet_output_exists():
    """Verifica que exista la salida Parquet generada por PySpark."""
    parquet_dir = os.path.join(PROJECT_DIR, "ventas_procesadas.parquet")
    assert os.path.exists(parquet_dir), "No se encuentra ventas_procesadas.parquet/"
    parquet_files = [f for f in os.listdir(parquet_dir) if f.endswith(".parquet")]
    assert len(parquet_files) > 0, "No hay archivos .parquet en el directorio de salida"


def test_parquet_has_correct_schema():
    """Verifica que el Parquet tenga la columna total_venta calculada."""
    parquet_dir = os.path.join(PROJECT_DIR, "ventas_procesadas.parquet")
    df = pd.read_parquet(parquet_dir)
    required_cols = {"id_venta", "producto", "cantidad", "precio", "total_venta"}
    assert required_cols.issubset(df.columns), f"Faltan columnas en Parquet: {required_cols - set(df.columns)}"


def test_total_venta_is_correct():
    """Verifica que total_venta = cantidad * precio."""
    parquet_dir = os.path.join(PROJECT_DIR, "ventas_procesadas.parquet")
    df = pd.read_parquet(parquet_dir)
    df["expected_total"] = df["cantidad"] * df["precio"]
    mismatches = df[df["total_venta"] != df["expected_total"]]
    assert len(mismatches) == 0, f"Hay {len(mismatches)} filas donde total_venta no coincide"


def test_parquet_no_nulls():
    """Verifica que no haya valores nulos en el Parquet."""
    parquet_dir = os.path.join(PROJECT_DIR, "ventas_procesadas.parquet")
    df = pd.read_parquet(parquet_dir)
    assert df.isnull().sum().sum() == 0, "Hay valores nulos en los datos procesados"


def test_parquet_positive_totals():
    """Verifica que todos los total_venta sean positivos."""
    parquet_dir = os.path.join(PROJECT_DIR, "ventas_procesadas.parquet")
    df = pd.read_parquet(parquet_dir)
    assert (df["total_venta"] > 0).all(), "Hay total_venta <= 0"


def test_procesar_ventas_script_has_main():
    """Verifica que procesar_ventas.py tenga la estructura correcta."""
    path = os.path.join(PROJECT_DIR, "procesar_ventas.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "def main():" in content, "Falta la función main()"
    assert 'if __name__ == "__main__":' in content, "Falta el bloque __main__"
    assert "SparkSession" in content, "Falta importación de SparkSession"
    assert "parquet" in content, "No se escribe a Parquet"


def test_train_model_script():
    """Verifica que train_model.py genere los archivos esperados."""
    path = os.path.join(PROJECT_DIR, "train_model.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "RandomForestRegressor" in content, "Falta RandomForestRegressor"
    assert "joblib.dump" in content, "Falta joblib.dump para guardar el modelo"
    assert "ventas_historicas.csv" in content, "Falta generar ventas_historicas.csv"


def test_requirements_has_pyspark():
    """Verifica que requirements.txt contenga las dependencias esenciales."""
    path = os.path.join(PROJECT_DIR, "requirements.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "pyspark" in content, "Falta pyspark en requirements.txt"
    assert "streamlit" in content, "Falta streamlit en requirements.txt"


def test_app_has_required_elements():
    """Verifica que app.py tenga los componentes clave del dashboard."""
    path = os.path.join(PROJECT_DIR, "app.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "st.set_page_config" in content, "Falta configuración de página"
    assert "total_venta" in content, "Falta referencia a total_venta"
    assert "bar_chart" in content or "st.bar_chart" in content, "Falta gráfico de barras"
    assert "read_parquet" in content, "Falta lectura de Parquet"


def test_hadoop_setup_in_procesar():
    """Verifica que procesar_ventas.py tenga setup para Windows."""
    path = os.path.join(PROJECT_DIR, "procesar_ventas.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "HADOOP_HOME" in content, "Falta configuración de HADOOP_HOME"
    assert "winutils" in content, "Falta manejo de winutils.exe"


def test_notebook_exists_and_has_cells():
    """Verifica que el notebook exista y contenga celdas de código."""
    path = os.path.join(PROJECT_DIR, "modelo_ventas.ipynb")
    assert os.path.exists(path), "No se encuentra modelo_ventas.ipynb"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "RandomForestRegressor" in content, "Falta RandomForestRegressor en el notebook"
