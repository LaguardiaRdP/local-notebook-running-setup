# Local Notebook Running Setup

A minimal template for running BigQuery queries locally inside a Jupyter notebook, with automatic CSV caching so you don't re-query BigQuery on every run.

---

## Folder Structure

```
notebooks/                      # Your working folder (the parent)
├── .env.localrunner            # Your credentials — SHARED by every cloned copy below
├── local-notebook-running-setup/
│   ├── example_notebook.ipynb  # Start here: run a query, explore results
│   ├── bigquery_adapter.py     # Query runner with local CSV caching (no edits needed)
│   ├── env_loader.py           # Loads ../.env.localrunner into the environment (no edits needed)
│   ├── requirements.txt        # Python dependencies
│   ├── queries/
│   │   └── example_query.sql   # Drop any .sql file here and point the notebook at it
│   └── bq_cache/
│       └── hash_map.txt        # Tracks query hashes for cache invalidation (auto-managed)
└── local-notebook-running-setup-2/   # Clone as many copies as you like — all share ../.env.localrunner
    └── ...
```

The notebook loads `.env.localrunner` from the **parent folder** (one level up from the repo), so you only keep one credentials file and every clone reuses it.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. **Add your credentials** - ⚠️ IMPORTANT ⚠️

Place your `.env.localrunner` file in the **parent folder** — i.e. one level above this repo, right alongside the `local-notebook-running-setup` folder (your notebooks folder). The notebook loads it automatically from there, so every copy you clone into that folder shares the same credentials file.

### 3. Write your query

Edit `queries/example_query.sql` (or add a new `.sql` file) with the query you want to run.

### 4. Open the notebook

Open `example_notebook.ipynb` in Jupyter and run the cells top to bottom.

---

## How caching works

`bigquery_adapter.py` saves query results as CSVs in `bq_cache/`. On the next run, if the SQL file hasn't changed, it loads from the CSV instead of hitting BigQuery again. To force a fresh pull:

```python
df = run_bq_query("queries/example_query.sql", full_refresh=True)
```

Delete the `bq_cache/` folder at any time to clear all cached results.

---

## Notes

- `.env.localrunner` lives outside the repo (in the parent folder), so it's never tracked by git. It's also listed in `.gitignore` as a safety net.
- Add as many `.sql` files as you like to `queries/` and call each one with `run_bq_query`.
- For small, one-off queries you'd rather keep inline, use `run_bq_query_string` instead of creating a `.sql` file:

  ```python
  from bigquery_adapter import run_bq_query_string

  df = run_bq_query_string("SELECT 1 AS n")
  ```

  Inline string queries are **not cached** — use file-based `run_bq_query` for anything expensive you'll re-run.
