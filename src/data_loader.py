# src/data_loader.py

import nflreadpy as nfl
import polars as pl
from pathlib import Path
import datetime
import argparse
from datetime import date

# Carpeta principal para datos crudos
DATA_DIR = Path(__file__).resolve().parents[1] / "data/raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Funcion que realiza la descarga de las temporadas conforme al año indicado.
def download_weekly_data(season = None):
    """
    Descarga o actualiza datos de jugadores de la temporada actual.
    """  
    if season is None:
        season = datetime.date.today().year
    print(f"Descargando información actualizadas para temporada {season}...")
    
    try:
        # Descargar datos
        df = nfl.load_player_stats([season])
        df_pl = pl.DataFrame(df)
    except Exception as e:
        print(f"❌ Error al descargar datos de la temporada{season}: {e}")
        return  # Sale de la season en caso de un error.
    # Guardar archivo
    today = date.today().strftime("%Y%m%d")
    file_name = f"player_stats_{season}_{today}.parquet"
    file_path = DATA_DIR / file_name
        
    try:
        df_pl.write_parquet(file_path)
        print(f"Datos actualizados guardados en: {file_path} | Registros: {len(df_pl)}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")

# -----------------------------
# Permitir ejecución desde terminal
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descargar estadísticas de jugadores de la NFL")
    
    # CAMBIO 4: Default en argparse usa el año actual (dinámico)
    current_year = datetime.date.today().year
    parser.add_argument(
        "--season", 
        type=int, 
        default=current_year, # Usamos el año actual como default
        help=f"Temporada a descargar (default: {current_year})"
    )
    args = parser.parse_args()

    download_weekly_data(season=args.season)
