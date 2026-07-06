import hashlib
import json
import os

import pandas as pd

try:
    from IPython.display import display
except ImportError:
    display = print  # fallback when run outside Jupyter
import pandas_gbq
from google.oauth2 import service_account

creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if not creds_json:
    raise ValueError(
        "GOOGLE_APPLICATION_CREDENTIALS env var not set. "
        "Load .env.localrunner or export it with your service account JSON."
    )
service_account_bq = json.loads(creds_json)
credentials = service_account.Credentials.from_service_account_info(service_account_bq)

# Project ID is read from the service account credentials.
PROJECT_ID = service_account_bq.get("project_id")

CACHE_DIR = os.path.join(os.getcwd(), "bq_cache")
HASH_MAP_PATH = os.path.join(CACHE_DIR, "hash_map.txt")


def _get_query_hash(query: str) -> str:
    return hashlib.sha256(query.encode()).hexdigest()


def _load_hash_map() -> dict:
    if os.path.isfile(HASH_MAP_PATH):
        with open(HASH_MAP_PATH) as f:
            return json.load(f)
    return {}


def _save_hash_map(mapping: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(HASH_MAP_PATH, "w") as f:
        json.dump(mapping, f, indent=2)


def run_bq_query_string(query: str) -> pd.DataFrame:
    """
    Run a SQL string directly against BigQuery and return the results as a DataFrame.

    Handy for small, ad-hoc queries you'd rather read inline in the notebook than
    keep in a separate .sql file. Unlike run_bq_query, results are NOT cached.

    Params:
    -------
    query: str
        The SQL query to run.

    Returns:
    --------
    pandas.DataFrame
        The results of the query as a pandas DataFrame.
    """
    return pandas_gbq.read_gbq(
        query,
        project_id=PROJECT_ID,
        credentials=credentials,
        progress_bar_type="tqdm",
    )


def run_bq_query(filepath: str, full_refresh: bool = False, show_head: bool = True):
    """
    Run a BigQuery query from a file and return the results as a pandas DataFrame.
    Caches results in local CSV. When full_refresh=False, returns cached data
    if the query hash hasn't changed since the last run.

    Params:
    -------
    filepath: str
        Path to the file containing the SQL query. The file name (without extension)
        is used as the query name for caching.
    full_refresh: bool
        If True, always runs the query and updates the cache. If False,
        returns cached CSV when the query hash is unchanged.
    show_head: bool
        If True, displays df.head() after loading (Jupyter-rich or print fallback). Defaults to True.

    Returns:
    --------
    pandas.DataFrame
        The results of the query as a pandas DataFrame.
    """
    with open(filepath) as f:
        query = f.read()
    name = os.path.splitext(os.path.basename(filepath))[0]
    csv_path = os.path.join(CACHE_DIR, f"{name}.csv")
    current_hash = _get_query_hash(query)

    if not full_refresh:
        mapping = _load_hash_map()
        if name in mapping and mapping[name] == current_hash and os.path.isfile(csv_path):
            df = pd.read_csv(csv_path)
            if show_head:
                display(df.head())
                display(f"{df.shape[0]} rows, {df.shape[1]} columns")
            return df

    df = run_bq_query_string(query)
    os.makedirs(CACHE_DIR, exist_ok=True)
    df.to_csv(csv_path, index=False)

    mapping = _load_hash_map()
    mapping[name] = current_hash
    _save_hash_map(mapping)

    if show_head:
        display(df.head())
        display(f"{df.shape[0]} rows, {df.shape[1]} columns")
    return df
