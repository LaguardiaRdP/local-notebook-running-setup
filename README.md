# Local Notebook Running Setup

A minimal template for running BigQuery queries locally inside a Jupyter notebook, with automatic CSV caching so you don't re-query BigQuery on every run.

---

## Folder Structure

```
local-notebook-running-setup/
├── example_notebook.ipynb  # Start here: run a query, explore results
├── bigquery_adapter.py     # Query runner with local CSV caching (no edits needed)
├── requirements.txt        # Python dependencies
├── .env.localrunner        # Your credentials — copy it here from your local machine
├── queries/
│   └── example_query.sql   # Drop any .sql file here and point the notebook at it
└── bq_cache/
    └── hash_map.txt        # Tracks query hashes for cache invalidation (auto-managed)
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your credentials

Copy your `.env.localrunner` file into the root of this folder. The notebook loads it automatically.

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

- `.env.localrunner` is excluded from git via `.gitignore` — don't commit it.
- Add as many `.sql` files as you like to `queries/` and call each one with `run_bq_query`.
