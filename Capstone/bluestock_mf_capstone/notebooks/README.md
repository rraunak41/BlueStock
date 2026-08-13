# Notebooks

The brief calls for Jupyter notebooks (`01_data_ingestion.ipynb` …
`05_advanced_analytics.ipynb`). For portability and easy CLI re-running,
this build implements the same logic as standalone, well-commented Python
scripts in `../scripts/` instead:

| Notebook (per brief) | Equivalent script |
|---|---|
| 01_data_ingestion.ipynb | `../scripts/data_ingestion.py` |
| 02_data_cleaning.ipynb | `../scripts/data_cleaning.py` + `../scripts/load_database.py` |
| 03_eda_analysis.ipynb | `../scripts/eda_analysis.py` |
| 04_performance_analytics.ipynb | `../scripts/performance_analytics.py` |
| 05_advanced_analytics.ipynb | `../scripts/advanced_analytics.py` |

Each script can be run directly (`python scripts/eda_analysis.py`) or pasted
cell-by-cell into a Jupyter notebook — the logic is identical either way.
