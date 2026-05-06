"""
data_loader.py
Handles loading, parsing, and cleaning the IMDb title.basics.tsv dataset.
"""

from pathlib import Path
import gzip
import shutil
import urllib.request

import pandas as pd

IMDB_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
DEFAULT_DATA_PATH = Path("data/title.basics.tsv")
GZ_DATA_PATH = Path("data/title.basics.tsv.gz")
SAMPLE_DATA_PATH = Path("data/title.basics.tsv")

COLUMNS_TO_KEEP = [
    "tconst",
    "titleType",
    "primaryTitle",
    "originalTitle",
    "startYear",
    "genres",
]


def normalize_title(title: object) -> str:
    """Normalize movie titles so baseline and optimized search use the same key."""
    return str(title).strip().lower()


def download_imdb_dataset() -> None:
    """Download and unzip IMDb title.basics.tsv.gz if the full dataset is missing."""
    DEFAULT_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DEFAULT_DATA_PATH.exists():
        return

    print("Full IMDb dataset not found. Downloading title.basics.tsv.gz...")
    urllib.request.urlretrieve(IMDB_URL, GZ_DATA_PATH)

    print("Unzipping dataset...")
    with gzip.open(GZ_DATA_PATH, "rb") as source, open(DEFAULT_DATA_PATH, "wb") as target:
        shutil.copyfileobj(source, target)

    print("Dataset ready at data/title.basics.tsv")


def get_data_path(prefer_sample: bool = False) -> Path:
    """
    Return the best available dataset path.
    For the final benchmark, use the full title.basics.tsv file.
    A small sample file is included only so the repo can run without downloading 1GB.
    """
    if prefer_sample and SAMPLE_DATA_PATH.exists():
        return SAMPLE_DATA_PATH

    if DEFAULT_DATA_PATH.exists():
        return DEFAULT_DATA_PATH

    if SAMPLE_DATA_PATH.exists():
        print("WARNING: Full dataset not found. Using sample data only.")
        print("For final results, download title.basics.tsv and place it in data/title.basics.tsv")
        return SAMPLE_DATA_PATH

    download_imdb_dataset()
    return DEFAULT_DATA_PATH


def load_data(file_path: str | Path | None = None, nrows: int | None = None) -> pd.DataFrame:
    """
    Load IMDb data as a cleaned pandas DataFrame.

    Args:
        file_path: Optional path to a TSV dataset.
        nrows: Optional number of rows to load for benchmarking different input sizes.

    Returns:
        Cleaned DataFrame containing only the useful columns.
    """
    path = Path(file_path) if file_path else get_data_path()

    df = pd.read_csv(
        path,
        sep="\t",
        usecols=COLUMNS_TO_KEEP,
        low_memory=False,
        nrows=nrows,
        na_values="\\N",
    )

    df = df.dropna(subset=["primaryTitle"])
    df["normalizedTitle"] = df["primaryTitle"].apply(normalize_title)

    return df.reset_index(drop=True)


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame rows into dictionaries for pure algorithm functions."""
    return df.to_dict("records")
