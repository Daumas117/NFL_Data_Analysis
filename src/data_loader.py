# src/data_loader.py

import nflreadpy as nfl
import polars as pl
from pathlib import Path
import argparse

# Carpeta principal para datos crudos
DATA_DIR = Path(__file__).resolve().parents[1] / "data/raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def download_weekly_data(seasons=[2024], weeks=None):
    """
    Descarga datos semanales de la NFL y los guarda en formato Parquet.
    
    Args:
        seasons (list[int]): Lista de temporadas a descargar.
        weeks (list[int], optional): Lista de semanas a descargar. Si es None, descarga todas.
    """
    for season in seasons:
        print(f"Descargando datos de la temporada {season}...")
        
        try:
            # Descargar datos
            df = nfl.load_weekly(years=[season], weeks=weeks)
            df_pl = pl.DataFrame(df)
        except Exception as e:
            print(f"❌ Error al descargar datos: {e}")
            return # Sale de la función si falla la descarga
        # Guardar archivo
        file_name = f"weekly_{season}"
        if weeks:
            weeks_str = "_".join(str(w) for w in weeks)
            file_name += f"_weeks_{weeks_str}"
        file_name += ".parquet"
        
        file_path = DATA_DIR / file_name
        df_pl.write_parquet(file_path)
        print(f"Datos guardados en: {file_path} | Registros: {len(df_pl)}")

# -----------------------------
# Permitir ejecución desde terminal
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descargar datos semanales de NFL")
    parser.add_argument(
        "--seasons",
        type=int,
        nargs="+",
        default=[2024],
        help="Lista de temporadas a descargar, ejemplo: --seasons 2022 2023"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        nargs="+",
        help="Lista de semanas a descargar, ejemplo: --weeks 1 2 3"
    )
    args = parser.parse_args()
    
    download_weekly_data(seasons=args.seasons, weeks=args.weeks)
