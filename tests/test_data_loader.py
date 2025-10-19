import pytest
import polars as pl
from pathlib import Path
from unittest.mock import patch
from datetime import date
import datetime

# *************************************************************************
# NOTA: Pytest está diseñado para encontrar y ejecutar pruebas automáticamente.
# Al ejecutar 'pytest' desde la carpeta raíz, él se encarga de las rutas 
# relativas, eliminando la necesidad del 'sys.path.append' manual.
# *************************************************************************

# Datos simulados que nflreadpy.load_player_stats devolvería (como pandas DataFrame)
MOCK_PANDAS_DF = pl.DataFrame({
    "player_display_name": ["J. Allen", "P. Mahomes"],
    "season": [2024, 2024],
    "week": [1, 1],
    "position": ["QB", "QB"],
    "passing_yards": [300, 250]
}).to_pandas()


# Usamos la fixture tmp_path de pytest para un directorio temporal
# Usamos patch para simular la descarga (evitar depender de la red)
@patch('src.data_loader.nfl.load_player_stats', return_value=MOCK_PANDAS_DF)
def test_download_weekly_data_success(mock_load_stats, tmp_path):
    """
    Prueba que la función de descarga simule la descarga, guarde el archivo 
    en un directorio temporal y verifique el contenido.
    """
    
    # 1. Redirigir DATA_DIR temporalmente al directorio de pytest (tmp_path)
    with patch('src.data_loader.DATA_DIR', tmp_path): 
        # Importamos la función DENTRO del contexto para asegurar que DATA_DIR esté parcheado
        from src.data_loader import download_weekly_data
        
        # 2. EJECUTAR FUNCIÓN (con el año actual como default, o explícitamente 2024)
        download_weekly_data(season=2024)

    # 3. VERIFICACIONES (sobre el directorio temporal)
    
    # c) Determinar el nombre del archivo esperado
    today_str = date.today().strftime("%Y%m%d")
    expected_file = tmp_path / f"player_stats_2024_{today_str}.parquet"
    
    # d) Verificar que se creó UN solo archivo
    assert expected_file.exists(), "❌ El archivo Parquet esperado no se creó."
    
    # e) Leer y verificar el contenido
    df = pl.read_parquet(expected_file)
    
    # f) Verificar registros
    assert len(df) == len(MOCK_PANDAS_DF), "❌ Número incorrecto de registros simulados."
    
    # g) Verificar columnas
    expected_columns = {"player_display_name", "season", "week", "position"}
    assert expected_columns.issubset(set(df.columns)), "❌ Faltan columnas esperadas."

# -- Prueba de Fallo de Descarga --
@patch('src.data_loader.nfl.load_player_stats', side_effect=Exception("Error de red simulado"))
def test_download_weekly_data_failure(mock_load_stats, tmp_path):
    """Prueba que la función maneje correctamente un error de descarga y no cree archivos."""
    with patch('src.data_loader.DATA_DIR', tmp_path):
        from src.data_loader import download_weekly_data
        
        # El test no debe lanzar una excepción, solo debe notificar el error
        # (lo que hace tu 'try/except' al usar 'return')
        download_weekly_data(season=2024)

    # Verificar que NO se crearon archivos en el directorio temporal
    parquet_files = list(tmp_path.glob("*.parquet"))
    assert len(parquet_files) == 0, "❌ Se creó un archivo a pesar de un error de descarga."